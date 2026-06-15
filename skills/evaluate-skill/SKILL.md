---
name: evaluate-skill
description: Use when the user asks to "evaluate", "评估", "验证", "质量检查" a skill's output quality. Evaluates any good-skills skill using SKILL.md as rubric with structural assertions + LLM-as-Judge compliance scoring. Supports single-case, batch, and run-then-evaluate modes.
allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch, Bash(python *), TodoWrite
argument-hint: "[skill-name] [--input <路径>] [--run <skill参数>] [--golden <路径>] [--regress <参考路径>] [--verbose]"
---

# Skill 输出质量评估

评估任意 skill 的输出质量，产出一份结构化评估报告。以 SKILL.md 为唯一 rubric，通过通用结构断言 + LLM-as-Judge 合规性评分，发现输出中的结构缺失、内容偏差、降级失败等问题，加速 SKILL.md 的迭代优化。

**核心定位**：skill 质量改进的**反馈工具**，不是绝对质量裁判。评估报告帮你快速发现问题，但关键决策仍需人工确认。

## 参数

解析 `$ARGUMENTS`：
- **skill-name**（必填）：要评估的 skill 名称（如 `web-to-local-md`、`research-landscape`、`learn-domain`）。空参数 = 报错，必须询问用户想评估哪个 skill。
- **--input <路径>**（可选）：指定已有输出文件路径。事后评估模式——评估已存在的输出文件。默认：在当前目录下自动查找匹配 skill 输出模式的文件（如 `research-landscape-report-*.md`、`learn-domain-guide-*.md`）。
- **--run <skill参数>**（可选）：先执行目标 skill 再评估其输出。`<skill参数>` 是目标 skill 的完整参数字符串（如 `--run "可观测 --since 2026-05-01"`）。evaluate-skill 会先调用目标 skill，然后自动定位其输出文件进行评估。
- **--golden <路径>**（可选）：批量评估黄金数据集目录路径。扫描该目录下的 `case-*` 子目录，逐个评估。产出综合评估报告。
- **--regress <参考路径>**（可选）：与参考输出做回归对比。可以是单文件路径或目录路径。读取参考输出，对比结构与语义差异，分类为改进/退化/不变。
- **--verbose**（可选）：输出详细判断依据（默认只输出分数和结论）。启用后每项断言和评分的推理过程完整呈现。

## 三种运行模式

| 模式 | 参数 | 说明 |
|------|------|------|
| 事后评估（默认） | `evaluate-skill web-to-local-md --input ./downloaded` | 评估已有输出文件 |
| 一体化 | `evaluate-skill research-landscape --run "可观测"` | 先执行目标 skill，再评估其输出 |
| 批量评估 | `evaluate-skill web-to-local-md --golden ./golden/web-to-local-md/` | 逐个评估黄金数据集中的所有 case-* 用例 |

## 工作流

严格按以下 5 步顺序执行。不得跳过步骤。

### 步骤 0：定位 SKILL.md + 输入文件

创建 TodoWrite 清单：
```
- [ ] 步骤 0：定位 SKILL.md 和输入文件
- [ ] 步骤 1：通用结构断言
- [ ] 步骤 2：SKILL.md 合规性评估（LLM-as-Judge）
- [ ] 步骤 3：回归对比（可选）
- [ ] 步骤 4：聚合与生成评估报告
```

**定位 SKILL.md**：根据传入的 `skill-name`，在 `skills/` 目录下查找对应的 `SKILL.md`。

```bash
Glob: skills/{skill-name}/SKILL.md
```

如果找不到 SKILL.md → 报错，告知用户该 skill 不存在或没有 SKILL.md 定义。evaluate-skill 只能评估有 SKILL.md 的 skill。

**定位输入文件**（按优先级）：

1. 如果指定了 `--input` → 直接使用该路径（文件或目录）
2. 如果指定了 `--run` → 先执行目标 skill，传入 `<skill参数>`：
   ```
   /good-skills:{skill-name} {skill参数}
   ```
   执行完成后，在当前目录下用 Glob 查找匹配 skill 输出模式的文件
