# Good Skills — 编码智能体技能合集

面向多平台编码智能体（Claude Code、Codex CLI、OpenCode、Cursor）的实用技能合集。每个技能是自包含的工作流，通过斜杠命令调用。

## 已有技能

### 1. research-landscape — 技术领域全景观测

**一句话**：扫描任意技术领域的最新进展，产出一份结构化中文 Markdown 报告。

**产出物**：`research-landscape-report-<话题>-<日期>.md`，包含 7 大板块 + 趋势点评。

**参数**：

| 参数 | 含义 | 默认值 | 示例 |
|------|------|--------|------|
| `<话题>`（位置参数） | **必填**。要扫描的技术领域，中文英文均可，直接写在命令后面 | 无（不传则报错） | `可观测`、`AI agent evaluation`、`微服务治理` |
| `--since YYYY-MM-DD` | 只采集该日期之后的内容 | 今天往前推 30 天 | `--since 2026-05-01` |
| `--deep` | 深度模式：每信源 5 条结果含完整摘要 | 广度模式：每信源 15 条结果但摘要更短 | `--deep` |

**7 大板块**（从"可看可不看"到"必须关注"）：
1. 行业周刊精选（TLDR AI、Latent Space、The Batch、RadarAI）
2. 国内信源（InfoQ、量子位、AI前线、知乎、即刻）
3. 学术论文（arXiv、Semantic Scholar、Twitter/X 学术号）
4. 标准&开源社区（按话题动态适配）
5. 大厂工程博客（Azure、Google、AWS、Anthropic、OpenAI、Datadog 等）
6. 开源工具动态（按话题动态适配）

**适用场景**：想知道某技术领域最近有什么新东西、新工具、新论文；定期追踪某领域动态。

**前置条件**：
```bash
pip install requests python-dateutil
```
可选：设置 `GITHUB_TOKEN` 和 `SEMANTIC_SCHOLAR_API_KEY` 环境变量提升 API 速率限制。

---

### 2. learn-domain — 技术领域学习指南

**一句话**：为任意技术领域生成结构化学习指南，解决"不知道该学什么、按什么顺序学"的问题。

**产出物**：`learn-domain-guide-<话题>-<日期>.md`，包含领域全景、概念依赖图、分级学习路径、实战项目建议、避坑指南。

**参数**：

| 参数 | 含义 | 默认值 | 示例 |
|------|------|--------|------|
| `<话题>` | **必填**。要学习的技术领域，中文英文均可 | 无（不传则报错） | `可观测`、`Kubernetes`、`Rust` |
| `--level beginner|intermediate` | 学习起点层级 | 根据用户上下文自动判断 | `--level beginner` |
| `--project <项目描述>` | 有具体项目目标时，反向推导必须学的概念 | 无（不限制学习范围） | `--project "写一个CLI工具"` |
| `--lang zh|en` | 输出语言 | `zh`（中文为主 + 英文术语） | `--lang en` |

**5 步工作流**：
1. 领域骨架（概念依赖图 + 术语对照 + 分级学习层级）— Claude 知识生成
2. WebSearch 定向补充资源链接
3. 引用 landscape 报告热点（如存在）
4. 实战项目建议生成
5. 渲染 Markdown 学习指南

**适用场景**：刚接触一个新领域不知道怎么学；有项目目标想反向推导学习路径；想快速了解某领域的概念全貌和依赖关系。

**与 research-landscape 的协作**：如果工作目录中有 landscape 报告，learn-domain 会自动引用其趋势点评作为"当前热点"板块。先跑 landscape 再跑 learn-domain，学习指南会包含最新行业动态。

**前置条件**：无（纯 WebSearch + Claude 知识，不依赖 Python 脚本）

---

### 3. web-to-local-md — 网站文档离线下载

**一句话**：将网站文档专区完整下载到本地 Markdown 文件，含图片和 Mermaid 流程图，支持 Typora 离线阅读。

**产出物**：`--output-dir` 指定目录下的 Markdown 文件 + `images/` 图片目录。输出可直接用 Typora 打开阅读。

