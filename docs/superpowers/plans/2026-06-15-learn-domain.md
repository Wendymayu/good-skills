# learn-domain Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a learn-domain skill that generates structured learning guides for any tech domain, combining Claude knowledge for the conceptual backbone with WebSearch for fresh resource links.

**Architecture:** Hybrid approach — Claude generates the domain skeleton (concepts, dependency graph, learning tiers, terminology, pitfalls) from its own knowledge, then WebSearch supplements each tier with article-level resource URLs. If a research-landscape report exists in the working directory, its trend commentary is extracted as the "current hotspots" section. No Python scripts needed (unlike landscape which uses API calls); all work is done through WebSearch/WebFetch/Read/Write tool orchestration within the SKILL.md instructions.

**Tech Stack:** Skill definition in Markdown (SKILL.md with YAML frontmatter), report template in Markdown, no scripts. Follows the established good-skills project pattern.

---

## File Structure

| File | Responsibility | Action |
|------|---------------|--------|
| `skills/learn-domain/SKILL.md` | Skill definition — triggers, parameters, workflow instructions | Create |
| `skills/learn-domain/references/report-template.md` | Output template with placeholder variables for the rendered guide | Create |
| `AGENTS.md` | Project-level skill registry — add learn-domain entry | Modify |
| `README.md` | User-facing docs — add learn-domain entry | Modify |

---

### Task 1: Report Template

**Files:**
- Create: `skills/learn-domain/references/report-template.md`

This is the Markdown skeleton that the skill fills in during rendering. It uses `{PLACEHOLDER}` variables matching the landscape template pattern.

- [ ] **Step 1: Write the report template**

Create `skills/learn-domain/references/report-template.md` with this content:

```markdown
# {TOPIC} 学习指南

**生成日期**: {DATE}
**话题**: {TOPIC}
**学习层级**: {LEVEL}

---

## 一、领域全景

{DOMAIN_OVERVIEW}

---

## 二、术语对照表

| 中文 | 英文 | 一句话释义 |
|------|------|-----------|
{TERMINOLOGY_TABLE}

---

## 三、概念依赖图

{CONCEPT_DEPENDENCY_GRAPH}

---

## 四、分级学习路径

### 第一层：基础（估计 {BEGINNER_DAYS} 天）

**需掌握的概念**：
{BEGINNER_CONCEPTS}

**推荐资源**：

| # | 资源标题 | 推荐理由 | 链接 |
|---|---------|---------|------|
{BEGINNER_RESOURCES}

### 第二层：核心（估计 {CORE_DAYS} 天）

**需掌握的概念**：
{CORE_CONCEPTS}

**推荐资源**：

| # | 资源标题 | 推荐理由 | 链接 |
|---|---------|---------|------|
{CORE_RESOURCES}

### 第三层：进阶（估计 {ADVANCED_DAYS} 天）

**需掌握的概念**：
{ADVANCED_CONCEPTS}

**推荐资源**：

| # | 资源标题 | 推荐理由 | 链接 |
|---|---------|---------|------|
{ADVANCED_RESOURCES}

---

## 五、实战项目建议

| # | 项目 | 难度 | 学到的核心概念 | 估计时间 |
|---|------|------|---------------|---------|
{PROJECT_TABLE}

---

## 六、当前热点

{CURRENT_HOTSPOTS}

---

## 七、避坑指南

{PITFALL_GUIDE}

---

*学习指南由 learn-domain skill 自动生成。建议搭配 /good-skills:research-landscape 补充最新行业动态。*
```

- [ ] **Step 2: Commit**

```bash
cd d:/opensource/github/good-skills
git add skills/learn-domain/references/report-template.md
git commit -m "feat(learn-domain): add report template with placeholder variables"
```

---

### Task 2: SKILL.md — Core Definition

**Files:**
- Create: `skills/learn-domain/SKILL.md`

This is the main skill definition file. It contains YAML frontmatter (name, description, allowed-tools, argument-hint) and the full workflow instructions that Claude follows when the skill is invoked.

- [ ] **Step 1: Write the SKILL.md**

Create `skills/learn-domain/SKILL.md` with this content:

