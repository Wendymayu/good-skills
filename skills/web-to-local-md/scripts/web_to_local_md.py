#!/usr/bin/env python3
"""
web_to_local_md.py - Download a website section to local markdown with images

Encapsulates the full process:
1. Discover pages from site sidebar
2. Download source .md from GitHub (preferred) or convert HTML
3. Download all images from CDN
4. Fix relative image paths

Usage:
  python web_to_local_md.py --url "https://javaguide.cn/ai/" --github-repo "Snailclimb/JavaGuide" --output-dir "./downloaded"
"""

import argparse
import os
import re
import sys
import json
import urllib.parse
import requests as req_lib
from html.parser import HTMLParser


# ─── HTTP Fetching ───

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def fetch_url(url, headers=None, timeout=15):
    """Fetch a URL with enhanced headers and error handling.

    Returns HTML text on success, None on failure (404, 403, timeout, etc).
    """
    h = headers or DEFAULT_HEADERS
    try:
        r = req_lib.get(url, headers=h, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return r.text
        print(f"  HTTP {r.status_code} for {url}")
        return None
    except req_lib.exceptions.Timeout:
        print(f"  Timeout fetching {url}")
        return None
    except req_lib.exceptions.RequestException as e:
        print(f"  Request error: {e}")
        return None


# ─── Page Discovery ───

class SidebarParser(HTMLParser):
    """Parse VuePress sidebar to discover all page links."""
    def __init__(self, base_url, section_prefix):
        super().__init__()
        self.base_url = base_url
        self.section_prefix = section_prefix
        self.pages = []
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.current_href = value

    def handle_data(self, data):
        if self.current_href and self.current_href.startswith(self.section_prefix):
            title = data.strip()
            if title:
                self.pages.append({
                    'url': self.base_url + self.current_href,
                    'path': self.current_href,
                    'title': title,
                })

    def handle_endtag(self, tag):
        if tag == 'a':
            self.current_href = None


def discover_pages(base_url, section_prefix, html_content):
    """Discover all page links from sidebar HTML."""
    parser = SidebarParser(base_url, section_prefix)
    parser.feed(html_content)
    return parser.pages


# ─── GitHub Source Download ───

def download_github_md(github_repo, source_path, save_path, branch='main'):
    """Download a markdown file from GitHub raw URL."""
    url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/{source_path}"
    try:
        r = req_lib.get(url, headers=DEFAULT_HEADERS, timeout=30)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return r.content.decode('utf-8', errors='ignore')
        print(f"  GitHub download failed: HTTP {r.status_code}")
        return None
    except req_lib.exceptions.RequestException as e:
        print(f"  GitHub download failed: {e}")
        return None


def strip_frontmatter(content):
    """Remove YAML frontmatter from markdown content."""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            return content[end + 3:].strip()
    return content


def extract_page_metadata(html):
    """Extract page title and publication date from HTML before noise stripping.

    Returns (title, date_str):
    - title: str or None — page H1 or <title> text
    - date_str: str or None — publication date in YYYY-MM-DD format
    """
    from bs4 import BeautifulSoup

    if not html:
        return (None, None)

    soup = BeautifulSoup(html, 'html.parser')

    # ── Title extraction ──
    title = None
    # Priority 1: <h1> inside the main content area (not in nav/header/footer)
    for h1 in soup.find_all('h1'):
        parent_tags = [p.name for p in h1.parents if p.name]
        # Skip if h1 is inside nav/header/footer/aside
        if any(t in ('nav', 'header', 'footer', 'aside') for t in parent_tags):
            continue
        title = h1.get_text(strip=True)
        if title:
            break

    # Priority 2: <title> element (fallback, often includes site name)
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            raw = title_tag.get_text(strip=True)
            # Remove common suffixes like " | Site Name" or " - Site Name"
            for sep in (' | ', ' - ', ' – ', ' — ', ' :: '):
                if sep in raw:
                    raw = raw.split(sep)[0]
            title = raw.strip()

    # ── Date extraction ──
    date_str = None
    date_pattern = r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})'

    # Priority 1: <meta property="article:published_time">
    meta_date = soup.find('meta', attrs={'property': 'article:published_time'})
    if meta_date and meta_date.get('content'):
        m = re.search(date_pattern, meta_date['content'])
        if m:
            date_str = m.group(1).replace('/', '-').replace('.', '-')

    # Priority 2: <meta name="date"> or <meta name="pubdate">
    if not date_str:
        for meta_name in ('date', 'pubdate', 'publish-date', 'article:date'):
            meta = soup.find('meta', attrs={'name': meta_name})
            if meta and meta.get('content'):
                m = re.search(date_pattern, meta['content'])
                if m:
                    date_str = m.group(1).replace('/', '-').replace('.', '-')
                    break

    # Priority 3: <time datetime="...">
    if not date_str:
        time_tag = soup.find('time', attrs={'datetime': True})
        if time_tag:
            m = re.search(date_pattern, time_tag['datetime'])
            if m:
                date_str = m.group(1).replace('/', '-').replace('.', '-')
            else:
                m = re.search(date_pattern, time_tag.get_text(strip=True))
                if m:
                    date_str = m.group(1).replace('/', '-').replace('.', '-')

    # Priority 4: <time> without datetime attribute (text contains date)
    if not date_str:
        for time_tag in soup.find_all('time'):
            m = re.search(date_pattern, time_tag.get_text(strip=True))
            if m:
                date_str = m.group(1).replace('/', '-').replace('.', '-')
                break

    # Priority 5: Common date class names (expanded list)
    date_classes = [
        'post-date', 'pub-date', 'article-date', 'date',
        'post-meta', 'article-meta', 'entry-date',
        'publish-date', 'pubtime', 'post-time',
        'pubdate', 'post-publish-date', 'meta-date',
        'updated', 'post-updated', 'article-updated',
        'last-updated', 'modify-date', 'created-at',
        'published-at', 'post-created', 'post-modified',
        'date-published', 'date-posted', 'date-updated',
    ]
    if not date_str:
        for cls in date_classes:
            el = soup.find(class_=cls)
            if el:
                m = re.search(date_pattern, el.get_text(strip=True))
                if m:
                    date_str = m.group(1).replace('/', '-').replace('.', '-')
                    break

    # Priority 6: data-date attribute on any element
    if not date_str:
        for el in soup.find_all(attrs={'data-date': True}):
            m = re.search(date_pattern, el['data-date'])
            if m:
                date_str = m.group(1).replace('/', '-').replace('.', '-')
                break

    # Priority 7: Any visible date text near page top (scan first 20 text nodes)
    if not date_str:
        for el in soup.find_all(['span', 'small', 'p', 'div']):
            text = el.get_text(strip=True)
            # Only consider short text nodes that look like dates
            if len(text) < 50:
                m = re.search(date_pattern, text)
                if m:
                    date_str = m.group(1).replace('/', '-').replace('.', '-')
                    break

    return (title, date_str)


