# Good Skills — 编码智能体技能合集

面向多平台编码智能体的实用技能合集。

## 已有技能

### research-landscape（技术领域全景观测）

采集、综合、报告任意技术领域的最新进展。覆盖 7 大板块：行业周刊 → 国内信源 → 学术论文 → 标准&社区 → 大厂博客 → 工具动态。产出结构化中文报告，保留原文标题。

**调用**：`/good-skills:research-landscape <话题> [--since YYYY-MM-DD] [--deep]`

**支持任意话题**：可观测、评估、安全、微服务治理、Kubernetes、成本优化等，中文英文均可。

**前置条件**：`pip install requests python-dateutil`

## 新增技能流程

1. 创建 `skills/<技能名>/SKILL.md`（含 YAML frontmatter：name、description、allowed-tools）
2. 添加辅助文件（references/、scripts/）按需
3. 更新本文件加入新技能描述
4. 更新 README.md 加入新技能条目