```markdown
---
name: learn-domain
description: Use when the user asks to "learn", "study", "入门", "上手", "学习路径", "怎么学", "推荐学习路线", or mentions wanting a structured learning guide for any technology domain. Works with any domain — observability, AI agents, LLM, Kubernetes, Rust, etc. Produces a structured Chinese learning guide with concept dependency graph, tiered learning path, resource recommendations, and practical project suggestions.
allowed-tools: WebSearch, WebFetch, Read, Write, Glob, TodoWrite
argument-hint: "[话题] [--level beginner|intermediate] [--project <项目描述>] [--lang zh|en]"
---

# 技术领域学习指南生成器

为任意技术领域生成结构化学习指南，解决"不知道该学什么、按什么顺序学、哪些资源靠谱"的问题。产出一份中文 Markdown 学习指南，概念名称附英文原文。

## 参数

解析 `$ARGUMENTS`：
- **话题**：必填，技术领域名称（如"可观测"、"Kubernetes"、"Rust"）。空参数 = 报错，必须询问用户想学什么领域。
- **--level beginner|intermediate**：可选，指定起点层级。默认：根据用户上下文自动判断（新手选 beginner，有基础选 intermediate）。
- **--project <项目描述>**：可选，用户有具体项目目标时，反向推导必须学的概念。
- **--lang zh|en**：可选，输出语言。默认 `zh`（中文为主 + 英文术语）。

## 关键词生成

根据用户话题，生成双语术语对照表的关键词。如果用户用语是中文，推断对应的英文术语；如果是英文，推断中文。示例：用户说"可观测" → 推断 "Observability, LLM monitoring, distributed tracing"。

## 工作流

严格按以下 5 步顺序执行。不得跳过步骤。

### 步骤 1：准备与领域骨架

创建 TodoWrite 清单：
```
- [ ] 步骤 1：领域骨架生成
- [ ] 步骤 2：WebSearch 定向补充资源
- [ ] 步骤 3：引用 landscape 报告热点
- [ ] 步骤 4：实战项目建议生成
- [ ] 步骤 5：渲染学习指南
```

用自身知识生成领域骨架，包含以下四个部分（**不使用 WebSearch，纯知识输出**）：

**a) 领域全景**：一句话定义该领域是什么 + 核心子方向列表（3-6 个）。每个子方向用一句话描述。

**b) 术语对照表**：列出该领域 10-20 个核心术语，每条包含中文、英文、一句话释义。释义必须准确简洁，不是泛泛描述。

**c) 概念依赖图**：用 Markdown 树状层级格式表示概念之间的依赖关系。每个概念标注层级标签 `[基础]`、`[核心]`、`[进阶]` 和一句话简释（如 `← 单次操作记录`）。

层级标签规则：
- `[基础]`：概念依赖图中最底层、无前置依赖的概念。目标：能读懂该领域的文章和对话。
- `[核心]`：依赖图中间层、有 1-2 个前置的概念。目标：能独立完成该领域的常规项目。
- `[进阶]`：依赖图顶层、多个前置的概念 + 当前热点。目标：能做技术决策、理解前沿趋势。

如果用户提供了 `--project` 参数：从项目目标反向推导，标注哪些概念是"必须学"（项目直接依赖），哪些是"可选学"（了解即可），在依赖图中用 `⚡` 标记必须学的概念。

**d) 分级概念列表**：将概念依赖图中的概念按层级分组，形成三个学习层级的概念清单。计算每层估计天数（基础层按每个概念约 1-2 天，核心层约 2-3 天，进阶层约 3-5 天）。

### 步骤 2：WebSearch 定向补充

为每个学习层级搜索入门资源。**精准搜索，不做大规模采集**。

**搜索计划**（每层 1-2 次搜索，取前 5 条）：

| 目标 | 搜索关键词 |
|------|-----------|
| 基础资源 | `<话题英文> beginner tutorial guide introduction` |
| 核心资源 | `<话题英文> best practices production practical guide` |
| 进阶资源 | `<话题英文> advanced deep dive architecture internals` |
| 中文资源 | `<话题中文> 入门 教程 实践 最佳实践` |
| 避坑指南 | `<话题英文> common mistakes pitfalls misconceptions` |

总计约 5 次搜索，每层最多 5 条资源。

**资源提取规则**：
- 每条资源记录 `{title, reason, url}`
- `reason` 是一句话推荐理由（为什么这篇适合该层级的学习者）
- URL 必须是文章级链接（路径深度 ≥ 1），不能是首页
- 如果 WebSearch 返回合成摘要而非具体 URL → 标记 `[链接暂缺，请搜索 <关键词>]`
- 搜索失败不阻塞——骨架输出仍然完整

**避坑指南补充**：WebSearch 搜索 1 次 `<话题英文> common mistakes pitfalls misconceptions`，提取 1-2 条社区反馈的常见坑。与 Claude 知识生成的避坑合并（去重）。

### 步骤 3：引用 landscape 报告热点

检查当前工作目录是否存在 `research-landscape-report-*.md` 文件：

```bash
Glob: research-landscape-report-*.md
```

**如果存在**：读取该文件，提取"七、趋势点评"部分的内容，作为"当前热点"板块的数据来源。引用时注明来源报告的日期。

**如果不存在**：输出以下提示文字：
```
建议运行 /good-skills:research-landscape {话题} 补充当前行业热点和最新动态。
```

### 步骤 4：实战项目建议

根据话题 + 用户 `--project` 参数（如有），生成 2-3 个实战项目建议。

**项目建议规则**：
- 项目从易到难排列
- 每个项目必须明确标注：难度（⭐/⭐⭐/⭐⭐⭐）、学到的核心概念列表、估计时间
- 如果用户提供了 `--project`：第一个项目建议应直接对齐用户的项目目标，标注"直接对齐你的项目目标"
- 项目建议应具体可执行（如"用 OpenTelemetry SDK 给一个 Flask API 添加 tracing"），不是泛泛的"做一个项目"

### 步骤 5：渲染学习指南

1. 将所有采集数据合并：

```
{
  "date": "<今天>",
  "topic": "<话题>",
  "level": "<层级>",
  "domain_overview": "<领域全景文字>",
  "terminology_table": "<术语对照表 Markdown>",
  "concept_dependency_graph": "<概念依赖图文字>",
  "beginner_days": "<基础天数>",
  "beginner_concepts": "<基础概念列表>",
  "beginner_resources": "<基础资源表格>",
  "core_days": "<核心天数>",
  "core_concepts": "<核心概念列表>",
  "core_resources": "<核心资源表格>",
  "advanced_days": "<进阶天数>",
  "advanced_concepts": "<进阶概念列表>",
  "advanced_resources": "<进阶资源表格>",
  "project_table": "<实战项目表格>",
  "current_hotspots": "<热点文字>",
  "pitfall_guide": "<避坑指南文字>"
}
```

2. 用步骤 1-4 生成的数据填充模板中的所有 `{PLACEHOLDER}` 变量。

3. 写入 Markdown 文件，命名为 `learn-domain-guide-{话题}-{日期}.md`。

4. 读取生成的指南并呈现给用户。说明文件路径。

5. 标记所有 TodoWrite 条目为完成。

## 常见错误

- **跳过步骤** — 所有 5 个步骤必须执行，即使某些步骤无数据也要输出占位提示。
- **用 WebSearch 生成概念依赖图** — 概念依赖图必须由 Claude 知识生成，不依赖 WebSearch。
- **翻译概念名称** — 概念必须保留原文语言（英文术语保留英文），中文摘要附在后面。
- **使用首页级 URL** — 每条资源的 URL 必须指向具体文章页面，不是网站首页。
- **忽略 --project 参数** — 如果用户提供了项目目标，必须反向推导必须学的概念并在依赖图中标注 ⚡。
- **省略避坑指南** — 避坑指南是必输出板块，不可跳过。

## 与 research-landscape 的协作

两个 skill 独立运行但可配合使用：
- **先 landscape 再 learn-domain**：landscape 提供当前热点，learn-domain 自动引用其趋势点评作为"当前热点"板块。
- **单独使用 learn-domain**：如果无 landscape 报告，"当前热点"板块输出建议运行 landscape 的提示文字。
- **不合并**：learn-domain 不作为 landscape 的子功能，两者是独立 skill。
```