3. 如果指定了 `--golden` → 扫描所有 `case-*` 子目录：
   ```bash
   Glob: {golden路径}/case-*/*
   ```
   每个用例目录应有 `input.yaml` 和 `reference/` 子目录
4. 如果以上都未指定 → 在当前目录下自动查找匹配 skill 输出模式的文件。常见模式：
   - `research-landscape` → `research-landscape-report-*.md`
   - `learn-domain` → `learn-domain-guide-*.md`
   - `web-to-local-md` → `downloaded/**/*.md`

**如果找不到任何输出文件** → 报错，告知用户没有可评估的输出。建议使用 `--run` 模式先执行目标 skill，或使用 `--input` 指定已有文件路径。

### 步骤 1：通用结构断言

Claude 读输出文件，逐项检查通用断言清单。每项产出 ✅/❌ + 具体问题描述。

断言清单详见 references/structural-checks.md，核心 8 项：

| # | 断言项 | 检查方法 | 严重级别 |
|---|--------|---------|---------|
| 1 | 输出文件存在 | Glob 查找匹配文件 | 🔴 Critical |
| 2 | 文件非空（> 100 字符） | Read 文件，检查长度 | 🔴 Critical |
| 3 | Markdown 可解析（有标题、段落） | Read 文件，检查 `#` 标题和段落存在 | 🟡 Medium |
| 4 | 无未填充占位符 | Grep 搜索 `{PLACEHOLDER}`、`TODO`、`TBD`、`FIXME` | 🔴 Critical |
| 5 | URL 是文章级 | 检查 URL 路径深度 ≥ 2 | 🟡 Medium |
| 6 | 图片引用是本地路径（非 CDN） | 检查 `![](...)` 中无 `http://` 开头的链接 | 🟡 Medium |
| 7 | 占位标记占比 < 30% | 计算 `[链接暂缺]`、`本期无更新`、`仅标题+链接` 占比 | 🟡 Medium |
| 8 | 无 Markdown 语法损坏 | 检查表格行列对齐和代码块闭合 | 🟢 Low |

**执行规则**：
- 逐项执行，每项记录结果和详情
- 🔴 Critical 项失败 → 报告"严重问题"标签，需优先修复
- 🟡 Medium 项失败 → 报告"需关注"标签
- 🟢 Low 项失败 → 报告"小问题"标签
- 断言 6（图片路径）仅适用于有图片下载的 skill（如 web-to-local-md）；报告类 skill 标记为"不适用"，不计入通过率

通过率 = ✅ 项数 / 总项数（不含"不适用"和"跳过"项）。

**批量模式**：对每个 case-* 用例独立执行断言，汇总各用例结果。

### 步骤 2：SKILL.md 合规性评估（LLM-as-Judge）

Claude 读 SKILL.md + 读输出文件，对照评估输出是否符合 SKILL.md 定义。

评分维度详见 references/scoring-rubric.md，4 个维度 1-5 分制：

**维度 1：完整性（Completeness）— 1-5 分**

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 缺少 SKILL.md 要求的 3+ 个核心输出板块 | "报告缺少板块一、二、四" |
| 2 | 缺少 2 个板块，或超过 2 个板块内容严重不足 | "板块二仅有 1 条，板块五仅有 2 条" |
| 3 | 所有板块存在，但 1-2 个板块内容较薄 | "板块六仅 3 条，SKILL.md 预期 5+" |
| 4 | 所有板块完整，个别条目偏少但可接受 | "所有板块有内容，板块四偏少" |
| 5 | 所有板块完整充实，条目数量符合 SKILL.md 预期 | "7 个板块均有 5+ 条内容" |

