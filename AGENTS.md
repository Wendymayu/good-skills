# Good Skills — Coding Agent Skills Collection

A collection of practical skills for coding agents (Claude Code, Codex CLI, OpenCode, Cursor). Each skill is a self-contained workflow that can be invoked via slash commands.

## Available Skills

### research-observe

Collect, synthesize, and report on the latest LLM/AI Agent observability developments across 7 plates. Produces a structured Chinese markdown report with original source links and article/blog/paper titles preserved in their original language.

**Invocation**: `/good-skills:research-observe [topic] [--since YYYY-MM-DD] [--deep]`

**7 Plates** (from browsable to must-read):
1. Industry newsletters (TLDR AI, Latent Space, The Batch, RadarAI)
2. Domestic sources (InfoQ, 量子位, AI前线, 知乎, 即刻)
3. Academic papers (arXiv, Semantic Scholar, Twitter/X academic accounts)
4. Standards & open-source communities (OTel GenAI SIG, OpenInference WG, CNCF AI/ML WG)
5. Enterprise engineering blogs (Azure, Google, AWS, Anthropic, OpenAI, Datadog, New Relic, 阿里云, 腾讯云, 火山引擎)
6. Open-source tool updates (LangFuse, Phoenix, Helicone, OpenLIT, OpenLLMetry, Coze罗盘, Grafana, Dynatrace, Splunk, Elastic)

**Prerequisites**:
```bash
pip install requests python-dateutil
```

Set `GITHUB_TOKEN` env var for higher GitHub API rate limits (optional but recommended).
Set `SEMANTIC_SCHOLAR_API_KEY` env var for higher S2 rate limits (optional).

## Installation

### Claude Code

```bash
claude plugin install good-skills
```

Or install from local directory:
```bash
claude plugin install --path ./good-skills
```

### Codex CLI

Codex CLI does not have a plugin system. Use `AGENTS.md` (included in this repo) as project-level instructions.

### OpenCode

See [.opencode/INSTALL.md](.opencode/INSTALL.md) for detailed instructions.

Quick setup:
```json
{
  "plugin": ["good-skills@git+https://github.com/Wendymayu/good-skills.git"]
}
```

## Project Structure

```
good-skills/
├── .claude-plugin/plugin.json          ← Claude Code plugin declaration
├── .claude-plugin/marketplace.json     ← Marketplace catalog
├── .codex-plugin/plugin.json           ← Codex CLI compatibility
├── .opencode/                          ← OpenCode compatibility
│   ├── INSTALL.md
│   └── plugins/good-skills.js
├── AGENTS.md                           ← Codex CLI / universal instruction layer
├── README.md                           ← Human-readable entry point
├── docs/                               ← Specs, plans, design docs
└── skills/
│   └── research-observe/
│       ├── SKILL.md                    ← Skill definition (orchestration)
│       ├── references/
│       │   ├── search-strategies.md    ← WebSearch query templates
│       │   ├── source-guide.md         ← API endpoints, repos, rate limits
│       │   └── report-template.md      ← Report markdown skeleton
│       └── scripts/
│           ├── search_arxiv.py
│           ├── search_semantic_scholar.py
│           ├── fetch_otel_updates.py
│           ├── fetch_openinference_updates.py
│           ├── fetch_tool_releases.py
│           └── generate_report.py
```

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (name, description, allowed-tools, argument-hint)
2. Add supporting files (references/, scripts/) as needed
3. Update `AGENTS.md` with a brief description of the new skill
4. Update this README with the new skill entry

## License

MIT
