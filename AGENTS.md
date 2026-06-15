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

将网站文档专区完整下载到本地 Markdown 文件，含图片和渲染后的 Mermaid 流程图，支持 Typora 等编辑器离线阅读。优先从 GitHub 下载源 `.md` 文件（质量远优于 HTML 转换），自动处理 VuePress/VitePress SPA 懒加载、Mermaid 图表渲染、CDN 图片下载和相对路径修正。

**调用**：`/good-skills:web-to-local-md <网站URL> --github-repo OWNER/REPO --output-dir DIR --render-mermaid`

**适用场景**：VuePress/VitePress 文档站、GitHub 开源项目文档、任何需要离线阅读的技术文档网站。

**前置条件**：Python 3；可选 `npm install -g @mermaid-js/mermaid-cli`（渲染 Mermaid 图表）

1. 创建 `skills/<技能名>/SKILL.md`（含 YAML frontmatter：name、description、allowed-tools）
2. 添加辅助文件（references/、scripts/）按需
3. 更新本文件加入新技能描述
4. 更新 README.md 加入新技能条目
