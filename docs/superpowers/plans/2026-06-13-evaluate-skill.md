# evaluate-skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create evaluate-skill skill that evaluates any good-skills skill's output quality using SKILL.md as rubric, with structural assertions + LLM-as-Judge + optional regression, supporting batch evaluation.

**Architecture:** Pure Claude orchestration (no Python scripts). SKILL.md defines the 5-step workflow; three reference files provide structural checks, scoring rubric, and report template. SKILL.md itself is the rubric for evaluation — new skills auto-gain evaluation support without per-skill code.

**Tech Stack:** Markdown skill definition + references (no scripts, no external dependencies)

---

### Task 1: structural-checks.md — 通用结构断言清单

**Files:**
- Create: `skills/evaluate-skill/references/structural-checks.md`

- [ ] **Step 1: Create structural-checks.md**

```markdown
# 通用结构断言清单

对所有产出 Markdown 文件的 skill 通用适用。每项断言由 Claude 读文件后判断，产出 ✅/❌ + 具体问题描述。

## 断言列表

| # | 断言项 | 检查方法 | 严重级别 |
|---|--------|---------|---------|
| 1 | 输出文件存在 | 用 Glob 查找目标 skill 的输出文件模式（如 `*.md`、`*.png`）。至少找到 1 个文件。 | 🔴 Critical |
| 2 | 文件非空 | Read 每个输出文件，检查内容长度 > 100 字符。空文件或仅含空白字符算失败。 | 🔴 Critical |
| 3 | Markdown 可解析 | Read 文件，检查至少含 1 个 `#` 标题和 2 个非空段落。 | 🟡 Medium |
| 4 | 无未填充占位符 | Grep 搜索 `{PLACEHOLDER}`、`TODO`、`TBD`、`FIXME`。这些不应出现在最终输出中。 | 🔴 Critical |
| 5 | URL 是文章级 | 提取所有 URL，检查每个 URL 的路径深度 ≥ 1（如 `/blog/xxx`，不能只是 `/` 或 `/blog`）。仅首页链接（如 `https://example.com` 或 `https://example.com/blog`）标记为失败。 | 🟡 Medium |
| 6 | 图片引用是本地路径 | 检查所有 `![](...)` 格式的图片引用，不应含 `http://` 或 `https://` 开头的外部链接。仅适用于 web-to-local-md 等下载类 skill。对于 research-landscape 等报告类 skill，此断言跳过（报告中图片引用允许外部 URL）。 | 🟡 Medium |
| 7 | 占位标记占比 < 30% | 计算输出中 `[链接暂缺]`、`本期无更新`、`仅标题+链接` 的出现次数占总条目数的比例。超过 30% 标记为失败。 | 🟡 Medium |
| 8 | 无 Markdown 语法损坏 | 检查表格格式：每个 `|` 分隔行的列数应与表头一致。检查无未闭合的代码块（`\`\`\` 开头无 `\`\`\` 结尾）。 | 🟢 Low |

## 断言执行规则

1. 逐项执行，每项记录结果和详情
2. 🔴 Critical 项失败 → 报告"严重问题"标签，需优先修复
3. 🟡 Medium 项失败 → 报告"需关注"标签
4. 🟢 Low 项失败 → 报告"小问题"标签
5. 断言 6（图片路径）根据 skill 类型决定是否执行：
   - web-to-local-md → 执行
   - research-landscape / learn-domain → 跳过，标记为"不适用"

## 结果汇总格式

| # | 断言 | 结果 | 详情 |
|---|------|------|------|
| 1 | 输出文件存在 | ✅/❌ | 找到 X 个文件 / 未找到任何文件 |
| 2 | 文件非空 | ✅/❌ | 最小文件 Y 字符 / 存在空文件 |
| ... | ... | ... | ... |

通过率 = ✅ 项数 / 总项数（不含"跳过"项）。
```

- [ ] **Step 2: Commit**

```bash
git add skills/evaluate-skill/references/structural-checks.md
git commit -m "feat(evaluate-skill): add structural checks reference — 8 universal Markdown assertions"
```

---

### Task 2: scoring-rubric.md — 4 维度评分标准

**Files:**
- Create: `skills/evaluate-skill/references/scoring-rubric.md`

- [ ] **Step 1: Create scoring-rubric.md**

