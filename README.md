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
│   └── research-landscape/
│       ├── SKILL.md                    ← 技能定义（编排层）
│       ├── references/
│       │   ├── search-strategies.md    ← 搜索策略模板
│       │   ├── source-guide.md         ← API 端点、仓库、速率限制
│       │   └── report-template.md      ← 报告 Markdown 骨架
│       └── scripts/
│           ├── search_arxiv.py
│           ├── search_semantic_scholar.py
│           ├── fetch_otel_updates.py
│           ├── fetch_openinference_updates.py
│           ├── fetch_tool_releases.py
│           └── generate_report.py
```

## 新增技能

1. 在 `skills/<技能名>/SKILL.md` 创建技能定义（含 YAML frontmatter）
2. 添加辅助文件（references/、scripts/）按需
3. 更新 `AGENTS.md` 加入新技能描述
4. 更新本 README 加入新技能条目

## 许可证

MIT