**维度 2：准确性（Accuracy）— 1-5 分**

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 严重事实错误或合成内容 | "3 个 URL 是合成内容，无法在真实网站找到" |
| 2 | 有 1-2 处可验证的错误 | "2 个链接返回 404" |
| 3 | 绝大部分准确，个别条目需外部验证 | "1 个摘要偏简略需核实" |
| 4 | 准确，所有内容无需外部验证即可确认正确 | "所有 URL 可访问，摘要与原文相符" |
| 5 | 所有内容经验证正确，信息密度高 | "WebFetch 抽查 3 条均准确" |

**维度 3：合规性（Compliance）— 1-5 分**

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 违反了 SKILL.md 中 3+ 条"常见错误"规则 | "标题被翻译了、板块被跳过、URL 是首页级" |
| 2 | 违反了 1-2 条规则 | "标题被翻译（违反保留原文规则）" |
| 3 | 基本合规，有 1 处轻微违规 | "1 个 URL 是首页级但标注了'链接暂缺'" |
| 4 | 完全合规，遵循了所有明确规则 | "板块顺序正确、标题保留原文、URL 文章级" |
| 5 | 合规 + 主动遵循了降级策略和 URL 质量规则 | "降级标记清晰、URL 经二次搜索获取" |

**维度 4：可用性（Usability）— 1-5 分**

| 分数 | 定义 | 判断依据示例 |
|------|------|-------------|
| 1 | 输出无法使用 | "Markdown 无法渲染，表格错乱" |
| 2 | 可勉强阅读，需大量人工修正 | "需手动修正 5+ 个链接" |
| 3 | 可正常阅读，部分内容需手动补充 | "3 个链接需手动搜索" |
| 4 | 可直接使用，偶有瑕疵 | "1 个链接需手动复制而非直接可点击" |
| 5 | 高质量输出，无需任何人工修正 | "格式完美、内容充实、链接全部有效" |

**评估流程**（关键规则）：

1. **先推理再评分** — 每个维度必须先列出判断依据（具体指出哪条内容支持哪个分数），再给出分数。避免"凭感觉打分"。
2. **SKILL.md 是唯一 rubric** — 不引入外部标准，只对照 SKILL.md 的定义评估。SKILL.md 中没有要求的板块，即使缺失也不扣分。
3. **多维分开评** — 不用一个总分糊弄，4 个维度各自独立评分。
4. **状态感知** — 评估时只考虑输出中实际呈现的信息，不用"上帝视角"判断信息是否完整或真实。对于准确性维度，只标记可从输出内容中直接判断的错误，不凭空猜测。

**总体评级规则**：

4 维度平均分 → 星级：
- 平均 ≥ 4.5 → ⭐⭐⭐⭐⭐
- 平均 ≥ 4.0 → ⭐⭐⭐⭐
- 平均 ≥ 3.0 → ⭐⭐⭐
- 平均 ≥ 2.0 → ⭐⭐
- 平均 < 2.0 → ⭐

**通过门槛**：每维度 ≥ 3 且平均 ≥ 3.0 为"通过"，否则为"需改进"。

**批量模式**：对每个 case-* 用例独立评分，汇总后计算语义平均分。

### 步骤 3：回归对比（可选，仅 --regress 或 --golden）

此步骤仅在指定 `--regress` 或 `--golden` 时执行。否则跳过，报告模板中"回归对比"板块填写"未启用"。

读取参考输出文件（`--regress` 指定的路径或 `--golden` 中每个用例的 `reference/` 目录），Claude 对比两者差异：

**对比维度**：

| 维度 | 检查内容 | 分类标准 |
|------|---------|---------|
| 结构差异 | 缺少的板块、新增的板块 | 新增必要板块 → 改进；缺少原有板块 → 退化；板块相同 → 不变 |
| 语义差异 | 内容准确性变化、信息密度变化 | 信息更准确/更充实 → 改进；信息减少或偏误 → 退化；内容持平 → 不变 |
| 格式差异 | 标题层级、表格结构、链接格式变化 | 格式更规范 → 改进；格式损坏 → 退化 |

每个差异点分类为：✅ 改进 / ⚠️ 退化 / — 不变。

