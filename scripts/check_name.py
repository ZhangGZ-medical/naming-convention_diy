#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""naming-convention_diy 命名校验器

规范：三段式 <领域>-<用途>-<主题>-<版本/状态>.<ext>
     + 自建技能目录名以 _diy 结尾（本规范中唯一涉及 _diy 的规则）

词表来自 references/scheme.md 的 vocab-* 代码块。

安全红线：本脚本只报告与给出建议名，不含任何改名或删除 API，绝不修改文件系统。
"""
import argparse
import json
import re
import sys
from pathlib import Path

COMPOUND_EXT = ('.tar.gz', '.tar.bz2', '.d.ts', '.d.mts', '.d.cts', '.min.js',
                '.min.css', '.spec.ts')
NL = '\n'

DOMAIN_DEFAULT = ('med', 'res', 'ai', 'grant', 'pat', 'biz', 'ops')
KIND_DEFAULT = ('lit', 'rev', 'dsgn', 'data', 'fig', 'doc', 'sld', 'tool', 'raw')
STATUS_DEFAULT = ('wip', 'pre', 'final', 'arch')
NOTSELF_DEFAULT = ('lc-', 'sci-', 'ms-')
RESERVED_DEFAULT = (
    'README.md', 'README_ZH.md', 'SKILL.md', 'LICENSE', 'LICENSE.md', 'CHANGELOG.md',
    'CITATION.cff', 'CITATION_AND_ATTRIBUTION.md', 'TRADEMARK.md', 'SOUL.md',
    'IDENTITY.md', 'USER.md', 'MEMORY.md', 'BOOTSTRAP.md', 'META.md', 'ALIAS.md',
    'AGENTS.md', 'CLAUDE.md', 'Claw', 'index.html', 'index.js', 'main.py', 'setup.py',
    'conftest.py', '__init__.py', 'requirements.txt', 'package.json',
    'package-lock.json', 'pnpm-lock.yaml', 'tsconfig.json', 'pyproject.toml',
    'Makefile', 'Dockerfile', 'docker-compose.yml', 'manifest.json',
    'fields.yaml', 'outline.yaml',
)
SKIP_DIRS = {
    'node_modules', 'site-packages', 'dist', 'build', '.venv', 'venv', '__pycache__',
    '.cache', '.git', '.next', '.nuxt', 'target',
}

# 领域推测关键词——仅用于生成"推测建议"，不作为合规判定依据
DOMAIN_HINTS = (
    ('med', ('干细胞', '卒中', '脑梗', 'als', 'nsc', 'msc', 'inpc', '761tel', '影像',
             'pet', 'mri', 'dicom', '患者', '临床', '神经', '颅', '外泌体', '偏头痛',
             '脑出血', 'bci', 'nmpa', '脱敏', '解剖', 'hace')),
    ('res', ('综述', '文献', '检索', 'pubmed', 'chictr', 'clinicaltrials', 'meta',
             '参考文献', '引文', '绘图', '查重', '审稿', 'peer', 'reporting', 'pyramid',
             '科研', '实验设计', '样本量', 'stem_cell')),
    ('ai', ('技能', 'skill', 'dsh', '插件', 'fable', '工作流', 'workflow', 'github',
            'deepseek', 'prompt', '插画', 'agent', '模型', 'mcp', '自动化', 'ocr')),
    ('grant', ('标书', '申请', '专项', '国自然', 'nsfc', '齐鲁', '尖兵', '验收', '课题')),
    ('pat', ('专利', '权利要求', '交底', 'patent', '查新', '知识产权')),
    ('biz', ('房价', '购房', '楼盘', '商业计划', '投资', '尽调', '房市', '住宅',
             '网约车', '疗愈', '收入', '市场')),
    ('ops', ('行程', '旅行', '通话', '转录', '时间管理', '清单', '排障', '安装', '合同',
             '会议', '通知', '退团', '录音')),
)


def load_vocab(md_path):
    v = {'domain': set(DOMAIN_DEFAULT), 'kind': set(KIND_DEFAULT),
         'status': set(STATUS_DEFAULT), 'reserved': set(RESERVED_DEFAULT),
         'notself': set(NOTSELF_DEFAULT)}
    mapping = {'vocab-domain': 'domain', 'vocab-kind': 'kind', 'vocab-status': 'status',
               'vocab-reserved': 'reserved', 'vocab-notselfbuilt': 'notself'}
    if md_path and Path(md_path).is_file():
        text = Path(md_path).read_text(encoding='utf-8', errors='replace')
        for tag, block in re.findall(r'```(vocab-[a-z]+)\s*\n(.*?)```', text, re.S):
            items = {ln.strip() for ln in block.splitlines() if ln.strip()}
            if tag in mapping and items:
                v[mapping[tag]] = items
    return v


def split_name(name, is_dir=False):
    if is_dir:
        return name, ''
    low = name.lower()
    for c in COMPOUND_EXT:
        if low.endswith(c):
            return name[:-len(c)], name[-len(c):]
    i = name.rfind('.')
    if i > 0:
        return name[:i], name[i:]
    return name, ''


def guess_domain(text):
    low = text.lower()
    for dom, keys in DOMAIN_HINTS:
        for k in keys:
            if k in low:
                return dom
    return ''


def mech_fix(stem):
    """机械修复：空格转 -、裸版号转 -vN、折叠重复分隔符、剥尾部分隔符。"""
    s = re.sub(r'\s+', '-', stem.strip())
    s = re.sub(r'(?<![-_vV])([A-Za-z_])(\d+)$',
               lambda m: '%s-v%s' % (m.group(1), m.group(2)), s)
    s = re.sub(r'-{2,}', '-', s)
    return s.strip('-')


def suggest(stem, vocab, force_diy=False):
    """返回 (建议名, 是否含领域推测)。

    只做两件事：机械修复 + 补推测领域前缀。不自动插入用途/状态中缀——
    那需要语义判断，工具不应伪造精确度。
    force_diy=True 时确保以 _diy 结尾（用于自建技能）。
    """
    tail = ''
    fixed = stem
    if re.search(r'[-_]diy$', fixed, re.I):
        tail = '_diy'
        fixed = re.sub(r'[-_]diy$', '', fixed, flags=re.I)
    fixed = mech_fix(fixed)
    if force_diy:
        tail = '_diy'
    segs = [s for s in fixed.split('-') if s]
    if segs and segs[0].lower() in vocab['domain']:
        return fixed + tail, False
    dom = guess_domain(fixed)
    if dom:
        return '%s-%s%s' % (dom, fixed, tail), True
    return fixed + tail, False


def check(name, vocab, is_dir=False, is_self_skill=False):
    """返回 (issues, note)。issues 元素为 (规则号, 说明, 'block'|'advise'|'info')

    两条独立的规则集：
      自建技能名 → 只受 N6/N7/N8/N9 约束（方案 §4.6 对技能名的规定独立于命名模板）
      文件 / 普通目录 → 受三段式模板 N1/N2/N3/N5/N6 约束
    """
    issues, note = [], ''
    if name in vocab['reserved'] or name.startswith('.'):
        return issues, '豁免：生态保留名 / 隐藏项'
    if is_dir and name in SKIP_DIRS:
        return issues, '豁免：依赖或构建目录'
    stem, ext = split_name(name, is_dir)
    if name.startswith('_') and not is_self_skill:
        note = '临时件：建议移入 tmp/，不需要改名'
    if ' ' in stem:
        issues.append(('N6', '名称含空格，段间应改用 - 连接', 'block'))
    if is_self_skill:
        if stem.endswith('-diy'):
            issues.append(('N8', '自建标记用了 -diy，建议统一为 _diy', 'advise'))
        elif stem.endswith('_diy'):
            core = stem[:-4]
            if re.search(r'[-_]diy', core, re.I):
                issues.append(('N9', '_diy 出现在名称中段，只能作为结尾标记', 'block'))
        else:
            issues.append(('N7', '自建技能目录名未以 _diy 结尾', 'block'))
        return issues, note
    segs = [s for s in stem.split('-') if s]
    if not (segs and segs[0].lower() in vocab['domain']):
        head = segs[0] if segs else stem
        issues.append(('N1', '缺少领域前缀（首个字段 "%s" 不在词表内）' % head, 'block'))
    elif not any(s.lower() in vocab['kind'] for s in segs[1:]):
        issues.append(('N2', '未含用途中缀（可选，推荐补上）', 'advise'))
    if re.search(r'(?<![-_vV])[A-Za-z_]\d+$', stem):
        issues.append(('N3', '裸版号，须改为 -vN 形式', 'block'))
    if re.search(r'\d{4}[-_.]\d{1,2}[-_.]\d{1,2}', stem):
        issues.append(('N5', '非紧凑日期形式，时间序列应用 -YYYYMMDD', 'advise'))
    return issues, note


def is_self_built_skill(skill_dir, vocab):
    name = skill_dir.name
    for p in vocab['notself']:
        if name.startswith(p):
            return False, '非自建：上游族 %s' % p
    if name.endswith(('_diy', '-diy')):
        return True, '自建：名称已带 _diy / -diy 标记'
    sm = skill_dir / 'SKILL.md'
    if sm.is_file():
        head = sm.read_text(encoding='utf-8', errors='replace')[:1500]
        if re.search(r'^\s*agent_created\s*:\s*true\s*$', head, re.M):
            return True, '自建：SKILL.md 声明 agent_created: true'
    return False, '非自建：无 agent_created 标记'


def walk_scan(root, recursive=True):
    r = Path(root)
    if not r.is_dir():
        return
    yield r, True
    if not recursive:
        for p in sorted(r.iterdir()):
            yield p, p.is_dir()
        return
    for p in sorted(r.rglob('*')):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p, p.is_dir()


def main():
    ap = argparse.ArgumentParser(
        description='naming-convention_diy 命名校验器（只报告，不改名）')
    ap.add_argument('--name', default=None, help='校验单个名称')
    ap.add_argument('--as-skill', action='store_true',
                    help='配合 --name：按"自建技能目录名"校验（启用 N7/N8/N9）')
    ap.add_argument('--scan', default=None, help='扫描目录，报告存量偏离')
    ap.add_argument('--skills-root', default=None, help='审计技能库的自建标记')
    ap.add_argument('--scheme', default=None, help='scheme.md 路径')
    ap.add_argument('--out', default=None,
                    help='报告写入文件（UTF-8）；Windows 上勿用 > 重定向')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--no-recursive', action='store_true')
    args = ap.parse_args()

    if args.out:
        sys.stdout = open(args.out, 'w', encoding='utf-8')

    here = Path(__file__).resolve().parent
    md = args.scheme
    if not md:
        cand = here.parent / 'references' / 'scheme.md'
        md = str(cand) if cand.is_file() else None
    vocab = load_vocab(md)

    if not (args.name or args.scan or args.skills_root):
        ap.error('须提供 --name、--scan 或 --skills-root 之一')

    rows = []
    stats = {'total': 0, 'ok': 0, 'block': 0, 'advise': 0, 'exempt': 0,
             'selfbuilt': 0, 'marked': 0, 'variant': 0, 'unmarked': 0}

    def record(path_str, iss, sug, guessed, note=''):
        if sug and Path(sug).name == Path(path_str).name:
            sug = ''  # 建议名与原名为同名，属无变化，不输出以免误导
        if any(t == 'block' for _, _, t in iss):
            stats['block'] += 1
        if any(t == 'advise' for _, _, t in iss):
            stats['advise'] += 1
        if not iss:
            stats['ok'] += 1
        if iss:
            rows.append({'path': path_str,
                         'issues': [{'rule': r, 'msg': m, 'type': t} for r, m, t in iss],
                         'suggest': sug, 'guessed': guessed, 'note': note})

    if args.name:
        nm = args.name
        ext = split_name(nm)[1]
        is_dir = not ext
        iss, note = check(nm, vocab, is_dir, args.as_skill)
        stats['total'] = 1
        sug, guessed = ('', False)
        if iss:
            s, guessed = suggest(split_name(nm, is_dir)[0], vocab,
                                 force_diy=args.as_skill)
            sug = s + split_name(nm, is_dir)[1]
        record(nm, iss, sug, guessed, note)

    elif args.scan:
        for p, is_dir in walk_scan(args.scan, not args.no_recursive):
            stats['total'] += 1
            looks_self = is_dir and p.name.endswith(('_diy', '-diy'))
            iss, note = check(p.name, vocab, is_dir, looks_self)
            if note.startswith('豁免'):
                stats['exempt'] += 1
                continue
            sug, guessed = ('', False)
            if iss:
                s, guessed = suggest(split_name(p.name, is_dir)[0], vocab,
                                     force_diy=looks_self)
                sug = s + split_name(p.name, is_dir)[1]
            record(str(p), iss, sug, guessed, note)

    elif args.skills_root:
        root = Path(args.skills_root)
        for d in sorted(x for x in root.iterdir() if x.is_dir()):
            stats['total'] += 1
            sb, why = is_self_built_skill(d, vocab)
            if not sb:
                stats['exempt'] += 1
                continue
            stats['selfbuilt'] += 1
            if d.name.endswith('_diy'):
                stats['marked'] += 1
            elif d.name.endswith('-diy'):
                stats['variant'] += 1
            else:
                stats['unmarked'] += 1
            iss, _ = check(d.name, vocab, True, True)
            sug, guessed = ('', False)
            if iss:
                sug, guessed = suggest(d.name, vocab, force_diy=True)
            record(str(d), iss, sug, guessed, why)

    if args.json:
        print(json.dumps({'stats': stats, 'scheme': md, 'rows': rows},
                         ensure_ascii=False, indent=2))
    else:
        print('naming-convention_diy 命名校验报告')
        print('规范：<领域>-<用途>-<主题>-<版本/状态>　|　自建技能目录名以 _diy 结尾')
        print('词表来源：%s' % md)
        print('-' * 74)
        if rows:
            for r in rows:
                tag = 'P1 偏离' if any(i['type'] == 'block' for i in r['issues']) \
                    else 'P2 建议'
                print('[%s] %s' % (tag, r['path']))
                if r['note']:
                    print('        · %s' % r['note'])
                for i in r['issues']:
                    lv = '阻断' if i['type'] == 'block' else '建议'
                    print('        %s %s（%s级）' % (i['rule'], i['msg'], lv))
                if r['suggest']:
                    mark = '（含领域推测，需人工确认）' if r['guessed'] else ''
                    print('        → %s %s' % (Path(r['suggest']).name, mark))
            print('')
        else:
            print('无偏离。')
        print('-' * 74)
        if args.skills_root:
            print('技能 {total} ｜ 自建 {selfbuilt} ｜ 已标记 _diy {marked} ｜ '
                  '变体 -diy {variant} ｜ 缺标记 {unmarked} ｜ 非自建 {exempt}'
                  .format(**stats))
        else:
            print('总计 {total} ｜ 合规 {ok} ｜ 阻断级 {block} ｜ 建议级 {advise} ｜ '
                  '豁免 {exempt}'.format(**stats))

    return 1 if stats['block'] else 0


if __name__ == '__main__':
    sys.exit(main())