def inject_metadata(markdown_text, title, date_str):
    """Inject H1 title and <small> publication date into markdown if missing.

    Order: # H1 title first, then <small> date below it.
    If the markdown already has a # H1 line, skip title injection.
    If it already has a <small> date line, skip date injection.
    Date is NEVER placed before H1 — if no H1 and no title, skip date too.
    """
    lines = markdown_text.split('\n')

    has_h1 = any(line.startswith('# ') and not line.startswith('## ') for line in lines[:5])
    has_date = any('<small style="color:gray">' in line for line in lines[:10])

    prefix_lines = []
    if title and not has_h1:
        prefix_lines.append(f'# {title}')
        prefix_lines.append('')
    # Only inject date if we have an H1 (either existing or newly injected)
    if date_str and not has_date:
        # Ensure there's an H1 before injecting date
        will_have_h1 = has_h1 or (title and not has_h1)
        if will_have_h1:
            prefix_lines.append(f'<small style="color:gray">{date_str}</small>')
            prefix_lines.append('')

    if prefix_lines:
        return '\n'.join(prefix_lines + lines)

    return markdown_text


# ─── Content Extraction (Strategy B) ───

def extract_main_content(html):
    """Extract the main content from HTML using CSS selector heuristics.

    Returns the inner HTML of the best content container found,
    or None if no meaningful content can be extracted.
    Thresholds: HTML input must be >=500 chars; content text must be >=200 chars.
    200 chars ≈ 2-3 paragraphs, filters out nav/sidebar/teaser snippets.
    """
    from bs4 import BeautifulSoup
    import copy

    if not html or len(html) < 500:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # Priority-ordered selector chain for known content containers
    # Each selector is tried in order; when multiple elements match a selector,
    # the one with the longest text content is preferred (avoids sidebar teasers).
    # Note: .content is intentionally omitted — too generic, matches sidebar divs.
    selectors = [
        # Semantic HTML5
        'article',
        '[role="main"]',
        'main',
        # Common doc site patterns
        '.article-content',
        '.post-content',
        '.main-content',
        '.content-body',
        '.documentation',
        '.doc-content',
        '#content',
        '#main-content',
        # Chinese tech blog patterns
        '#cnblogs_post_body',          # 博客园
        '.article__content',           # SegmentFault
        '#article-content',            # 阿里云开发者社区
        '.topic-richtext',             # 知乎专栏
        '.Post-RichTextContainer',     # 知乎专栏新版
        # Cloud/docs patterns
        '.awsui-text-container',       # AWS docs
    ]

    for sel in selectors:
        elements = soup.select(sel)
        if elements:
            # Prefer the element with the most content text
            best = max(elements, key=lambda el: len(el.get_text(strip=True)))
            text = best.get_text(strip=True)
            # Must have substantial content (>200 chars of actual text)
            if len(text) > 200:
                return str(best)

    # Fallback: use <body> copy (avoid mutating the original soup) with noise removal
    body = soup.find('body')
    if body:
        # Work on a copy to avoid irreversible decompose() mutations
        body_copy = copy.copy(body)
        # Remove known noise elements
        for tag in body_copy.find_all(['nav', 'header', 'footer', 'aside']):
            tag.decompose()
        # Use word-boundary anchors to avoid overstripping (e.g. "content-header" won't match \bheader\b)
        for tag in body_copy.find_all(class_=re.compile(r'\bsidebar\b|\bmenu\b|\bnav\b|\bbreadcrumb\b|\bcookie\b|\bad\b|\bbanner\b|\bpromo\b|\bshare\b|\bcomment\b|\bfooter\b|\bheader\b')):
            tag.decompose()
        for tag in body_copy.find_all(id=re.compile(r'\bsidebar\b|\bnav\b|\bheader\b|\bfooter\b|\bmenu\b|\bcomment\b')):
            tag.decompose()

        text = body_copy.get_text(strip=True)
        if len(text) > 200:
            return str(body_copy)

    return None


