# Good Skills — 编码智能体技能合集

面向多平台编码智能体的实用技能合集。

## 已有技能

### research-landscape（技术领域全景观测）

采集、综合、报告任意技术领域的最新进展。覆盖 7 大板块：行业周刊 → 国内信源 → 学术论文 → 标准&社区 → 大厂博客 → 工具动态。产出结构化中文报告，保留原文标题。

**调用**：`/good-skills:research-landscape <话题> [--since YYYY-MM-DD] [--deep]`

**支持任意话题**：可观测、评估、安全、微服务治理、Kubernetes、成本优化等，中文英文均可。

**前置条件**：`pip install requests python-dateutil`

### learn-domain（技术领域学习指南）

为任意技术领域生成结构化学习指南，解决"不知道该学什么、按什么顺序学、哪些资源靠谱"的问题。产出中文 Markdown 指南，含概念依赖图、分级学习路径、资源推荐、实战项目建议和避坑指南。自动引用 research-landscape 报告的热点数据。

**调用**：`/good-skills:learn-domain <话题> [--level beginner|intermediate] [--project <项目描述>] [--lang zh|en]`

**支持任意话题**：可观测、AI Agent、Kubernetes、Rust、微服务等，中文英文均可。

**前置条件**：无（不依赖 Python 脚本，纯 WebSearch + Claude 知识）

### web-to-local-md（网站文档离线下载）

将网站文档专区完整下载到本地 Markdown 文件，含图片和渲染后的 Mermaid 流程图，支持 Typora 等编辑器离线阅读。双策略架构：优先从 GitHub 下载源 `.md` 文件（Strategy A，质量最优），无 GitHub 源时自动切换 Strategy B 直接提取 HTML 正文并转换为 Markdown。支持 VuePress/VitePress、GitHub 开源文档、SSR 文档站（AWS、Azure、GCP 等）和中文技术博客。

**调用**：`/good-skills:web-to-local-md <网站URL> [--github-repo OWNER/REPO] [--output-dir DIR] [--render-mermaid]`

**适用场景**：VuePress/VitePress 文档站、GitHub 开源项目文档、云平台文档、技术博客、任何需要离线阅读的技术文档网站。

**前置条件**：Python 3 + `pip install beautifulsoup4 markdownify requests`

### evaluate-skill（Skill 质量评估）

评估任意 good-skills skill 的输出质量。SKILL.md 本身就是评估 rubric——新增 skill 时评估自动生效，零额外代码。三层评估：通用结构断言 → SKILL.md 合规性（LLM-as-Judge）→ 可选回归对比。支持批量评估（黄金数据集）和综合报告。

**调用**：`/good-skills:evaluate-skill <skill-name> [--input <路径>] [--run <skill参数>] [--golden <路径>] [--regress <参考路径>] [--verbose]`

**适用场景**：Skill 变更后验证、新 Skill 首次验收、定期质量检查、多版本对比。

**局限**：黑盒评估无中间过程追踪；LLM-as-Judge 主观性 ±1 波动；非文件输出类 skill 不适用。

**前置条件**：无（纯 Claude 编排，不依赖 Python 评估脚本）

1. 创建 `skills/<技能名>/SKILL.md`（含 YAML frontmatter：name、description、allowed-tools）
2. 添加辅助文件（references/、scripts/）按需
3. 更新本文件加入新技能描述
4. 更新 README.md 加入新技能条目
