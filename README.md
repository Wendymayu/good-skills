# Good Skills — 编码智能体技能合集

面向多平台编码智能体（Claude Code、Codex CLI、OpenCode、Cursor）的实用技能合集。每个技能是自包含的工作流，通过斜杠命令调用。

## 已有技能

### research-landscape（技术领域全景观测）

采集、综合、报告任意技术领域的最新进展，覆盖 7 大板块。产出结构化中文 Markdown 报告，保留原文标题，中文摘要。

**调用**：`/good-skills:research-landscape <话题> [--since YYYY-MM-DD] [--deep]`

**7 大板块**（从可看可不看 → 必须关注）：
1. 行业周刊精选（TLDR AI、Latent Space、The Batch、RadarAI）
2. 国内信源（InfoQ、量子位、AI前线、知乎、即刻）
3. 学术论文（arXiv、Semantic Scholar、Twitter/X 学术号）
4. 标准&开源社区（按话题动态适配）
5. 大厂工程博客（Azure、Google、AWS、Anthropic、OpenAI、Datadog、New Relic、阿里云、腾讯云、火山引擎）
6. 开源工具动态（按话题动态适配）

**前置条件**：
```bash
pip install requests python-dateutil
```

可选：设置 `GITHUB_TOKEN` 和 `SEMANTIC_SCHOLAR_API_KEY` 环境变量。

### learn-domain（技术领域学习指南）

为任意技术领域生成结构化学习指南，含概念依赖图、分级学习路径、资源推荐、实战项目建议和避坑指南。自动引用 research-landscape 报告的热点数据。

**调用**：`/good-skills:learn-domain <话题> [--level beginner|intermediate] [--project <项目描述>] [--lang zh|en]`

**5 步工作流**：
1. 领域骨架（概念依赖图 + 术语对照 + 分级学习层级）— Claude 知识生成
2. WebSearch 定向补充资源链接
3. 引用 landscape 报告热点（如存在）
4. 实战项目建议生成
5. 渲染 Markdown 学习指南

**前置条件**：无（纯 WebSearch + Claude 知识，不依赖 Python 脚本）

### web-to-local-md（网站文档离线下载）

将网站文档专区完整下载到本地 Markdown 文件，含图片和渲染后的 Mermaid 流程图，支持 Typora 等编辑器离线阅读。优先从 GitHub 下载源 `.md` 文件（质量远优于 HTML 转换），自动处理 VuePress/VitePress SPA 懒加载、Mermaid 图表渲染、CDN 图片下载和相对路径修正。

**调用**：`/good-skills:web-to-local-md <网站URL> --github-repo OWNER/REPO --output-dir DIR --render-mermaid`

**适用场景**：VuePress/VitePress 文档站、GitHub 开源项目文档、任何需要离线阅读的技术文档网站。

**前置条件**：
```bash
# Python 3 必需
# 可选：渲染 Mermaid 流程图为 PNG
npm install -g @mermaid-js/mermaid-cli
```

**使用示例**：
```
/good-skills:web-to-local-md https://javaguide.cn/ai/ --github-repo Snailclimb/JavaGuide --output-dir ./downloaded --render-mermaid
```

### evaluate-skill（Skill 质量评估）

评估任意 good-skills skill 的输出质量。三层评估：通用结构断言 → SKILL.md 合规性（LLM-as-Judge）→ 可选回归对比。SKILL.md 本身就是评估 rubric，新增 skill 时评估自动生效，零额外代码。支持批量评估和综合报告。

**调用**：`/good-skills:evaluate-skill <skill-name> [--input <路径>] [--run <skill参数>] [--golden <路径>] [--regress <参考路径>] [--verbose]`

**适用场景**：Skill 变更后验证、新 Skill 首次验收、定期质量检查、多版本对比。

**局限**：黑盒评估（无中间追踪）；LLM-as-Judge ±1 波动；非文件输出类 skill 不适用。

**前置条件**：无（纯 Claude 编排，不依赖 Python 评估脚本）

## 安装

### Claude Code

```bash
claude plugin install good-skills
```

或从本地目录安装：
```bash
claude plugin install --path d:/opensource/github/good-skills
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
/good-skills:research-landscape 微服务治理 --since 2026-05-01  # 微服务治理
/good-skills:research-landscape safety --deep              # 安全深度扫描
/good-skills:web-to-local-md https://javaguide.cn/ai/ --github-repo Snailclimb/JavaGuide --output-dir ./downloaded --render-mermaid  # 下载网站文档到本地
/good-skills:learn-domain 可观测                          # 可观测性学习指南（自动判断层级）
/good-skills:learn-domain AI agent --level beginner       # Agent 入门路径
/good-skills:learn-domain Rust --project "写一个CLI工具"   # 反向推导Rust学习路径
/good-skills:learn-domain Kubernetes --lang en            # 英文输出
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
