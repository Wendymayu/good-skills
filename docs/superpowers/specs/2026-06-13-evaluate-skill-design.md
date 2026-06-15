# evaluate-skill Skill 设计文档

**日期**: 2026-06-13
**作者**: Claude + Wendymayu
**状态**: 设计完成，待用户审核

---

## 问题陈述

good-skills 项目已有 3 个 skill（research-landscape、learn-domain、web-to-local-md），但这些 skill 的输出质量只能靠人工阅读来判断。核心痛点：

1. **无法系统性地评估 skill 输出质量** — 不知道输出是否完整、准确、合规
2. **skill 变更后无法验证不退化** — 改了 SKILL.md 或脚本后，无法自动确认输出质量不下降
3. **per-skill 评估代码不可扩展** — 为每个 skill 写不同的评估代码，新增 skill 时评估成本线性增长
4. **黑盒评估困难** — Claude Code 内部 LLM 调用不可观测，无法追踪中间过程

## 设计决策

**方案选择**: 方案 C（分层渐进）—— 默认做通用结构断言 + LLM-as-Judge（SKILL.md 合规性评估），回归对比可选。**纯 Claude 编排，不依赖外部 Python 评估脚本**。

**理由**:
1. 与 good-skills 项目风格一致（其他 skill 都是 SKILL.md + references）
2. SKILL.md 本身就是评估 rubric——新增 skill 时评估自动生效，零额外代码
3. Claude Code 内部就能读文件、做判断、写报告
4. 不需要额外依赖（embedding 模型、评估框架）
5. 回归对比是进阶需求，可选启用，不增加基础复杂度

---

## 1. Skill 元信息

**名称**: `evaluate-skill`

**触发关键词**: "evaluate", "评估", "验证", "质量检查", "测试 skill"

**参数**:
- `<skill-name>` (必填): 要评估的 skill 名称（如 `web-to-local-md`、`research-landscape`、`learn-domain`）
- `--input <路径>` (可选): 指定已有输出文件路径（事后评估模式）
- `--run <skill参数>` (可选): 先执行目标 skill 再评估。`<skill参数>` 是目标 skill 的完整参数字符串（如 `--run "可观测 --since 2026-05-01"`）。evaluate-skill 会先调用目标 skill，然后自动定位其输出文件进行评估。
- `--golden <路径>` (可选): 批量评估黄金数据集目录路径
- `--regress <参考路径>` (可选): 与黄金参考输出做回归对比
- `--verbose` (可选): 输出详细判断依据（默认只输出分数和结论）

**两种运行模式**:
1. **事后评估**（默认）: `/good-skills:evaluate-skill web-to-local-md --input ./downloaded`
2. **一体化**: `/good-skills:evaluate-skill research-landscape --run 可观测`
3. **批量评估**: `/good-skills:evaluate-skill web-to-local-md --golden ./golden/web-to-local-md/`

**allowed-tools**: Read, Write, Glob, Grep, WebSearch, WebFetch, Bash(python *), TodoWrite

---

## 2. 适用场景与局限

### 适用场景

| 场景 | 说明 |
|------|------|
| Skill 变更后验证 | 改了 SKILL.md 或脚本，重跑评估确认输出质量不退化 |
| 新 Skill 首次验收 | 新 skill 写完后，跑评估确认基本质量达标 |
| 定期质量检查 | 配合 /loop 周期性评估 skill 输出，发现退化趋势 |
| 多版本对比 | 修改 SKILL.md 前后各跑一次，对比改进效果 |
| CI/CD 门禁 | 评估报告分数低于阈值时，阻止 skill 变更合入 |

### 局限性

| 局限 | 原因 | 影响 |
|------|------|------|
| 黑盒评估，无中间过程追踪 | Claude Code 内部 LLM 调用不可观测 | 无法评估"为什么 WebSearch 返回了合成摘要"，只能评估"最终输出是否包含真实 URL" |
| LLM-as-Judge 主观性 | 不同运行可能给出不同评分 | 同一份输出跑两次评估，分数可能有 ±1 的波动。不适合做精确阈值门禁 |
| 结构性断言非确定性 | Claude 读文件做判断，不是脚本正则匹配 | 对"是否包含某个 section"这类判断准确率高，但不如脚本 100% 确定 |
| 黄金参考维护成本 | 需要人工标注和更新参考输出 | 参考输出会过时（skill 改进后"更好"的输出可能与旧参考不同） |
| 非执行类 skill 不适用 | 纯对话型 skill（聊天、问答）没有文件输出 | evaluate-skill 只能评估有文件输出的 skill，无法评估纯对话质量 |
| --run 模式成本高 | 先跑目标 skill 再评估，双重 token 消耗 | 一个 topic 的 landscape + evaluate 可能消耗大量 token |
| 不替代人工审核 | LLM 判断可能有偏见 | 关键决策仍需人工确认，evaluate-skill 是辅助工具不是替代 |