- [ ] **Step 2: Commit**

```bash
cd d:/opensource/github/good-skills
git add skills/learn-domain/SKILL.md
git commit -m "feat(learn-domain): add SKILL.md with workflow, parameters, and search strategy"
```

---

### Task 3: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

Add the learn-domain skill entry after the research-landscape section.

- [ ] **Step 1: Add learn-domain entry to AGENTS.md**

After the research-landscape section (line 13), add:

```markdown

### learn-domain（技术领域学习指南）

为任意技术领域生成结构化学习指南，解决"不知道该学什么、按什么顺序学、哪些资源靠谱"的问题。产出中文 Markdown 指南，含概念依赖图、分级学习路径、资源推荐、实战项目建议和避坑指南。自动引用 research-landscape 报告的热点数据。

**调用**：`/good-skills:learn-domain <话题> [--level beginner|intermediate] [--project <项目描述>] [--lang zh|en]`

**支持任意话题**：可观测、AI Agent、Kubernetes、Rust、微服务等，中文英文均可。

**前置条件**：无（不依赖 Python 脚本，纯 WebSearch + Claude 知识）

```

- [ ] **Step 2: Commit**

```bash
cd d:/opensource/github/good-skills
git add AGENTS.md
git commit -m "docs: add learn-domain skill entry to AGENTS.md"
```

---

### Task 4: Update README.md

**Files:**
- Modify: `README.md`

Add the learn-domain skill entry to the README, update the usage examples, and update the project structure.

- [ ] **Step 1: Add learn-domain skill description after research-landscape section**

After the research-landscape section (after line 27), add:

```markdown

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

```

- [ ] **Step 2: Add learn-domain usage examples**

