# web-to-local-md 黄金测试集设计

## 背景

web-to-local-md 技能用于将网站文档下载为本地 Markdown 文件（含图片），供离线阅读。每次更新技能后，需要评估输出质量是否退化。黄金测试集提供可量化的质量基线：约 50 条测试用例，每条来自不同知名网站，搭配参考输出文件。通过 evaluate-skill 的 `--golden` 批量模式进行评估。

## 目标

- 为 web-to-local-md 创建 ~50 条黄金测试用例
- 每条用例来自不同的知名网站（非小众站点）
- 中英文混合覆盖
- 以单页文章/文档为主（区段少量）
- 覆盖多种网站形态和技术栈
- 搭配参考输出文件，支持 evaluate-skill 回归对比

## 目录结构

黄金测试集存放在 `data/golden/web-to-local-md/`（不提交到 git，符合现有 `.gitignore` 规则）。

```
data/golden/web-to-local-md/
  README.md                           -- 数据集说明：如何使用、如何更新
  case-01/
    input.yaml                        -- 测试输入定义
    reference/                        -- 参考输出（web-to-local-md 生成的文件）
      *.md                            -- 下载的 Markdown 文件
      images/                         -- 下载的图片（如有）
  case-02/
    input.yaml
    reference/
      ...
  ... (共 ~50 个 case)
```

### input.yaml 格式

遵循 evaluate-skill `--golden` 模式，额外增加标签便于分析：

```yaml
skill: web-to-local-md
args: "https://vuejs.org/guide/introduction.html"
description: "Vue.js 官方文档 - VitePress SPA 站点单页下载测试"
site_type: vitepress       # 网站技术栈分类
language: en               # zh | en
priority: high             # high | medium | low
difficulty: easy            # easy | medium | hard
```

标签说明：
- `site_type`：网站技术栈（vitepress, vuepress, github-docs, sphinx, jekyll, hugo, plain-html, blog, wiki 等）
- `language`：页面主要语言
- `difficulty`：对 web-to-local-md 的处理难度预估

## URL 分类与覆盖策略

50 个用例按网站形态和技术栈分类：

| 分类 | 数量 | 代表性网站 | 测试重点 |
|------|------|-----------|---------|
| VuePress / VitePress SPA | 8 | Vue.js, Vite, Pinia, Vitest, React, Nuxt, Electron, Flutter | SPA 侧边栏发现、子目录路径 |
| GitHub 开源文档 | 6 | PostgreSQL, Redis, Django, FastAPI, Rust, Go | Strategy A（直接下载源 .md） |
| 纯 HTML 文档站 | 5 | MDN, Apache, Nginx, OpenSSL, W3C | Strategy B（HTML→MD 转换） |
| 云平台文档 | 4 | AWS, Azure, GCP, Alibaba Cloud | 复杂导航、多层目录 |
| 技术博客（单文章） | 8 | Anthropic, OpenAI, Google AI, InfoQ中文, 阿里云开发者社区, 腾讯云开发者社区, 掘金, 美团技术团队 | 单页文章、图片下载、代码块 |
| 中文知识库/社区 | 4 | 知乎专栏, CSDN, 博客园, SegmentFault | 中文内容、HTML→MD 转换 |
| Jekyll/Hugo 文档站 | 3 | Hugo docs, Jekyll docs, GitHub Pages | 静态站点、Markdown 源码 |
| AI/ML 平台文档 | 4 | PyTorch, TensorFlow, Hugging Face, LangChain | Sphinx/GitHub docs 混合 |
| Mermaid/图表类 | 4 | Mermaid docs, D3 docs, Apache ECharts, PlantUML | Mermaid 渲染、SVG 图片 |
| 其他/边缘场景 | 8 | Wikipedia, StackOverflow, GitHub Readme, Docker docs, Kubernetes docs, Terraform docs, Wikipedia 中文, Grafana docs | 各种边界情况 |

每个 URL 选择该网站的一个**单页文章/文档页面**（不是首页或导航页），路径深度 ≥ 2，页面有实质内容（文字 + 可能的图片/代码/图表）。

## 生成流程

### 步骤 1：URL 精选

根据分类策略，为每类挑选具体 URL：
- 每个来自不同知名网站
- 路径深度 ≥ 2
- 页面有实质内容（文字 ≥ 200 字，理想情况包含图片、代码块、表格等）
- 中英文混合

### 步骤 2：逐个运行 web-to-local-md

对每个 URL 通过 `/good-skills:web-to-local-md <url>` skill 调用运行，生成输出文件。

### 步骤 3：人工审核参考输出

检查每个输出：
- 文件非空（> 100 字符）
- Markdown 可读（有标题、段落）
- 图片路径是本地路径（非 CDN）
- 无占位符残留

### 步骤 4：创建 case-* 目录结构

将审核通过的输出移入 `case-NN/reference/`，编写对应的 `input.yaml`。

### 步骤 5：编写 README.md

说明数据集用途、如何用 evaluate-skill 评估、如何新增用例。

## 质量门控

每个参考输出必须通过 evaluate-skill 的 8 项结构断言（特别是 🔴 Critical 项），否则该用例标记为"待修复"而非正式纳入。

## 失败处理

如果一个 URL 的 web-to-local-md 运行失败或输出质量不合格：
- 记录失败原因（网站形态、具体错误）
- 将该 URL 作为"负例"保留在 input.yaml 中（`status: failed` 标签），reference/ 目录为空
- 有助于未来测试技能对困难网站的处理能力是否改善

input.yaml 失败用例格式：
```yaml
skill: web-to-local-md
args: "https://example.com/problematic-page"
description: "困难网站 - HTML 结构异常"
site_type: plain-html
language: en
priority: low
difficulty: hard
status: failed
failure_reason: "侧边栏发现 0 页面，单页 fallback 也因 CORS 限制失败"
```

## 维护与更新

### 日常使用

每次更新 web-to-local-md 后，运行：
```
/good-skills:evaluate-skill web-to-local-md --golden data/golden/web-to-local-md/
```

### 更新参考输出

只在版本升级时重新生成（如 v0.3.0 → v0.4.0），不要频繁更新——参考输出频繁变动会使回归对比失去意义。

### 新增用例

发现新的网站形态问题时，手动新增 `case-NN/`，编号从当前最大编号 +1 继续。

### 负例管理

定期重试 `status: failed` 的用例。成功后改为正式用例，补充 reference/ 输出。

## 存放位置

黄金测试集存放在 `data/golden/web-to-local-md/`，不提交到 git（符合现有 `.gitignore` 规则）。数据集本地维护，不共享到仓库。
