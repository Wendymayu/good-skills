# good-skills Roadmap

未来计划的工作项（backlog）。每项在实际开工时，再到 `docs/superpowers/specs/` 写详细设计文档。

## 状态说明

- 📌 **Planned** — 已记录需求，未开工
- 🚧 **In Progress** — 设计/开发中
- ✅ **Done** — 已完成

## 计划项

| 项目 | 状态 | 说明 |
|------|------|------|
| [evaluate-slides](#evaluate-slides) | 📌 Planned | 评估产出 PPT(.pptx) 的 skill |

---

## evaluate-slides

**需求**：当出现产出 PPT(.pptx) 的 skill 时，需要一套评估机制检验幻灯片质量（结构 + 视觉）。

**决策：新写独立 skill，不更新 evaluate-skill。**

- `evaluate-skill` 只适合 Markdown 输出（5/7 结构断言是 MD 专属：`#` 标题、`![]()` 图片语法、`|` 表格、` ``` ` 代码块）。
- PPT 是**二进制 + 强视觉**格式，需要**不同的评估机制**（不是"换一套断言"）：
  1. `python-pptx` 解析 slide 结构（标题 / bullet / 演讲者备注 / 图片 / 字号 / 页数）
  2. `libreoffice --headless` 渲染每页为 PNG
  3. 多模态模型逐页判视觉设计（版式 / 配色 / 字号 / 对齐 / 留白）
  4. PPT 专属断言清单（每页有标题、bullet ≤6、字号可读、主题一致…）
- **判据**：只需换结构检查项 → 更新 evaluate-skill；需要执行类机制（解析 + 渲染 + 看图）→ 新 skill。PPT 属后者。

**复用 evaluate-skill 约定**（保持生态一致）：黄金数据集布局、4（+1 视觉）维评分 + 星级门槛、报告模板 + `{PLACEHOLDER}` 约定、`--input` / `--run` / `--golden` 三模式、输出隔离到 `output/{skill}/{datetime}/`。

**依赖**：`python-pptx`、`libreoffice`（soffice）、多模态模型。

**开放问题**（开工时再定）：
- 环境是否有 libreoffice？若无 → 退化到纯 `python-pptx` 结构断言 + 文本 LLM-Judge，降级标注"未做视觉评估"。
- 视觉设计维是否纳入综合分（4+1=5 维，平均分计算需调整）。
- 大 PPT（30 页）渲染 + 逐页多模态判图的成本 / 采样策略。
- 是否支持旧 `.ppt` 格式，还是只 `.pptx`。

> 详细设计文档待开工时写入 `docs/superpowers/specs/`。