```markdown
# SKILL.md 合规性评分标准

LLM-as-Judge 评估输出是否符合 SKILL.md 定义。4 个维度，每个 1-5 分制。

## 评估原则

1. **先推理再评分** — 每个维度必须先列出判断依据（具体指出哪条内容支持哪个分数），再给出分数
2. **SKILL.md 是唯一 rubric** — 不引入外部标准，只对照 SKILL.md 的定义评估
3. **多维分开评** — 不用一个总分糊弄，4 个维度各自独立评分
4. **状态感知** — 评估时只考虑输出中实际呈现的信息，不用"上帝视角"判断信息是否完整

## 维度 1：完整性（Completeness）— 1-5 分

评估输出是否包含 SKILL.md 要求的所有板块和内容。

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 缺少 SKILL.md 要求的 3+ 个核心输出板块 | "报告缺少板块一、二、四" |
| 2 | 缺少 2 个板块，或某些板块内容严重不足（仅 1-2 条而非预期 5+ 条） | "板块二仅有 1 条，板块五仅有 2 条" |
| 3 | 所有板块存在，但 1-2 个板块内容较薄（条目数低于 SKILL.md 预期） | "板块六仅 3 条，SKILL.md 预期 5+" |
| 4 | 所有板块完整，个别条目偏少但可接受 | "所有板块有内容，板块四偏少" |
| 5 | 所有板块完整充实，条目数量符合 SKILL.md 预期 | "7 个板块均有 5+ 条内容" |

## 维度 2：准确性（Accuracy）— 1-5 分

评估输出内容的事实准确性和信息质量。

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 严重事实错误或合成内容（编造了不存在的 URL/论文/事件） | "3 个 URL 是合成内容，无法在真实网站找到" |
| 2 | 有 1-2 处可验证的错误（URL 404、摘要与原文不符） | "2 个链接返回 404" |
| 3 | 绝大部分准确，个别条目需人工验证但不明显错误 | "整体准确，1 个摘要偏简略" |
| 4 | 准确，无明显错误 | "所有 URL 可访问，摘要与原文相符" |
| 5 | 所有内容经验证正确，信息密度高 | "WebFetch 抽查 3 条均准确" |

## 维度 3：合规性（Compliance）— 1-5 分

评估输出是否遵循了 SKILL.md 的规则（常见错误、URL 质量、降级策略）。

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 违反了 SKILL.md 中 3+ 条"常见错误"规则 | "标题被翻译了、板块被跳过、URL 是首页级" |
| 2 | 违反了 1-2 条规则 | "标题被翻译（违反保留原文规则）" |
| 3 | 基本合规，有 1 处轻微违规 | "1 个 URL 是首页级但标注了'链接暂缺'" |
| 4 | 完全合规，遵循了所有明确规则 | "板块顺序正确、标题保留原文、URL 文章级" |
| 5 | 合规 + 主动遵循了降级策略和 URL 质量规则 | "降级标记清晰、URL 经二次搜索获取" |

## 维度 4：可用性（Usability）— 1-5 分

评估输出对目标用户是否可直接使用。

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 输出无法使用（文件损坏、格式乱、完全缺失关键信息） | "Markdown 无法渲染，表格错乱" |
| 2 | 可勉强阅读，需大量人工修正才能实际使用 | "需手动修正 5+ 个链接和 3 个格式问题" |
| 3 | 可正常阅读，部分内容需手动补充 | "3 个链接需手动搜索，1 个板块内容偏薄" |
| 4 | 可直接使用，偶有瑕疵但不影响实际效用 | "整体质量好，1-2 个小问题" |
| 5 | 高质量输出，无需任何人工修正即可直接使用 | "格式完美、内容充实、链接全部有效" |

## 总体评级规则

4 维度平均分 → 星级：
- 平均 ≥ 4.5 → ⭐⭐⭐⭐⭐
- 平均 ≥ 4.0 → ⭐⭐⭐⭐
- 平均 ≥ 3.0 → ⭐⭐⭐
- 平均 ≥ 2.0 → ⭐⭐
- 平均 < 2.0 → ⭐

**通过门槛**：每维度 ≥ 3 且平均 ≥ 3.0 为"通过"，否则为"需改进"。
```

- [ ] **Step 2: Commit**

```bash
git add skills/evaluate-skill/references/scoring-rubric.md
git commit -m "feat(evaluate-skill): add scoring rubric — 4 dimensions with 1-5 scale definitions"
```

---

### Task 3: report-template.md — 评估报告模板

**Files:**
- Create: `skills/evaluate-skill/references/report-template.md`

- [ ] **Step 1: Create report-template.md**

