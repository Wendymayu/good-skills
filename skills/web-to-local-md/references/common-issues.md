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

**Symptom:** Curl/wget downloads show `Page height: 2551px` with content but no mermaid SVGs. Browser automation (Playwright) can't find rendered SVGs even after scrolling.

**Root cause:** VuePress is a Vue.js SPA. SSR provides a skeleton page. The Vue app hydrates client-side, but Mermaid lazy components (`mermaid-lazy-container`) only render via IntersectionObserver when visible. In headless browsers, IntersectionObserver often doesn't fire properly.

**Solution:** Don't try browser rendering. Instead:
1. Get source `.md` files from GitHub (contain `\`\`\`mermaid` code blocks)
2. Render mermaid locally with `mmdc` CLI tool

## Issue 3: Mermaid Rendering

**Symptom:** `mermaid-py` API returns 400 errors for Chinese text and `classDef` styles. `mmdc` not found in Python subprocess.

**Solutions:**
- **mermaid-py:** Uses Mermaid.ink online API which rejects advanced syntax (classDef, Chinese text, subgraph). Don't rely on it for production docs.
- **mmdc CLI:** Install via `npm install -g @mermaid-js/mermaid-cli`. On Windows, Python subprocess can't find it by name — use full path from `npm prefix -g` (typically `C:\Users\{user}\AppData\Roaming\npm\mmdc.cmd`).
- **Rendering command:** `mmdc -i input.mmd -o output.png -b white --scale 2`

## Issue 4: Image Relative Paths

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

## Issue 5: URL-Encoded Filenames

**Symptom:** One image URL contains `%20` (space): `sub-agent-task-splitting-context-isolation%20.png`. Local file saved as `sub-agent-task-splitting-context-isolation.png` (without `%20`). Markdown reference still has `%20`, so Typora can't find it.

**Solution:** After downloading images, scan all markdown files for `%20` in image references and replace with the actual local filename.

## Issue 6: Discovering All Pages

**Symptom:** How to find all page URLs from a documentation site?

**Methods:**
1. **Sidebar parsing:** Fetch the main page HTML, parse `<aside>` or sidebar `<ul>` for all `<a href>` links under the relevant section
2. **"Edit this page" links:** Each VuePress page has a link like `https://github.com/OWNER/REPO/edit/main/docs/ai/README.md` revealing the source path
3. **Sitemap:** Check `/sitemap.xml` or `/atom.xml`
4. **Manual:** If site structure is clear (e.g., `/ai/agent/`, `/ai/rag/`), enumerate known paths

## Issue 7: CDN Image URLs

**Symptom:** Images hosted on `oss.javaguide.cn` or similar CDN. Need to extract all image URLs from each page and download them.

**Pattern:** Most VuePress/VitePress sites use a CDN for images. Extract URLs matching `https://oss.example.com/...png|jpg|jpeg|gif|svg|webp` from each page's HTML or markdown, download to local `images/` directory, then replace remote URLs with local relative paths.