**参数**：

| 参数 | 含义 | 默认值 | 示例 |
|------|------|--------|------|
| `<网站URL>`（位置参数） | **必填**。要下载的文档站点 URL，直接写在命令后面，不需要 `--url` 前缀 | 无（不传则报错） | `https://javaguide.cn/ai/` |
| `--github-repo OWNER/REPO` | **推荐必填**。文档的 GitHub 仓库。提供后会从 GitHub 下载源 `.md` 文件（质量远优于 HTML 转换） | 无（缺少则走 HTML 转换策略，质量较低） | `--github-repo Snailclimb/JavaGuide` |
| `--output-dir DIR` | 输出目录 | `./downloaded` | `--output-dir ./downloaded-docs` |
| `--render-mermaid` | 将 Mermaid 代码块渲染为 PNG 图片 | 不渲染（保留 Mermaid 代码块原文） | `--render-mermaid` |

**两种下载策略**：
- **Strategy A（推荐）**：提供 `--github-repo` → 从 GitHub 下载源 `.md` 文件，质量最高
- **Strategy B（降级）**：不提供 `--github-repo` → HTML 转 Markdown，质量较低（可能丢失标题、损坏图片 URL）

**适用场景**：想离线阅读 VuePress/VitePress 文档站；出差/飞行时需要本地技术文档；文档网站访问慢想存本地。

**前置条件**：
```bash
# Python 3 必需
# 可选：渲染 Mermaid 流程图为 PNG
npm install -g @mermaid-js/mermaid-cli
```

---

### 4. evaluate-skill — Skill 质量评估

**一句话**：评估任意 skill 的输出质量，发现结构缺失、内容偏差、降级失败等问题，加速 SKILL.md 的迭代优化。

**产出物**：`evaluate-skill-report-<skill-name>-<日期>.md`，包含结构断言结果、4 维度评分（完整性/准确性/合规性/可用性）、改进建议。批量模式额外产出逐用例评分表和共性问题分析。

**参数**：

| 参数 | 含义 | 默认值 | 示例 |
|------|------|--------|------|
| `<skill-name>`（位置参数） | **必填**。要评估的 skill 名称，直接写在命令后面 | 无（不传则报错） | `research-landscape`、`web-to-local-md` |
| `--input <路径>` | 指定已有输出文件路径（事后评估） | 当前目录自动查找匹配文件 | `--input ./downloaded` |
| `--run <skill参数>` | 先执行目标 skill 再评估其输出（一体化模式） | 不执行，只评估已有输出 | `--run "可观测 --since 2026-05-01"` |
| `--golden <路径>` | 批量评估黄金数据集目录 | 无（单用例模式） | `--golden ./golden/web-to-local-md/` |
| `--regress <参考路径>` | 与参考输出做回归对比 | 不做回归 | `--regress ./reference-report.md` |
| `--verbose` | 输出详细判断依据 | 只输出分数和结论 | `--verbose` |

**三层评估**：
1. **结构断言**（8 项通用检查）：文件存在？非空？Markdown 可解析？无占位符？URL 是文章级？
2. **SKILL.md 合规性**（LLM-as-Judge）：完整性、准确性、合规性、可用性各 1-5 分
3. **回归对比**（可选）：与参考输出对比，分类为改进/退化/不变

**核心定位**：skill 质量改进的**反馈工具**，不是绝对质量裁判。评估帮你发现问题，改 SKILL.md 来修复，再评估验证。

**适用场景**：改了 SKILL.md 后验证输出不退化；新 skill 写完后首次验收；定期检查 skill 输出质量趋势。

**局限**：黑盒评估（看不到中间过程）；LLM-as-Judge 评分 ±1 波动；没有文件输出的 skill 不适用。

**前置条件**：无（纯 Claude 编排，不依赖 Python 评估脚本）

---

## 安装

### Claude Code

```bash
claude plugin install good-skills
```

### Codex CLI

Codex CLI 没有插件系统，通过项目级 `AGENTS.md` 文件提供技能描述。

### OpenCode