NOISE_CLASSES = [
    'sidebar', 'menu', 'nav', 'navigation', 'breadcrumb',
    'cookie', 'cookie-banner', 'ad', 'ads', 'advertisement',
    'banner', 'promo', 'promotion', 'share', 'social-share',
    'comment', 'comments', 'disqus', 'footer', 'header',
    'toc', 'table-of-contents', 'related', 'recommend',
    'tags', 'tag-list', 'pagination', 'pager',
    # Copy/clipboard buttons
    'copy', 'copy-button', 'copy-code-btn', 'copy-action',
    # Promotional content
    'sponsor', 'affiliate', 'newsletter', 'subscribe', 'cta',
    'callout', 'tip-box', 'download-app',
    # Author/metadata noise
    'author-info', 'author-card', 'post-meta-author',
    'reading-time', 'view-count',
]

NOISE_IDS = [
    'sidebar', 'nav', 'navigation', 'header', 'footer',
    'menu', 'comments', 'comment', 'disqus_thread',
    'breadcrumb', 'toc',
]

def strip_noise(html):
    """Remove navigation, sidebars, ads, scripts, styles from HTML content.

    Preserves <pre>, <code>, <table>, <img>, and semantic content tags.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script/style tags entirely
    for tag in soup.find_all(['script', 'style', 'noscript']):
        tag.decompose()

    # Remove semantic noise tags
    for tag in soup.find_all(['nav', 'header', 'footer', 'aside']):
        tag.decompose()

    # Remove elements by noise class names (BeautifulSoup accepts list for class_)
    for tag in soup.find_all(class_=NOISE_CLASSES):
        tag.decompose()

    # Remove elements by noise IDs (id parameter needs regex for list matching)
    noise_id_pattern = '|'.join(NOISE_IDS)
    for tag in soup.find_all(id=re.compile(noise_id_pattern)):
        tag.decompose()

    return str(soup)


def unwrap_anchor_headers(html):
    """Unwrap <a class="header-anchor"> or <a class="anchor"> inside headings.

    VuePress/VitePress headers use <h2><a class="header-anchor"><span>Title</span></a></h2>.
    Removing the <a> wrapper keeps the inner text clean, preventing
    markdownify from producing ## [Title](#title) artifacts.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')

    for a_tag in soup.find_all('a', class_=re.compile(r'header-anchor|anchor')):
        # Only unwrap if parent is a heading tag
        if a_tag.parent and a_tag.parent.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            a_tag.unwrap()

    return str(soup)


