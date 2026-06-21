# {SKILL_NAME} 评估报告

**评估日期**: {DATETIME}
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

---

# {SKILL_NAME} 综合评估报告（批量模式）

**评估日期**: {DATETIME}
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

---

*综合评估报告由 evaluate-skill skill 自动生成。核心定位：skill 质量改进的反馈工具，不是绝对质量裁判。*