```markdown
# {SKILL_NAME} 评估报告

**评估日期**: {DATE}
**Skill 名称**: {SKILL_NAME}
**输入描述**: {INPUT_DESCRIPTION}
**评估模式**: {EVAL_MODE}

---

## 一、总览

| 指标 | 值 |
|------|-----|
| 结构断言 | {STRUCTURAL_PASSED}/{STRUCTURAL_TOTAL} 通过 |
| 语义平均分 | {SEMANTIC_AVG}/5 |
| 总体评级 | {OVERALL_RATING} |
| 评估结论 | {CONCLUSION} |

---

## 二、结构断言结果

| # | 断言 | 结果 | 详情 |
|---|------|------|------|
{STRUCTURAL_RESULTS}

**通过率**: {STRUCTURAL_PASSED}/{STRUCTURAL_TOTAL} ({STRUCTURAL_RATE}%)

---

## 三、SKILL.md 合规性评估

### 完整性（{COMPLETENESS_SCORE}/5）

判断依据：
{COMPLETENESS_EVIDENCE}

### 准确性（{ACCURACY_SCORE}/5）

判断依据：
{ACCURACY_EVIDENCE}

### 合规性（{COMPLIANCE_SCORE}/5）

判断依据：
{COMPLIANCE_EVIDENCE}

### 可用性（{USABILITY_SCORE}/5）

判断依据：
{USABILITY_EVIDENCE}

---

## 四、回归对比（可选）

{REGRESSION_RESULTS}

---

## 五、改进建议

{IMPROVEMENT_SUGGESTIONS}

---

*评估报告由 evaluate-skill skill 自动生成。核心定位：skill 质量改进的反馈工具，不是绝对质量裁判。*
```

**批量模式追加模板（嵌入同一文件末尾，用 `---` 分隔）**：

```markdown
---

# {SKILL_NAME} 综合评估报告（批量模式）

**评估日期**: {DATE}
**Skill 名称**: {SKILL_NAME}
**黄金数据集**: {GOLDEN_PATH}
**用例数量**: {CASE_COUNT}

---

## 总览

| 指标 | 值 |
|------|-----|
| 测试用例数 | {CASE_COUNT} |
| 结构通过率 | {BATCH_STRUCTURAL_RATE}% |
| 语义平均分 | {BATCH_SEMANTIC_AVG}/5 |
| 总体评级 | {BATCH_OVERALL_RATING} |

---

## 逐用例评分

| 用例 | 结构 | 完整性 | 准确性 | 合规性 | 可用性 | 回归 | 关键问题 |
|------|------|--------|--------|--------|--------|------|---------|
{CASE_TABLE}

---

## 共性问题（出现在 ≥3 个用例中）

{COMMON_ISSUES}

---

## 改进建议

{BATCH_IMPROVEMENT_SUGGESTIONS}
```

- [ ] **Step 2: Commit**

```bash
git add skills/evaluate-skill/references/report-template.md
git commit -m "feat(evaluate-skill): add report template — single-case + batch-mode evaluation reports"
```

---

### Task 4: SKILL.md — Skill 定义文件

**Files:**
- Create: `skills/evaluate-skill/SKILL.md`

- [ ] **Step 1: Create SKILL.md**

Write the full SKILL.md with YAML frontmatter and 5-step workflow. Content must cover:
- Frontmatter: `name: evaluate-skill`, `description`, `allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch, Bash(python *), TodoWrite`, `argument-hint: "[skill-name] [--input <路径>] [--run <skill参数>] [--golden <路径>] [--regress <参考路径>] [--verbose]"`
- Parameter parsing section (same as spec section 1)
- 5-step workflow (steps 0-4, same as spec section 3)
- Structural assertions reference (point to structural-checks.md)
- Scoring rubric reference (point to scoring-rubric.md)
- Batch evaluation mode (golden data set directory scan, same as spec section 4)
- Improvement suggestion rules (same as spec section 5)
- Common errors section (7 items derived from spec limitations)
- Report template reference (point to report-template.md)
- Output file naming: `evaluate-skill-report-{skill-name}-{日期}.md`

The SKILL.md content mirrors the design spec's workflow and rules, adapted into the established skill format (matching research-landscape and learn-domain style).

- [ ] **Step 2: Commit**

```bash
git add skills/evaluate-skill/SKILL.md
git commit -m "feat(evaluate-skill): add SKILL.md — 5-step evaluation workflow with structural + semantic + optional regression"
```

---

### Task 5: AGENTS.md + README.md 更新

**Files:**
- Modify: `AGENTS.md` — add evaluate-skill entry after web-to-local-md section
- Modify: `README.md` — add evaluate-skill entry in "已有技能" section, add usage examples, update project structure

- [ ] **Step 1: Add evaluate-skill entry to AGENTS.md**

Insert after the web-to-local-md section:

```markdown
### evaluate-skill（Skill 质量评估）

评估任意 good-skills skill 的输出质量。SKILL.md 本身就是评估 rubric——新增 skill 时评估自动生效，零额外代码。三层评估：通用结构断言 → SKILL.md 合规性（LLM-as-Judge）→ 可选回归对比。支持批量评估（黄金数据集）和综合报告。

**调用**：`/good-skills:evaluate-skill <skill-name> [--input <路径>] [--run <skill参数>] [--golden <路径>] [--regress <参考路径>] [--verbose]`

**适用场景**：Skill 变更后验证、新 Skill 首次验收、定期质量检查、多版本对比。

**局限**：黑盒评估无中间过程追踪；LLM-as-Judge 主观性 ±1 波动；非文件输出类 skill 不适用。

**前置条件**：无（纯 Claude 编排，不依赖 Python 评估脚本）
```