def clean_html_artifacts(markdown_text):
    """Remove text-level HTML artifacts from markdownified content.

    Handles:
    - "Copy" / "复制代码" / "Copied!" standalone lines (code block buttons)
    - Anchor links in headings: ## [Title](#title) → ## Title
    - Empty table separator rows: |  |  |  |  | → remove
    """
    # Remove standalone Copy/Copied/复制代码 lines
    markdown_text = re.sub(r'^\s*(Copy|Copied!|复制代码|复制)\s*$', '', markdown_text, flags=re.MULTILINE)

    # Clean anchor links in headings: ## [Title](#title) → ## Title
    markdown_text = re.sub(
        r'^(#{1,6})\s+\[([^\]]+)\]\([^)]*\)',
        r'\1 \2',
        markdown_text,
        flags=re.MULTILINE
    )

    # Remove empty table separator rows (all cells empty or just whitespace)
    markdown_text = re.sub(r'^\s*\|\s*(?:\s*\|\s*)+\s*$', '', markdown_text, flags=re.MULTILINE)

    return markdown_text


def html_to_markdown(html):
    """Convert HTML content to Markdown using extract + strip_noise + markdownify.

    Pipeline: extract_main → strip_noise → unwrap_anchor_headers → md_conv
              → clean_html_artifacts → inject_metadata → whitespace cleanup

    Returns (markdown_text, title, date_str, nested_images) tuple on success,
    (None, None, None, set()) if content is too short/empty.
    """
    from markdownify import markdownify as md_conv

    # Step 0: Extract page metadata from original HTML (before noise stripping)
    title, date_str = extract_page_metadata(html)

    # Step 1: Extract main content
    content_html = extract_main_content(html)
    if content_html is None:
        return (None, None, None, set())

    # Step 1a: Extract ALL image src URLs from content HTML (before noise stripping)
    # This catches deeply nested images (e.g. WordPress <table><td><figure><img>)
    nested_images = extract_images_from_html(content_html)

    # Step 2: Strip noise
    clean_html = strip_noise(content_html)

    # Step 3: Unwrap anchor-only headers (before markdownify)
    clean_html = unwrap_anchor_headers(clean_html)

    # Step 4: Convert to Markdown
    markdown_text = md_conv(clean_html, heading_style="ATX", bullets="-")

    # Step 5: Clean HTML artifacts (after markdownify)
    markdown_text = clean_html_artifacts(markdown_text)

    # Step 6: Inject H1 title and publication date if missing
    markdown_text = inject_metadata(markdown_text, title, date_str)

    # Step 7: Clean up excessive whitespace
    markdown_text = re.sub(r'\n{4,}', '\n\n\n', markdown_text)
    markdown_text = re.sub(r' +\n', '\n', markdown_text)

    # Step 8: Check minimum content length
    plain_text = re.sub(r'[#*\[\]\(\)!>`\n]', '', markdown_text)
    if len(plain_text.strip()) < 200:
        return (None, None, None, set())

    return (markdown_text.strip(), title, date_str, nested_images)