**核心定位**: evaluate-skill 是**skill 质量改进的反馈工具**，不是**绝对质量裁判**。它的价值在于帮你快速发现 skill 输出中的结构缺失、内容偏差、降级失败等问题，加速 SKILL.md 的迭代优化。

---

## 3. 评估工作流

### 步骤 0：定位 SKILL.md + 输入文件

- 根据传入的 `skill-name`，在 `skills/` 目录下找到对应的 `SKILL.md`
- 如果指定了 `--input`，定位已有输出文件
- 如果指定了 `--golden`，扫描所有 `case-*` 子目录
- 如果指定了 `--run`，先执行目标 skill（需传入 skill 的参数）

创建 TodoWrite 清单：
```
- [ ] 步骤 0：定位 SKILL.md 和输入文件
- [ ] 步骤 1：通用结构断言
- [ ] 步骤 2：SKILL.md 合规性评估（LLM-as-Judge）
- [ ] 步骤 3：回归对比（可选）
- [ ] 步骤 4：聚合与生成评估报告
```

### 步骤 1：通用结构断言（确定性）

Claude 读输出文件，逐项检查通用断言清单。每项产出 ✅/❌ + 具体问题描述。

断言清单（见 references/structural-checks.md）：

| # | 断言项 | 检查方法 | 严重级别 |
|---|--------|---------|---------|
| 1 | 输出文件存在 | Glob 查找匹配文件 | 🔴 Critical |
| 2 | 文件非空（> 100 字符） | Read 文件，检查长度 | 🔴 Critical |
| 3 | Markdown 可解析（有标题、段落） | Read 文件，检查 `#` 标题和段落存在 | 🟡 Medium |
| 4 | 无未填充占位符 | 检查 `{PLACEHOLDER}`、`TODO`、`TBD` 不存在 | 🔴 Critical |
| 5 | URL 是文章级 | 检查 URL 路径深度 ≥ 1 | 🟡 Medium |
| 6 | 图片引用是本地路径（非 CDN） | 检查 `![](...)` 中无 `http://` 开头的链接 | 🟡 Medium |
| 7 | "链接暂缺"/"本期无更新" 占比 < 30% | 计算占位标记占比 | 🟡 Medium |
| 8 | 无 Markdown 语法损坏 | 检查表格行数与 `|` 分隔符对齐 | 🟢 Low |

### 步骤 2：SKILL.md 合规性评估（LLM-as-Judge）

Claude 读 SKILL.md + 读输出文件，对照评估输出是否符合 SKILL.md 定义。

评估维度（见 references/scoring-rubric.md）：

**维度 1：完整性（Completeness）— 1-5 分**

| 分数 | 定义 |
|------|------|
| 1 | 缺少 SKILL.md 要求的 3+ 个核心输出板块 |
| 2 | 缺少 2 个板块，或某些板块内容严重不足 |
| 3 | 所有板块存在，但 1-2 个板块内容较薄 |
| 4 | 所有板块完整，个别条目偏少 |
| 5 | 所有板块完整充实，条目数量符合 SKILL.md 预期 |

**维度 2：准确性（Accuracy）— 1-5 分**

| 分数 | 定义 |
|------|------|
| 1 | 严重事实错误或合成内容 |
| 2 | 有 1-2 处可验证的错误（URL 404、摘要与原文不符） |
| 3 | 绝大部分准确，个别条目需人工验证 |
| 4 | 准确，无明显错误 |
| 5 | 所有内容经验证正确 |

**维度 3：合规性（Compliance）— 1-5 分**

| 分数 | 定义 |
|------|------|
| 1 | 违反了 SKILL.md 中 3+ 条"常见错误"规则 |
| 2 | 违反了 1-2 条规则 |
| 3 | 基本合规，有 1 处轻微违规 |
| 4 | 完全合规 |
| 5 | 合规 + 主动遵循了降级策略和 URL 质量规则 |

**维度 4：可用性（Usability）— 1-5 分**

| 分数 | 定义 |
|------|------|
| 1 | 输出无法使用（文件损坏、格式乱） |
| 2 | 可勉强阅读，需大量人工修正 |
| 3 | 可正常阅读，部分内容需手动补充 |
| 4 | 可直接使用，偶有瑕疵 |
| 5 | 高质量输出，无需任何人工修正 |

**评估流程**: Claude **先列出判断依据**（具体指出哪条内容支持哪个分数），再给出每维度分数。避免"凭感觉打分"。

### 步骤 3：回归对比（可选，仅 --regress 或 --golden）

读取黄金参考输出，Claude 对比两者差异：

- **结构差异**: 缺少的板块、新增的板块
- **语义差异**: 内容准确性变化、信息密度变化
- **分类**: 改进点 / 退化点 / 不变点

不做数值 embedding similarity——用 Claude 自身做语义对比，与 skill 生态的纯 Claude 编排风格一致。

