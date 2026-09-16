# 命名方案本体与词表

来源：《WorkBuddy 工作区命名现状分析与前缀分类方案 v1》（2026-09-17）

**命名模板**

```
<领域>-<用途>-<主题>-<版本/状态>.<扩展名>
```

**核心依据**：按"交付对象与合规链"划分领域，**不按技术手段**。脚本跟随它的服务对象，不跟随技术栈。

---

## 词表（校验器的事实来源）

`check_name.py` 直接解析以下三个块。**扩充前缀只改本文件，无需改代码。**

### 领域前缀

```vocab-domain
med
res
ai
grant
pat
biz
ops
```

| 前缀 | 含义 | 适用范围 |
|---|---|---|
| `med-` | 临床医学与神经科学 | 干细胞管线、脑卒中/ALS、影像处理、患者数据集、临床方案 |
| `res-` | 科研方法与文献产出 | 综述、Meta、文献检索与验证、实验设计、绘图方法 |
| `ai-` | AI/大模型工具链与技能资产 | 技能开发发布、模型能力调研、dsh、GitHub 同步、自动化编排 |
| `grant-` | 基金与标书申报 | 齐鲁专项、国自然、尖兵计划、申报书与附件 |
| `pat-` | 专利与知识产权 | 交底书、权利要求、检索查新、法律状态核查 |
| `biz-` | 商业与投资决策 | 商业计划书、科学尽调、投资测算、房产投资调研 |
| `ops-` | 个人事务与运行维护 | 行程、通话转录、时间管理、环境排障、自动化配置 |

### 用途中缀

```vocab-kind
lit
rev
dsgn
data
fig
doc
sld
tool
raw
```

| 中缀 | 含义 | 典型产物 |
|---|---|---|
| `-lit-` | 文献检索与证据收集 | 检索清单、参考文献验证、ClinicalTrials 摘录 |
| `-rev-` | 综述与深度调研 | 调研报告、叙事综述、尽调结论 |
| `-dsgn-` | 方案与设计 | 技术路线、实验设计、标书路线、流程图 |
| `-data-` | 数据与数据集 | 影像数据、队列追踪表、结构化 JSON |
| `-fig-` | 图与视觉 | 机制示意图、路线图、封面、信息图 |
| `-doc-` | 正式成稿 | DOCX 终稿、通知书、合同、操作指引 |
| `-sld-` | 演示与汇报 | PPT、汇报页、验收汇报 |
| `-tool-` | 脚本与工具 | `.py` / `.mjs` / `.ps1` / `.bat` |
| `-raw-` | 原始素材 | 通话录音、扫描件、来源网页、原始响应 |

### 状态后缀

```vocab-status
wip
pre
final
arch
```

| 状态 | 含义 |
|---|---|
| `-wip` | 草稿（缺省视为 wip） |
| `-pre` | 待审 |
| `-final` | 定稿 |
| `-arch` | 归档 |

### 不可套用命名模板的保留项

```vocab-reserved
README.md
README_ZH.md
SKILL.md
LICENSE
LICENSE.md
CHANGELOG.md
CITATION.cff
CITATION_AND_ATTRIBUTION.md
TRADEMARK.md
SOUL.md
IDENTITY.md
USER.md
MEMORY.md
BOOTSTRAP.md
META.md
ALIAS.md
AGENTS.md
CLAUDE.md
Claw
index.html
index.js
main.py
setup.py
conftest.py
__init__.py
requirements.txt
package.json
package-lock.json
pnpm-lock.yaml
tsconfig.json
pyproject.toml
Makefile
Dockerfile
docker-compose.yml
manifest.json
```

### 上游/第三方技能前缀（非自建，跳过 N7）

```vocab-notselfbuilt
lc-
sci-
ms-
```

---

## 边界易混点仲裁规则

| 情形 | 归属 | 规则 |
|---|---|---|
| 房产调研（自住兼投资） | `biz-` | 涉金额决策与外部交易 → `biz-` |
| 纯出行、生活事务 | `ops-` | 仅涉个人安排 → `ops-` |
| 影像处理脚本 | `med-` | 脚本跟随服务对象，不跟随技术栈 |
| 技能开发 vs 科研方法 | `ai-` vs `res-` | 产出是工具 → `ai-`；产出是结论 → `res-` |
| PDF OCR | 随用途变 | 服务于医学名词提取 → `res-`；服务于合同解析 → `ops-` |

---

## 目录层方案