# ─── Image Handling ───

def extract_image_urls(content):
    """Extract all remote image URLs from content (Markdown or HTML).

    Handles standard CDN URLs, byteimg signed URLs (with ~tplv in path),
    and Next.js /_next/image proxy URLs with encoded nested URLs.
    """
    urls = set()
    # Standard CDN URLs — expanded with .awebp and ~ in path/filename
    pattern = r'https://[a-zA-Z0-9._/~-]+/[a-zA-Z0-9._~-]+\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)(?:\?[a-zA-Z0-9=%&_.+-]*)?'
    for url in re.findall(pattern, content):
        urls.add(url)

    # Byteimg signed URLs: xxx~tplv-xxx.awebp?x-expires=...&x-signature=...
    # The ~tplv suffix makes the filename part longer than [a-zA-Z0-9._~-]+ can handle
    # because it includes URL-encoded segments. Use a broader pattern.
    byteimg_pattern = r'https://[a-zA-Z0-9._/~-]+/[a-zA-Z0-9._~%-]+\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)(?:~[a-zA-Z0-9._%-]+)?(?:\?[a-zA-Z0-9=%&_.+~-]*)?'
    for url in re.findall(byteimg_pattern, content):
        urls.add(url)

    # Next.js /_next/image proxy: decode nested url parameter
    next_pattern = r'/_next/image\?url=(https?%3A%2F%2F[a-zA-Z0-9._/~%-]+(?:\.[a-zA-Z0-9._~-]+(?:\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)))?[a-zA-Z0-9./%~_-]*)(?:&[^"\'\\)]*)?'
    for encoded_url in re.findall(next_pattern, content):
        real_url = urllib.parse.unquote(encoded_url)
        urls.add(real_url)

    return urls


def download_image(url, save_path):
    """Download an image from URL to local path."""
    try:
        r = req_lib.get(url, headers=DEFAULT_HEADERS, timeout=30)
        if r.status_code == 200 and len(r.content) > 100:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return len(r.content)
        return 0
    except req_lib.exceptions.RequestException as e:
        print(f"    Image download failed: {e}")
        return 0


def get_image_prefix(subdir):
    """Calculate relative path prefix from a subdirectory to the images/ directory.

    For root-level files: images/
    For one level deep (e.g. 'ai'): ../images/
    For two levels deep (e.g. 'ai/llm-basis'): ../../images/
    """
    if not subdir:
        return 'images/'
    depth = subdir.count('/')
    return '../' * (depth + 1) + 'images/'