不做数值 embedding similarity——用 Claude 自身做语义对比，与 skill 生态的纯 Claude 编排风格一致。

**批量模式**：对每个 case-* 用例的输出与 reference/ 目录中的参考输出做对比。

### 步骤 4：聚合与生成评估报告

使用 references/report-template.md 的模板结构，填充所有 `{PLACEHOLDER}` 变量。

**单用例模式**：生成一份评估报告 `evaluate-skill-report-{skill-name}-{日期}.md`

填充映射：

| 模板变量 | 数据来源 |
|---------|---------|
| `{SKILL_NAME}` | 参数 skill-name |
| `{DATE}` | 今天日期 |
| `{INPUT_DESCRIPTION}` | 输入文件路径或 `--run` 参数描述 |
| `{EVAL_MODE}` | "事后评估" / "一体化" / "批量评估" |
| `{STRUCTURAL_PASSED}` | 步骤 1 中 ✅ 项数 |
| `{STRUCTURAL_TOTAL}` | 步骤 1 中总项数（不含"不适用"） |
| `{STRUCTURAL_RESULTS}` | 步骤 1 的逐项结果表格 |
| `{STRUCTURAL_RATE}` | 通过率百分比 |
| `{SEMANTIC_AVG}` | 4 维度平均分 |
| `{COMPLETENESS_SCORE}` | 完整性维度分数 |
| `{COMPLETENESS_EVIDENCE}` | 完整性判断依据 |
| `{ACCURACY_SCORE}` | 准确性维度分数 |
| `{ACCURACY_EVIDENCE}` | 准确性判断依据 |
| `{COMPLIANCE_SCORE}` | 合规性维度分数 |
| `{COMPLIANCE_EVIDENCE}` | 合规性判断依据 |
| `{USABILITY_SCORE}` | 可用性维度分数 |
| `{USABILITY_EVIDENCE}` | 可用性判断依据 |
| `{OVERALL_RATING}` | 星级评级 |
| `{CONCLUSION}` | "通过" / "需改进" |
| `{REGRESSION_RESULTS}` | 步骤 3 回归对比结果（或"未启用"） |
| `{IMPROVEMENT_SUGGESTIONS}` | 根据改进建议规则生成的建议列表 |

**批量模式**：生成综合评估报告，包含额外板块：

| 模板变量 | 数据来源 |
|---------|---------|
| `{GOLDEN_PATH}` | --golden 参数路径 |
| `{CASE_COUNT}` | case-* 用例数量 |
| `{BATCH_STRUCTURAL_RATE}` | 所有用例的结构通过率 |
| `{BATCH_SEMANTIC_AVG}` | 所有用例的语义平均分 |
| `{BATCH_OVERALL_RATING}` | 总体星级评级 |
| `{CASE_TABLE}` | 逐用例评分表 |
| `{COMMON_ISSUES}` | 出现在 ≥3 个用例中的共性问题 |
| `{BATCH_IMPROVEMENT_SUGGESTIONS}` | 合并改进建议 |

报告写入 Markdown 文件，命名为 `evaluate-skill-report-{skill-name}-{日期}.md`。

读取生成的报告并呈现给用户。说明文件路径。

标记所有 TodoWrite 条目为完成。

## 改进建议生成规则

评估报告末尾的改进建议不是泛泛说"提高质量"，而是指向具体 SKILL.md 位置的修改建议：

| 问题类型 | 建议格式 |
|---------|---------|
| 结构缺失 | "建议在 SKILL.md 的步骤 N 中补充明确要求输出 `<板块名>`" |
| 合规违规 | "建议在 SKILL.md 的常见错误部分增加：`<具体规则描述>`" |
| 降级失败 | "建议在 SKILL.md 的降级策略部分补充 `<具体场景>` 的处理规则" |
| 信息质量 | "建议在 SKILL.md 的搜索策略部分调整 `<关键词>` 为 `<更精准的关键词>`" |