### 步骤 4：聚合与生成报告

- **单用例**: 生成一份评估报告 `evaluate-skill-report-<skill-name>-<日期>.md`
- **批量模式**: 生成综合报告，包含汇总板块（逐用例表格 + 共性问题分析 + 合并改进建议）

---

## 4. 批量评估（黄金数据集）

### 黄金数据集目录结构

```
golden/<skill-name>/           ← 每个 skill 一个目录
├── case-01/                   ← 一个测试用例
│   ├── input.yaml             ← 输入参数（URL、话题、选项等）
│   └── reference/             ← 参考输出（人工审核过的"好"输出）
│       ├── report.md
│       └── images/
├── case-02/
│   ├── input.yaml
│   └── reference/
│       ├── report.md
├── ...
└── case-20/
```

### input.yaml 格式

```yaml
skill: web-to-local-md
args: "https://javaguide.cn/ai/ --github-repo Snailclimb/JavaGuide --output-dir ./downloaded --render-mermaid"
description: "JavaGuide AI 章节下载测试"
priority: high    # high/medium/low — 决定报告中该用例的权重
```

### 综合报告额外板块

```markdown
## 总览

| 指标 | 值 |
|------|-----|
| 测试用例数 | 20 |
| 结构通过率 | 17/20 (85%) |
| 语义平均分 | 3.8 / 5 |
| 总体评级 | ⭐⭐⭐⭐ |

## 逐用例评分

| 用例 | 结构 | 语义 | 回归 | 关键问题 |
|------|------|------|------|---------|
| case-01 | ✅ | 4.2 | 改进 ✅ | 无 |
| case-03 | ❌ | 2.8 | 退化 ⚠️ | 图片路径未修正 |

## 共性问题（出现在 ≥3 个用例中）

1. VuePress SPA 懒加载内容缺失 — 7/20 用例受影响
2. 图片相对路径偶发错误 — 4/20 用例受影响

## 改进建议

1. 🔧 SKILL.md 步骤 7 补充：对 VuePress SPA 站点，强制使用 GitHub 源 .md 文件
2. 🔧 脚本修复：图片路径修正逻辑处理子目录嵌套
3. 📝 新增断言：Mermaid 渲染验证步骤
```

---

## 5. 改进建议生成规则

评估报告末尾的改进建议不是泛泛说"提高质量"，而是指向具体 SKILL.md 位置的修改建议：

| 问题类型 | 建议格式 |
|---------|---------|
| 结构缺失 | "建议在 SKILL.md 的步骤 N 中补充明确要求输出 `<板块名>`" |
| 合规违规 | "建议在 SKILL.md 的常见错误部分增加：`<具体规则描述>`" |
| 降级失败 | "建议在 SKILL.md 的降级策略部分补充 `<具体场景>` 的处理规则" |
| 信息质量 | "建议在 SKILL.md 的搜索策略部分调整 `<关键词>` 为 `<更精准的关键词>`" |

---

## 6. 输出结构（评估报告模板）

见 references/report-template.md。核心板块：

1. 总览（指标 + 评级）
2. 结构断言结果（逐项 ✅/❌）
3. SKILL.md 合规性评估（4 维度评分 + 判断依据）
4. 回归对比（可选）
5. 改进建议（指向 SKILL.md 具体位置的修改建议）

批量模式额外包含：
- 逐用例评分表
- 共性问题分析（出现在 ≥3 个用例中的问题）
- 合并改进建议

---

## 7. 文件结构

```
skills/evaluate-skill/
├── SKILL.md                    ← Skill 定义（工作流、参数、评估维度）
└── references/
    ├── structural-checks.md    ← 通用结构断言清单（8 项）
    ├── scoring-rubric.md       ← 4 维度评分标准（1-5 分制描述）
    └── report-template.md      ← 评估报告模板（单用例 + 批量综合）
```

不写 Python 评估脚本——纯 SKILL.md + references，与 learn-domain 风格一致。

---

## 8. 不做的事（YAGNI）

| 不做 | 原因 |
|------|------|
| ❌ Python 评估脚本 | 与 skill 生态风格不一致，方案 C 选择纯 Claude 编排 |
| ❌ Embedding similarity 回归 | 需要额外依赖和模型调用，Claude 语义对比已足够 |
| ❌ 自动 CI/CD 集成 | 这是 skill，不是 DevOps 工具；CI 集成是用户自己的事 |
| ❌ 评估历史记录/趋势追踪 | 过度设计，用户不需要一个"评估管理系统" |
| ❌ 多模型 Judge 对比 | 一个 Judge（Claude 自身）足够 |
| ❌ 自动修复 skill 输出 | 评估只发现问题，修复由用户手动改 SKILL.md |
| ❌ 评估纯对话型 skill | 没有文件输出就没法做结构断言，不适用 |