def fix_image_paths(content, subdir):
    """Replace remote image URLs with local relative paths.

    Handles standard CDN URLs, byteimg signed URLs, and Next.js proxy URLs.
    Uses human-readable filenames where possible (strips hash prefix,
    removes ~tplv suffix, cleans up query params).
    """
    prefix = get_image_prefix(subdir)

    def make_readable_filename(url):
        """Generate a human-readable filename from an image URL.

        Handles:
        - Standard URLs: use basename (e.g. 'anthropic-evals-1.png')
        - Hash-prefixed URLs: strip leading hash (e.g. 'bd42e7b2f-4584x2834.png' → '4584x2834.png')
        - Byteimg signed URLs: strip ~tplv suffix (e.g. 'xxx~tplv-73owjymdk6.awebp' → 'xxx.awebp')
        - Query params: stripped (filename = basename only)
        """
        raw = os.path.basename(url.split('?')[0])
        # Strip ~tplv suffix from byteimg filenames
        tilde_idx = raw.find('~tplv')
        if tilde_idx > 0:
            raw = raw[:tilde_idx]
        # Strip leading hash prefix (common in Next.js CDN): 8+ hex chars followed by -
        m = re.match(r'^[a-f0-9]{8,}-', raw)
        if m:
            raw = raw[len(m.group(0)):]
        # Clean up remaining % encodings
        raw = raw.replace('%20', '')
        return raw

    def replace_url(match):
        url = match.group(0)
        filename = make_readable_filename(url)
        return prefix + filename

    # Replace standard remote image URLs (any domain)
    content = re.sub(
        r'https://[a-zA-Z0-9._/~-]+/[a-zA-Z0-9._~-]+\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)(?:\?[a-zA-Z0-9=%&_.+-]*)?',
        replace_url, content
    )

    # Replace byteimg signed URLs (broader pattern for ~tplv suffix)
    def replace_byteimg_url(match):
        url = match.group(0)
        filename = make_readable_filename(url)
        return prefix + filename

    content = re.sub(
        r'https://[a-zA-Z0-9._/~-]+/[a-zA-Z0-9._~%-]+\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)(?:~[a-zA-Z0-9._%-]+)?(?:\?[a-zA-Z0-9=%&_.+~-]*)?',
        replace_byteimg_url, content
    )

    # Replace Next.js /_next/image proxy URLs — decode and get real image URL, then localize
    def replace_next_url(match):
        encoded_url = match.group(1)
        real_url = urllib.parse.unquote(encoded_url)
        filename = make_readable_filename(real_url)
        return prefix + filename

    content = re.sub(
        r'/_next/image\?url=(https?%3A%2F%2F[a-zA-Z0-9._/~%-]+(?:\.[a-zA-Z0-9._~-]+(?:\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)))?[a-zA-Z0-9./%~_-]*)(?:&[^"\'\\)]*)?',
        replace_next_url, content
    )

    # Fix %20 in filenames
    content = content.replace('%20.png', '.png')
    content = content.replace('%20.svg', '.svg')
    content = content.replace('%20.jpg', '.jpg')
    content = content.replace('%20.jpeg', '.jpeg')
    content = content.replace('%20.awebp', '.awebp')
    content = content.replace('%20.webp', '.webp')
    return content


def fill_image_alt_text(content):
    """Fill empty or generic image alt text with descriptive text from filename.

    Handles:
    - ![](local_path) → ![filename-based-text](local_path)
    - ![image.png](local_path) → ![filename-based-text](local_path)
    Does NOT overwrite existing descriptive alt text.
    Also cleans up alt text that contains URL garbage (tplv, signatures, etc).
    """
    def derive_alt(path):
        """Derive alt text from image filename: strip extension, replace -/_ with spaces."""
        basename = os.path.basename(path)
        # Remove extension
        name = re.sub(r'\.(?:png|jpg|jpeg|gif|svg|webp|avif|awebp)$', '', basename, flags=re.IGNORECASE)
        # Replace - and _ with spaces
        name = name.replace('-', ' ').replace('_', ' ')
        # Capitalize first letter
        if name:
            name = name[0].upper() + name[1:]
        return name or 'image'

    # Fill empty alt text: ![](path) → ![derived](path)
    def replace_empty_alt(match):
        path = match.group(1)
        alt = derive_alt(path)
        return f'![{alt}]({path})'

    content = re.sub(r'!\[\]\(([^)]+)\)', replace_empty_alt, content)

    # Fill generic alt text: ![image.png](path), ![image](path), ![图片](path)
    generic_alts = ['image.png', 'image.jpg', 'image.jpeg', 'image.svg', 'image.webp', 'image', '图片']
    def replace_generic_alt(match):
        alt = match.group(1)
        path = match.group(2)
        if alt in generic_alts:
            new_alt = derive_alt(path)
            return f'![{new_alt}]({path})'
        return match.group(0)

    content = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', replace_generic_alt, content)

    # Clean alt text containing URL garbage (tplv, x-signature, hash strings, etc.)
    # Pattern: ![text-containing-url-gunk](path) → ![clean-derived-text](path)
    def clean_garbage_alt(match):
        alt = match.group(1)
        path = match.group(2)
        # If alt contains tplv, signature, hash, or URL params → replace with derived
        if re.search(r'tplv|x-signature|x-expires|[a-f0-9]{16,}|~', alt):
            new_alt = derive_alt(path)
            return f'![{new_alt}]({path})'
        return match.group(0)

    content = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', clean_garbage_alt, content)

    return content