**建议必须具体**：指明 SKILL.md 的哪个步骤、哪个板块、哪条规则需要修改。不允许"建议提高输出质量"这类泛泛建议。

## 常见错误

- **评估纯对话型 skill** — 没有文件输出就无法做结构断言，evaluate-skill 不适用。只评估有文件输出的 skill。
- **跳过结构断言直接评分** — 结构断言是必做步骤（步骤 1），不是可选。必须先完成结构断言再做合规性评分。结构断言中的 🔴 Critical 项失败应优先修复再重评。
- **用外部标准而非 SKILL.md 评分** — SKILL.md 是唯一 rubric。不允许引入外部标准（如"业界最佳实践"）来评判输出。SKILL.md 中没有要求的板块，缺失也不扣分。
- **不列出判断依据直接给分数** — 每个维度必须先推理再评分。判断依据应具体指向输出中的哪条内容、哪个位置支持该分数。不允许"整体还行，给 3 分"。
- **评估时用上帝视角** — 只看输出中实际呈现的信息来判断。不允许凭空猜测 URL 是否真实、信息是否完整。对于准确性维度，只标记可从输出内容中直接观察到的错误。
- **评估报告留空占位符** — 所有 `{PLACEHOLDER}` 必须填充具体内容。不允许出现 `{IMPROVEMENT_SUGGESTIONS}` 或 `{COMPLETENESS_EVIDENCE}` 等未填充的占位符。
- **--run 模式不传入 skill 参数** — 使用 `--run` 时必须同时传入目标 skill 的完整参数（如 `--run "可观测 --since 2026-05-01"`）。不传参数则目标 skill 无法执行，评估无从做起。

## 与其他 skill 的协作

- evaluate-skill 是独立 skill，但需要其他 skill 有 SKILL.md 才能评估。没有 SKILL.md 的 skill 无法评估。
- 可评估任何有文件输出的 skill（不限于 good-skills 项目内的 skill）。只需提供 SKILL.md 蓝本路径和输出文件路径。
- `--run` 模式会先调用目标 skill，再评估其输出。一体化流程，适合首次验收新 skill。
- 配合 `/loop` 实现定期质量检查：`/loop 168h /good-skills:evaluate-skill {skill-name} --run "{skill参数}"`

## 适用场景与局限

### 适用场景

| 场景 | 说明 |
|------|------|
| Skill 变更后验证 | 改了 SKILL.md 或脚本，重跑评估确认输出质量不退化 |
| 新 Skill 首次验收 | 新 skill 写完后，跑评估确认基本质量达标 |
| 定期质量检查 | 配合 /loop 周期性评估 skill 输出，发现退化趋势 |
| 多版本对比 | 修改 SKILL.md 前后各跑一次，对比改进效果 |

### 局限性

| 局限 | 原因 | 影响 |
|------|------|------|
| 黑盒评估 | Claude Code 内部 LLM 调用不可观测 | 只能评估最终输出，无法追踪中间过程 |
| LLM-as-Judge 主观性 | 不同运行可能给出不同评分 | 同一份输出跑两次，分数可能有 ±1 波动 |
| --run 模式成本高 | 先跑目标 skill 再评估 | 双重 token 消耗 |
| 黄金参考维护成本 | 需要人工标注和更新参考输出 | 参考输出会过时 |
| 非执行类 skill 不适用 | 纯对话型 skill 没有文件输出 | 无法评估纯对话质量 |

## 快速参考

| 步骤 | 动作 | 工具 |
|------|------|------|
| 0. 定位 | Glob 查找 SKILL.md + 输出文件 | Glob, Read |
| 1. 断言 | Read 输出文件 → 逐项 ✅/❌ | Read, Grep, Glob |
| 2. 评分 | Read SKILL.md + 输出文件 → 4 维度 1-5 分 | Read |
| 3. 回归（可选） | Read 参考输出 → 对比差异 | Read |
| 4. 报告 | 填充 report-template.md → 写文件 | Read, Write |
