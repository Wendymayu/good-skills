# Common Issues and Solutions

Issues encountered during real-world website-to-markdown conversion, with proven solutions.

## Issue 1: HTML-to-Markdown Conversion Quality

**Symptom:** Converted markdown has empty `##` headers, corrupted image URLs (`![alt](paragraph text instead of URL)`), tables flattened into one long line, content duplication.

**Root cause:** VuePress/VitePress HTML is a complex SPA with nested components. Simple regex-based conversion can't handle:
- `<a class="header-anchor"><span>Title</span></a>` inside `<h2>` tags (removing anchor loses title)
- `<img>` tags inside `<h2>` headers (image becomes part of header)
- Vue-specific `<iconify-icon>` elements
- `<table>` → markdown table conversion
- Content appearing in both sidebar and main div

**Solution:** Use GitHub source markdown files directly. For open-source docs sites, the "Edit this page" link reveals the source path. Download raw `.md` from `https://raw.githubusercontent.com/OWNER/REPO/main/docs/PATH.md`.

**Fallback:** If GitHub source unavailable, use `BeautifulSoup` + `markdownify` with careful preprocessing:
1. Find `#markdown-content` div only (skip sidebar/footer)
2. Unwrap `<a class="header-anchor">` tags (keep text, remove anchor wrapper)
3. Move `<img>` tags out of headers (insert as separate `<p>` after header)
4. Remove `<iconify-icon>` and page metadata divs
5. Strip VuePress frontmatter (`---` blocks)

## Issue 2: VuePress SPA Lazy Content

**Symptom:** Curl/wget downloads show `Page height: 2551px` with content but no rendered diagrams. Browser automation (Playwright) can't find rendered SVGs even after scrolling.

**Root cause:** VuePress is a Vue.js SPA. SSR provides a skeleton page. The Vue app hydrates client-side, but lazy components only render via IntersectionObserver when visible. In headless browsers, IntersectionObserver often doesn't fire properly.

**Solution:** Get source `.md` files from GitHub. Mermaid code blocks are preserved as-is in the downloaded Markdown — they render natively in editors like Typora and VS Code that support Mermaid preview.

## Issue 3: Image Relative Paths

**Symptom:** Markdown file at `docs/agent/prompt-engineering.md` references `images/llm-context-window.png`. Typora resolves this relative to the markdown file's directory, looking for `docs/agent/images/` — wrong.

**Solution:** All markdown files in subdirectories must use `../images/` (one level up). The root-level overview file uses `images/` (same level).

Directory layout:
```
output/
├── overview.md          → images/xxx (same level, OK)
├── images/              → all PNG/SVG files
├── agent/
│   └── prompt.md        → ../images/xxx (up one level, OK)
├── rag/
│   └── rag-basis.md     → ../images/xxx (up one level, OK)
```

## Issue 4: URL-Encoded Filenames

**Symptom:** One image URL contains `%20` (space): `sub-agent-task-splitting-context-isolation%20.png`. Local file saved as `sub-agent-task-splitting-context-isolation.png` (without `%20`). Markdown reference still has `%20`, so Typora can't find it.

**Solution:** After downloading images, scan all markdown files for `%20` in image references and replace with the actual local filename.

## Issue 5: Discovering All Pages

**Symptom:** How to find all page URLs from a documentation site?

**Methods:**
1. **Sidebar parsing:** Fetch the main page HTML, parse `<aside>` or sidebar `<ul>` for all `<a href>` links under the relevant section
2. **"Edit this page" links:** Each VuePress page has a link like `https://github.com/OWNER/REPO/edit/main/docs/ai/README.md` revealing the source path
3. **Sitemap:** Check `/sitemap.xml` or `/atom.xml`
4. **Manual:** If site structure is clear (e.g., `/ai/agent/`, `/ai/rag/`), enumerate known paths

## Issue 6: CDN Image URLs

**Symptom:** Images hosted on `oss.javaguide.cn` or similar CDN. Need to extract all image URLs from each page and download them.

**Pattern:** Most VuePress/VitePress sites use a CDN for images. Extract URLs matching any `https://...png|jpg|jpeg|gif|svg|webp` from each page's HTML or markdown, download to local `images/` directory, then replace remote URLs with local relative paths. The script now handles any remote image URL (not just oss.* domains).

## Issue 7: Strategy B — Direct HTML Extraction

**When it applies:** Sidebar discovers 0 pages and no `--github-repo` is provided.

**How it works:**
1. Fetch URL HTML with enhanced headers (Mozilla UA, Accept-Language, Connection)
2. Find main content container via CSS selector heuristics (article, main, [role="main"], known blog IDs)
3. Strip noise (nav, header, footer, aside, ads, scripts, styles)
4. Convert to Markdown with markdownify (ATX headings, dash bullets)
5. Localize remote image URLs to `images/` directory

**Known limitations:**
- Pure SPA sites (Go Tour, Anthropic Docs, InfoQ) return empty HTML shells → Strategy B cannot extract content
- Anti-bot sites (知乎 403, CSDN 521) block automated requests
- Some sites serve SSR HTML but content is minimal (<200 chars of actual text) → treated as empty

**Content container selectors tried (in priority order):**
- `article`, `[role="main"]`, `main`
- `.article-content`, `.post-content`, `.main-content`, `.content-body`
- `.documentation`, `.doc-content`, `#content`, `#main-content`
- `#cnblogs_post_body` (博客园), `.article__content` (SegmentFault)
- `#article-content` (阿里云), `.topic-richtext` (知乎)
- `.awsui-text-container` (AWS docs)
- Fallback: `<body>` with noise removed (nav/header/footer/aside + class/id-based noise stripping with word-boundary anchors)