详见 [.opencode/INSTALL.md](.opencode/INSTALL.md)。

快速配置 — 添加到 `opencode.json`：
```json
{
  "plugin": ["good-skills@git+https://github.com/Wendymayu/good-skills.git"]
}
```

## 使用示例

```
/good-skills:research-landscape 可观测                     # 可观测性全景观测（默认 30 天）
/good-skills:research-landscape AI agent evaluation        # 评估领域
/good-skills:research-landscape 微服务治理 --since 2026-05-01  # 微服务治理（指定起始日期）
/good-skills:research-landscape safety --deep              # 安全深度扫描（每信源 5 条完整摘要）

/good-skills:learn-domain 可观测                          # 可观测性学习指南（自动判断层级）
/good-skills:learn-domain AI agent --level beginner       # Agent 入门路径
/good-skills:learn-domain Rust --project "写一个CLI工具"   # 反向推导 Rust 学习路径
/good-skills:learn-domain Kubernetes --lang en            # 英文输出

/good-skills:web-to-local-md https://javaguide.cn/ai/ --github-repo Snailclimb/JavaGuide --output-dir ./downloaded --render-mermaid  # 下载 JavaGuide AI 章节

/good-skills:evaluate-skill research-landscape --input ./research-landscape-report-*.md  # 评估已有报告
/good-skills:evaluate-skill web-to-local-md --input ./downloaded                         # 评估下载输出
/good-skills:evaluate-skill research-landscape --run "可观测"                             # 先执行再评估
/good-skills:evaluate-skill web-to-local-md --golden ./golden/web-to-local-md/            # 批量评估
```

### 定期扫描

配合 `/loop` 实现周期性自动扫描：
```
/loop 168h /good-skills:research-landscape <话题> --since $(date -d '7 days ago' +%Y-%m-%d)
```

## 项目结构

```
good-skills/
├── .claude-plugin/plugin.json          ← Claude Code 插件声明
├── .claude-plugin/marketplace.json     ← Marketplace 目录
├── .codex-plugin/plugin.json           ← Codex CLI 兼容
├── .opencode/                          ← OpenCode 兼容
│   ├── INSTALL.md
│   └── plugins/good-skills.js
├── AGENTS.md                           ← Codex CLI / 通用指令层
├── README.md                           ← 项目入口
├── docs/                               ← spec、plan 等开发文档
└── skills/
    ├── research-landscape/
    │   ├── SKILL.md                    ← 技能定义（编排层）
    │   ├── references/
    │   │   ├── search-strategies.md    ← 搜索策略模板
    │   │   ├── source-guide.md         ← API 端点、仓库、速率限制
    │   │   └── report-template.md      ← 报告 Markdown 骨架
    │   └── scripts/
    │       ├── search_arxiv.py
    │       ├── search_semantic_scholar.py
    │       ├── fetch_otel_updates.py
    │       ├── fetch_openinference_updates.py
    │       ├── fetch_tool_releases.py
    │       └── generate_report.py
    ├── learn-domain/
    │   ├── SKILL.md                    ← 技能定义（编排层）
    │   └── references/
    │       └── report-template.md      ← 学习指南 Markdown 骨架
    ├── evaluate-skill/
    │   ├── SKILL.md                    ← 技能定义（编排层）
    │   └── references/
    │       ├── structural-checks.md    ← 通用结构断言清单
    │       ├── scoring-rubric.md       ← 4 维度评分标准
    │       └── report-template.md      ← 评估报告模板
    └── web-to-local-md/
        ├── SKILL.md                    ← 技能定义（编排层）
        ├── references/
        │   └── common-issues.md        ← 常见问题与解决方案
        └── scripts/
            └── web_to_local_md.py      ← 核心下载/转换脚本
```

## 新增技能

1. 在 `skills/<技能名>/SKILL.md` 创建技能定义（含 YAML frontmatter）
2. 添加辅助文件（references/、scripts/）按需
3. 更新 `AGENTS.md` 加入新技能描述
4. 更新本 README 加入新技能条目

## 许可证

MIT
