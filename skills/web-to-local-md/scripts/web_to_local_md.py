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


def html_to_markdown(html):
    """Convert HTML content to Markdown using extract + strip_noise + markdownify.

    Returns Markdown text on success, None if content is too short/empty.
    """
    from markdownify import markdownify as md_conv

    # Step 1: Extract main content
    content_html = extract_main_content(html)
    if content_html is None:
        return None

    # Step 2: Strip noise
    clean_html = strip_noise(content_html)

    # Step 3: Convert to Markdown
    markdown_text = md_conv(clean_html, heading_style="ATX", bullets="-")

    # Step 4: Clean up excessive whitespace
    # Remove 3+ consecutive blank lines → 2 blank lines
    markdown_text = re.sub(r'\n{4,}', '\n\n\n', markdown_text)
    # Remove trailing whitespace on each line
    markdown_text = re.sub(r' +\n', '\n', markdown_text)

    # Step 5: Check minimum content length
    plain_text = re.sub(r'[#*\[\]\(\)!>`\n]', '', markdown_text)
    if len(plain_text.strip()) < 200:
        return None

    return markdown_text.strip()


# ─── Image Handling ───

def extract_image_urls(content):
    """Extract all remote image URLs from content (Markdown or HTML)."""
    urls = set()
    # Match any https:// URL ending in an image extension
    # Covers CDN, docs sites, static sites, etc.
    pattern = r'https://[a-zA-Z0-9._/-]+/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|gif|svg|webp|avif)(?:\?[a-zA-Z0-9=&_-]*)?'
    for url in re.findall(pattern, content):
        urls.add(url)
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
    """Replace remote image URLs with local relative paths."""
    prefix = get_image_prefix(subdir)
    def replace_url(match):
        url = match.group(0)
        filename = os.path.basename(url.split('?')[0])
        return prefix + filename

    # Replace all remote image URLs (any domain)
    content = re.sub(
        r'https://[a-zA-Z0-9._/-]+/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|gif|svg|webp|avif)(?:\?[a-zA-Z0-9=&_-]*)?',
        replace_url, content
    )
    # Fix %20 in filenames
    content = content.replace('%20.png', '.png')
    content = content.replace('%20.svg', '.svg')
    content = content.replace('%20.jpg', '.jpg')
    content = content.replace('%20.jpeg', '.jpeg')
    return content


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
            strategy_b_md = html_to_markdown(html)
            if strategy_b_md:
                filename = 'index'
                md_save_path = os.path.join(output_dir, f"{filename}.md")
                strategy_b_used = True
                all_remote_images.update(extract_image_urls(strategy_b_md))
                strategy_b_md = fix_image_paths(strategy_b_md, '')
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
                # Collect remote image URLs
                all_remote_images.update(extract_image_urls(content))
                # Fix image paths for local viewing
                content = fix_image_paths(content, subdir)

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