In the "使用示例" section, after the landscape examples (after line 83), add:

```markdown
/good-skills:learn-domain 可观测                          # 可观测性学习指南（自动判断层级）
/good-skills:learn-domain AI agent --level beginner       # Agent 入门路径
/good-skills:learn-domain Rust --project "写一个CLI工具"   # 反向推导Rust学习路径
/good-skills:learn-domain Kubernetes --lang en            # 英文输出
```

- [ ] **Step 3: Update project structure**

In the project structure tree (around line 108), add the learn-domain directory after the research-landscape directory:

```markdown
    └── learn-domain/
        ├── SKILL.md                    ← 技能定义（编排层）
        └── references/
            └── report-template.md      ← 学习指南 Markdown 骨架
```

And update the "已有技能" count / listing accordingly.

- [ ] **Step 4: Commit**

```bash
cd d:/opensource/github/good-skills
git add README.md
git commit -m "docs: add learn-domain skill entry, examples, and project structure to README.md"
```

---

### Task 5: Verify the Skill Works — Smoke Test

**Files:**
- Verify: `skills/learn-domain/SKILL.md`, `skills/learn-domain/references/report-template.md`

Run a quick verification that the skill files are properly structured and discoverable.

- [ ] **Step 1: Verify SKILL.md frontmatter parses correctly**

Run:
```bash
cd d:/opensource/github/good-skills
python -c "
import yaml
with open('skills/learn-domain/SKILL.md') as f:
    content = f.read()
# Extract YAML frontmatter between --- markers
parts = content.split('---')
fm = yaml.safe_load(parts[1])
assert fm['name'] == 'learn-domain'
assert fm['description'] is not None
assert fm['allowed-tools'] is not None
assert fm['argument-hint'] is not None
print('Frontmatter OK:', fm)
"
```
Expected: Frontmatter parses without errors, prints `{'name': 'learn-domain', 'description': '...', 'allowed-tools': [...], 'argument-hint': '...'}`

- [ ] **Step 2: Verify report template has all required placeholders**

Run:
```bash
cd d:/opensource/github/good-skills
python -c "
with open('skills/learn-domain/references/report-template.md') as f:
    content = f.read()
required = [
    '{TOPIC}', '{DATE}', '{LEVEL}',
    '{DOMAIN_OVERVIEW}', '{TERMINOLOGY_TABLE}',
    '{CONCEPT_DEPENDENCY_GRAPH}',
    '{BEGINNER_DAYS}', '{BEGINNER_CONCEPTS}', '{BEGINNER_RESOURCES}',
    '{CORE_DAYS}', '{CORE_CONCEPTS}', '{CORE_RESOURCES}',
    '{ADVANCED_DAYS}', '{ADVANCED_CONCEPTS}', '{ADVANCED_RESOURCES}',
    '{PROJECT_TABLE}', '{CURRENT_HOTSPOTS}', '{PITFALL_GUIDE}'
]
missing = [p for p in required if p not in content]
if missing:
    print('MISSING placeholders:', missing)
else:
    print('All placeholders present ✅')
"
```
Expected: `All placeholders present ✅`

- [ ] **Step 3: Verify AGENTS.md and README.md contain learn-domain references**

Run:
```bash
cd d:/opensource/github/good-skills
grep -c "learn-domain" AGENTS.md README.md
```
Expected: Both files show count ≥ 1

- [ ] **Step 4: Final commit (if any verification fixes needed)**

If verification uncovered issues, fix them and commit. If all passed, skip this step.

---

## Self-Review

### Spec Coverage Check

| Spec Section | Task Implementing It |
|-------------|---------------------|
| §1 Skill元信息 (name, triggers, params, landscape relation) | Task 2: SKILL.md frontmatter + workflow |
| §2 工作流 (5 steps) | Task 2: SKILL.md workflow section |
| §3 输出结构 (6 sections) | Task 1: report-template.md |
| §4 概念依赖图格式 (tree + tier labels) | Task 2: SKILL.md step 1c |
| §5 WebSearch定向补充策略 | Task 2: SKILL.md step 2 |
| §6 文件结构 | Task 1 + Task 2 |
| §7 YAGNI | Design decisions reflected in Tasks (no scripts, no Mermaid) |
| AGENTS.md update | Task 3 |
| README.md update | Task 4 |

All spec sections are covered. ✅

### Placeholder Scan

No TBD/TODO/fill-in-later patterns found. All steps contain complete content. ✅

### Type Consistency

- Template placeholder names (`{BEGINNER_DAYS}`, `{CORE_RESOURCES}`, etc.) are consistent between Task 1 (template) and Task 2 (SKILL.md step 5 data merging). ✅
- SKILL.md workflow step references match template sections. ✅