def extract_images_from_html(html):
    """Recursively extract all <img> src URLs from HTML content.

    Handles deeply nested structures like WordPress
    <table><td><figure><img> where <img> is buried inside
    multiple container elements. Returns a set of src URLs.
    """
    from bs4 import BeautifulSoup

    if not html:
        return set()

    soup = BeautifulSoup(html, 'html.parser')
    urls = set()
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-original')
        if src and src.startswith('http'):
            urls.add(src)
    return urls


# ─── Main Pipeline ───

def main():
    parser = argparse.ArgumentParser(description='Download website to local markdown')
    parser.add_argument('--url', required=True, help='Website section URL (e.g. https://javaguide.cn/ai/)')
    parser.add_argument('--github-repo', default=None, help='GitHub repo with source .md files (e.g. Snailclimb/JavaGuide)')
    parser.add_argument('--github-branch', default='main', help='GitHub branch for source files (default: main)')
    parser.add_argument('--github-docs-path', default='docs', help='Path prefix in GitHub repo for doc files (default: docs)')
    parser.add_argument('--output-dir', required=True, help='Local output directory')
    parser.add_argument('--pages', default=None, help='JSON file with page definitions [{subdir, filename, path, title}]')
    args = parser.parse_args()

    output_dir = args.output_dir
    img_dir = os.path.join(output_dir, 'images')
    os.makedirs(img_dir, exist_ok=True)

    print("=" * 60)
    print("Web to Local Markdown Converter")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"Output: {output_dir}")
    print(f"GitHub repo: {args.github_repo}")
    print()

    # Load page definitions
    strategy_b_used = False
    all_remote_images = set()
    if args.pages:
        with open(args.pages, 'r', encoding='utf-8') as f:
            pages = json.load(f)
    else:
        # Discover pages from the site
        print("Step 1: Discovering pages from site sidebar...")
        html = fetch_url(args.url)
        if html is None:
            print(f"Failed to fetch site: {args.url}")
            sys.exit(1)

        # Parse section prefix from URL
        section_prefix = args.url.replace('https://', '/').replace('http://', '/').split('?')[0]
        if not section_prefix.endswith('/'):
            section_prefix += '/'
        base_url = args.url.split('/')[0] + '://' + '/'.join(args.url.split('/')[1:3])

        pages = discover_pages(base_url, section_prefix, html)
        print(f"  Found {len(pages)} pages")

        strategy_b_used = False

        # Fallback A: single-page GitHub source download
        if len(pages) == 0 and args.github_repo:
            # Handles both:
            #   https://javaguide.cn/ai/llm-basis/llm-operation-mechanism.html
            #   https://pinia.vuejs.org/core-concepts/  (trailing-slash → core-concepts.md)
            url_path = args.url.replace('https://', '').replace('http://', '').split('?')[0]
            # Remove domain, keep path
            domain = url_path.split('/')[0]
            page_path = '/' + '/'.join(url_path.split('/')[1:])
            # Strip trailing slash (VitePress /core-concepts/ → /core-concepts)
            page_path = page_path.rstrip('/')
            # Convert .html to .md path; also append .md if path has no extension (VitePress-style)
            md_path = page_path.replace('.html', '.md')
            if not md_path.endswith('.md'):
                md_path += '.md'
            # Derive subdir and filename from path
            path_parts = md_path.strip('/').split('/')
            if len(path_parts) > 1:
                subdir = '/'.join(path_parts[:-1])
                filename = path_parts[-1].replace('.md', '')
            else:
                subdir = ''
                filename = path_parts[-1].replace('.md', '')
            pages = [{'subdir': subdir, 'filename': filename, 'path': md_path, 'title': filename}]
            print(f"  Fallback A: single-page GitHub download → {md_path}")

        # Fallback B: direct HTML extraction (Strategy B) when no sidebar pages and no GitHub source
        if len(pages) == 0 and not args.github_repo:
            print("  No sidebar pages found. Trying Strategy B: direct HTML extraction...")
            strategy_b_md, _, _, nested_imgs = html_to_markdown(html)
            if strategy_b_md:
                filename = 'index'
                md_save_path = os.path.join(output_dir, f"{filename}.md")
                strategy_b_used = True
                all_remote_images.update(extract_image_urls(strategy_b_md))
                all_remote_images.update(nested_imgs)
                strategy_b_md = fix_image_paths(strategy_b_md, '')
                strategy_b_md = fill_image_alt_text(strategy_b_md)
                with open(md_save_path, 'w', encoding='utf-8') as f:
                    f.write(strategy_b_md)
                total_ok = 1
                print(f"    Strategy B OK: {len(strategy_b_md)} chars")
            else:
                print("  Strategy B failed: no meaningful content extracted")


    # Step 2: Download source files (only if not already handled by Strategy B)
    total_ok = 0
    total_fail = 0

    if not strategy_b_used and pages:
        print(f"\nStep 2: Downloading {len(pages)} pages...")

        for page in pages:
            subdir = page.get('subdir', '')
            filename = page.get('filename', '')
            path = page.get('path', '')
            title = page.get('title', '')

            # Create subdirectory
            if subdir:
                save_dir = os.path.join(output_dir, subdir)
                os.makedirs(save_dir, exist_ok=True)
                md_path = os.path.join(save_dir, f"{filename}.md")
            else:
                md_path = os.path.join(output_dir, f"{filename}.md")

            print(f"  [{total_ok + 1}] {title}")

            # Prefer GitHub source
            content = None
            if args.github_repo:
                # Derive GitHub source path
                source_path = path.replace('.html', '.md')
                if not source_path.startswith(args.github_docs_path):
                    source_path = f"{args.github_docs_path}{source_path}"
                content = download_github_md(args.github_repo, source_path, md_path, args.github_branch)

                # Fallback: for trailing-slash URLs (VitePress/VuePress convention),
                # /section/ maps to section/index.md, not section.md
                if content is None and source_path.endswith('.md'):
                    index_path = source_path.replace('.md', '/index.md')
                    content = download_github_md(args.github_repo, index_path, md_path, args.github_branch)

            if content:
                content = strip_frontmatter(content)
                # Inject H1 title and date from original page HTML
                title_meta, date_meta = extract_page_metadata(html)
                content = inject_metadata(content, title_meta, date_meta)
                # Collect remote image URLs
                all_remote_images.update(extract_image_urls(content))
                # Fix image paths for local viewing
                content = fix_image_paths(content, subdir)
                # Fill empty/generic image alt text
                content = fill_image_alt_text(content)

                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                total_ok += 1
                print(f"    OK: {len(content)} chars")
            else:
                total_fail += 1
                print(f"    FAILED")

    # Step 3: Download all images
    print(f"\nStep 3: Downloading {len(all_remote_images)} images...")
    img_ok = 0
    img_fail = 0

    for img_url in sorted(all_remote_images):
        img_filename = os.path.basename(img_url.split('?')[0])
        img_save_path = os.path.join(img_dir, img_filename)

        if os.path.exists(img_save_path):
            img_ok += 1
            continue

        size = download_image(img_url, img_save_path)
        if size > 0:
            print(f"    {img_filename}: {size} bytes OK")
            img_ok += 1
        else:
            img_fail += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Pages: {total_ok} success, {total_fail} fail")
    print(f"  Images: {img_ok} success, {img_fail} fail")
    print(f"  Output: {output_dir}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