- [ ] **Step 2: Add evaluate-skill entry to README.md**

Insert after the web-to-local-md section in "已有技能", add usage examples, and update project structure.

**已有技能部分** — insert after web-to-local-md:

```markdown
### evaluate-skill（Skill 质量评估）

评估任意 good-skills skill 的输出质量。三层评估：通用结构断言 → SKILL.md 合规性（LLM-as-Judge）→ 可选回归对比。SKILL.md 本身就是评估 rubric，新增 skill 时评估自动生效，零额外代码。支持批量评估和综合报告。

**调用**：`/good-skills:evaluate-skill <skill-name> [--input <路径>] [--run <skill参数>] [--golden <路径>] [--regress <参考路径>] [--verbose]`

**适用场景**：Skill 变更后验证、新 Skill 首次验收、定期质量检查、多版本对比。

**局限**：黑盒评估（无中间追踪）；LLM-as-Judge ±1 波动；非文件输出类 skill 不适用。

**前置条件**：无（纯 Claude 编排，不依赖 Python 评估脚本）
```

**使用示例部分** — add after existing examples:

```markdown
/good-skills:evaluate-skill research-landscape --input ./research-landscape-report-*.md  # 评估已有报告
/good-skills:evaluate-skill web-to-local-md --input ./downloaded                         # 评估下载输出
/good-skills:evaluate-skill research-landscape --run 可观测                               # 先执行再评估
/good-skills:evaluate-skill web-to-local-md --golden ./golden/web-to-local-md/            # 批量评估
```

**项目结构部分** — add evaluate-skill subtree after learn-domain:

```
    ├── evaluate-skill/
    │   ├── SKILL.md                    ← 技能定义（编排层）
    │   └── references/
    │       ├── structural-checks.md    ← 通用结构断言清单
    │       ├── scoring-rubric.md       ← 4 维度评分标准
    │       └── report-template.md      ← 评估报告模板
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md README.md
git commit -m "docs: add evaluate-skill entry to AGENTS.md and README.md"
```

---

### Task 6: Smoke test — 用已有 landscape 报告验证评估流程

**Files:**
- No new files (verification only)

- [ ] **Step 1: Locate existing landscape report**

Run:
```bash
ls d:/opensource/github/good-skills/research-landscape-report-*.md
```
Expected: Find the previously generated landscape report file.

- [ ] **Step 2: Verify SKILL.md reads correctly**

Run the evaluate-skill skill in simulation — manually walk through the 5-step workflow against the existing landscape report to verify:
- Step 0: Glob finds `skills/evaluate-skill/SKILL.md`
- Step 0: Glob finds the landscape report file
- Step 1: Structural assertions produce results (8 checks, some pass some fail)
- Step 2: SKILL.md compliance produces 4-dimension scores with evidence
- Step 4: Report renders with all placeholders filled

This is a manual verification — read the output files, check that each step produces expected content, and confirm no template placeholders remain unfilled in the final report.

- [ ] **Step 3: Commit verification status**

No code change needed. Mark this task as complete after visual verification.

---

## Self-Review

**1. Spec coverage:**

| Spec section | Task |
|--------------|------|
| §1 Skill metadata (name, params, allowed-tools) | Task 4 (SKILL.md frontmatter) |
| §2 适用场景与局限 | Task 4 (SKILL.md body) |
| §3 评估工作流 (steps 0-4) | Task 4 (SKILL.md workflow) |
| §3 Structural assertions (8 items) | Task 1 (structural-checks.md) |
| §3 Scoring rubric (4 dimensions) | Task 2 (scoring-rubric.md) |
| §3 Regression comparison | Task 4 (SKILL.md step 3) |
| §4 Batch evaluation (golden dataset) | Task 4 (SKILL.md batch mode) + Task 3 (batch template) |
| §5 Improvement suggestion rules | Task 4 (SKILL.md suggestions section) |
| §6 Output structure (report template) | Task 3 (report-template.md) |
| §7 File structure | Tasks 1-4 |
| §7 AGENTS.md update | Task 5 |
| §7 README.md update | Task 5 |
| Smoke test | Task 6 |

All sections covered. ✅

**2. Placeholder scan:** No TBD/TODO/implement-later found. All steps contain complete content. ✅

**3. Type consistency:** Placeholder variable names in report-template.md (`{SKILL_NAME}`, `{DATE}`, `{STRUCTURAL_RESULTS}`, etc.) are consistent between Task 3 template and Task 4 SKILL.md workflow. ✅