| 对象 | 处置 | 命名 |
|---|---|---|
| 新增活跃项目工作区 | 语义化命名 | `<领域>-<主题>-<YYYYMMDD>`，例 `med-761tel-ia-20260814` |
| 系统时间戳工作区 | **不改名**，补元数据 | 放 `META.md`，首行写 `主题: <一句话>` |
| 历史目录（2026-04~07） | 维持原状 | 不迁移、不改名 |
| 角色子目录 | 收敛为 5 个 | `out/` `src/` `raw/` `ref/` `tmp/` |

**角色目录映射**：`outputs`／`results`／`deliverables`／`work`／`docs` → 全部收敛为 `out/`；`test_pdf`／`covers_sample`／`generated-images` → `tmp/` 或 `ref/`。

---

## 技能库命名治理

**关键改动：把前缀的划分基准从"内容"改为"来源"。**

| 前缀 | 定义 | 读写策略 |
|---|---|---|
| `lc-*` | LabClaw 上游同步 | 只读，冻结不再新增；上游更新时整族覆盖 |
| `sci-*` | scientific-agent-skills 上游同步 | 只读，同上 |
| `ms-*` | medsci 上游族 | 只读 |
| `*_diy` | **自建技能** | 可自由改，最高优先级资产 |
| 无前缀 | 第三方独立技能（`tavily`、`pathclaw` 等） | 保持原名 |

配套动作：建 `ALIAS.md` 把 40 余组跨族重名建立映射（如 `citation-management` → 首选 `ms-` 实现），**不删除任何上游技能目录**（会破坏升级路径）。

---

## 新旧对照（真实文件 → 规范命名）

| 现存文件 | 规范命名 |
|---|---|
| `齐鲁制药专项_干细胞神经疾病结合点分析.md` | `grant-qilu-2026-94-rev-final.md` |
| `ChiCTR干细胞治疗脑卒中注册项目清单.md` | `res-chictr-stroke-lit-v1.md` |
| `dsh插件装机量调研_速览版.md` | `ai-dsh-plugin-survey-rev-v1.md` |
| `北京十三陵山居疗愈_商业计划书.md` | `biz-shisanling-retreat-doc-v1.md` |
| `通话转录_交通事故维修纠纷.docx` | `ops-call-transcript-doc-final.docx` |
| `compare_char3.py` | `compare-char-tool-v3.py` |
| `upload_github_upload3.py` | `upload-github-tool-v3.py` |
| `MSC-NSC技术路线图.html` | `med-msc-nsc-dsgn-fig-v1.html` |
| `_dellog.txt`、`_verify.docx` | 移入 `tmp/`，**不改名** |

---

## 建议清单（按优先级）

| # | 建议 | 优先级 | 理由 |
|---|---|---|---|
| 1 | 冻结"裸版号"，迭代产物改 `-vN` | 高 | 唯一会引发执行事故的问题——`upload_*.py` 通配匹配会把旧版当有效脚本一并处理 |
| 2 | 临时件一律进 `tmp/` | 高 | 11 个 `test_*.mjs`、`_dellog.txt` 与终稿同层，有拿错文件的实际风险 |
| 3 | 新建工作区用 `<领域>-<主题>-<YYYYMMDD>` | 高 | 解决 97% 目录无主题锚点，新建即生效、零迁移 |
| 4 | 时间戳目录补 `META.md` | 高 | 不动目录名（规避索引断链）即可恢复可检索性 |
| 5 | md/docx 同名成对写成硬规范 | 中 | 已有 12 组成对实践，属固化既有正确做法，成本为零 |
| 6 | 角色目录 5 词收敛制 | 中 | 消除四词一义的检索噪音 |
| 7 | 同内容禁中英双份，弃用件加 `-arch` | 中 | 避免版本分叉、无法判定以谁为准 |
| 8 | 技能库前缀改按"来源"定义 | 中 | 40 余组重名的根因是前缀按内容划分 |
| 9 | 日期后缀统一 8 位 `-YYYYMMDD` 且仅限时间序列 | 低 | 现有 3 种格式解析规则不一致 |
| 10 | **明确不做**：历史目录批量迁移、`lc-`/`sci-` 技能族合并 | — | 代价远高于冗余本身 |

### 落地节奏

| 阶段 | 动作 |
|---|---|
| 立即 | 建议 1、2、3、5、9 |
| 2 周内 | 建议 4、6、8 |
| 3 个月内 | 建议 7、10 |
| 不做 | 历史目录改名（146 个维持原状） |
