#!/usr/bin/env python3
"""
web_to_local_md.py - Download a website section to local markdown with images

Encapsulates the full process:
1. Discover pages from site sidebar
2. Download source .md from GitHub (preferred) or convert HTML
3. Download all images from CDN
4. Render mermaid blocks to PNG (if mmdc available)
5. Fix relative image paths
6. Clean up temp files

Usage:
  python web_to_local_md.py --url "https://javaguide.cn/ai/" --github-repo "Snailclimb/JavaGuide" --output-dir "./downloaded" --render-mermaid
"""

import argparse
import os
import re
import sys
import json
import subprocess
import tempfile
import urllib.request
from html.parser import HTMLParser


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

def download_github_md(github_repo, source_path, save_path):
    """Download a markdown file from GitHub raw URL."""
    url = f"https://raw.githubusercontent.com/{github_repo}/main/{source_path}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        with open(save_path, 'wb') as f:
            f.write(content)
        return content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  GitHub download failed: {e}")
        return None


def strip_frontmatter(content):
    """Remove YAML frontmatter from markdown content."""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            return content[end + 3:].strip()
    return content


# ─── Image Handling ───

def extract_image_urls(content):
    """Extract all remote image URLs from content."""
    urls = set()
    # oss.javaguide.cn or generic CDN patterns
    patterns = [
        r'https://oss\.[a-zA-Z0-9_-]+\.[a-zA-Z]{2,}/[^\s)\"]+\.(?:png|jpg|jpeg|gif|svg|webp)',
        r'https://[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}/[^\s)\"]+\.(?:png|jpg|jpeg|gif|svg|webp)',
    ]
    for pattern in patterns:
        for url in re.findall(pattern, content):
            urls.add(url)
    return urls


def download_image(url, save_path):
    """Download an image from URL to local path."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        if len(content) > 100:
            with open(save_path, 'wb') as f:
                f.write(content)
            return len(content)
        return 0
    except Exception as e:
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

    content = re.sub(
        r'https://oss\.[a-zA-Z0-9_-]+\.[a-zA-Z]{2,}/[^\s)\"]+\.(?:png|jpg|jpeg|gif|svg|webp)',
        replace_url, content
    )
    # Fix %20 in filenames
    content = content.replace('%20.png', '.png')
    content = content.replace('%20.svg', '.svg')
    return content


# ─── Mermaid Rendering ───

def find_mmdc_path():
    """Find mmdc executable path (handles Windows npm location)."""
    # Try direct execution first
    try:
        result = subprocess.run(['mmdc', '--version'], capture_output=True, timeout=10)
        if result.returncode == 0:
            return 'mmdc'
    except Exception:
        pass

    # On Windows, find npm global path
    try:
        result = subprocess.run(['npm', 'prefix', '-g'], capture_output=True, timeout=10,
                                shell=True)
        if result.returncode == 0:
            prefix = result.stdout.decode('utf-8', errors='ignore').strip()
            mmdc_path = os.path.join(prefix, 'mmdc.cmd')
            if os.path.exists(mmdc_path):
                return mmdc_path
    except Exception:
        pass

    return None


def render_mermaid_block(code, output_path, mmdc_path):
    """Render a mermaid code block to PNG using mmdc."""
    tmp_mmd = os.path.join(tempfile.gettempdir(), 'mermaid_temp.mmd')
    with open(tmp_mmd, 'w', encoding='utf-8') as f:
        f.write(code)

    try:
        cmd = [mmdc_path, '-i', tmp_mmd, '-o', output_path, '-b', 'white', '--scale', '2']
        result = subprocess.run(cmd, capture_output=True, timeout=60, shell=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            return True
        return False
    except Exception as e:
        print(f"    mmdc error: {e}")
        return False
    finally:
        if os.path.exists(tmp_mmd):
            os.unlink(tmp_mmd)


def render_all_mermaid(content, filename, img_dir, mmdc_path, subdir=''):
    """Find all mermaid code blocks, render to PNG, replace with image refs."""
    blocks = []
    pattern = r'```mermaid\n(.*?)```'
    for match in re.finditer(pattern, content, re.DOTALL):
        blocks.append({
            'start': match.start(),
            'end': match.end(),
            'code': match.group(1),
        })

    if not blocks or not mmdc_path:
        return content, 0

    new_content = content
    rendered = 0

    # Process from end to start to preserve offsets
    for i in range(len(blocks) - 1, -1, -1):
        block = blocks[i]
        base_name = filename.replace('.md', '')
        img_filename = f"{base_name}-mermaid-{i + 1}.png"
        img_path = os.path.join(img_dir, img_filename)

        success = render_mermaid_block(block['code'], img_path, mmdc_path)
        if success:
            img_prefix = get_image_prefix(subdir)
            img_ref = f"![流程图 {i + 1}]({img_prefix}{img_filename})"
            new_content = new_content[:block['start']] + img_ref + new_content[block['end']:]
            rendered += 1
            print(f"    Mermaid block {i + 1}: rendered to {img_filename}")
        else:
            print(f"    Mermaid block {i + 1}: rendering failed, keeping code block")

    return new_content, rendered


# ─── Main Pipeline ───

def main():
    parser = argparse.ArgumentParser(description='Download website to local markdown')
    parser.add_argument('--url', required=True, help='Website section URL (e.g. https://javaguide.cn/ai/)')
    parser.add_argument('--github-repo', default=None, help='GitHub repo with source .md files (e.g. Snailclimb/JavaGuide)')
    parser.add_argument('--github-docs-path', default='docs', help='Path prefix in GitHub repo for doc files (default: docs)')
    parser.add_argument('--output-dir', required=True, help='Local output directory')
    parser.add_argument('--render-mermaid', action='store_true', help='Render mermaid blocks to PNG using mmdc')
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
    if args.pages:
        with open(args.pages, 'r', encoding='utf-8') as f:
            pages = json.load(f)
    else:
        # Discover pages from the site
        print("Step 1: Discovering pages from site sidebar...")
        try:
            req = urllib.request.Request(args.url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Failed to fetch site: {e}")
            sys.exit(1)

        # Parse section prefix from URL
        section_prefix = args.url.replace('https://', '/').replace('http://', '/').split('?')[0]
        if not section_prefix.endswith('/'):
            section_prefix += '/'
        base_url = args.url.split('/')[0] + '://' + '/'.join(args.url.split('/')[1:3])

        pages = discover_pages(base_url, section_prefix, html)
        print(f"  Found {len(pages)} pages")

        # Fallback: if no pages discovered and URL points to a specific page, download it directly
        if len(pages) == 0 and args.github_repo and not args.url.endswith('/'):
            # URL like https://javaguide.cn/ai/llm-basis/llm-operation-mechanism.html
            url_path = args.url.replace('https://', '').replace('http://', '').split('?')[0]
            # Remove domain, keep path
            domain = url_path.split('/')[0]
            page_path = '/' + '/'.join(url_path.split('/')[1:])
            # Convert .html to .md path
            md_path = page_path.replace('.html', '.md')
            # Derive subdir and filename from path
            path_parts = md_path.strip('/').split('/')
            if len(path_parts) > 1:
                subdir = '/'.join(path_parts[:-1])
                filename = path_parts[-1].replace('.md', '')
            else:
                subdir = ''
                filename = path_parts[-1].replace('.md', '')
            pages = [{'subdir': subdir, 'filename': filename, 'path': md_path, 'title': filename}]
            print(f"  Fallback: single-page download → {md_path}")


    # Step 2: Download source files
    print(f"\nStep 2: Downloading {len(pages)} pages...")
    total_ok = 0
    total_fail = 0
    all_remote_images = set()
    mmdc_path = find_mmdc_path() if args.render_mermaid else None

    if mmdc_path:
        print(f"  mmdc found: {mmdc_path}")
    elif args.render_mermaid:
        print("  WARNING: mmdc not found. Install: npm install -g @mermaid-js/mermaid-cli")

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
            is_subdir = True
        else:
            md_path = os.path.join(output_dir, f"{filename}.md")
            is_subdir = False

        print(f"  [{total_ok + 1}] {title}")

        # Prefer GitHub source
        content = None
        if args.github_repo:
            # Derive GitHub source path
            # path like /ai/agent/mcp.html -> docs/ai/agent/mcp.md
            source_path = path.replace('.html', '.md')
            if not source_path.startswith(args.github_docs_path):
                source_path = f"{args.github_docs_path}{source_path}"
            content = download_github_md(args.github_repo, source_path, md_path)

        if content:
            content = strip_frontmatter(content)
            # Collect remote image URLs
            all_remote_images.update(extract_image_urls(content))
            # Fix image paths for local viewing
            content = fix_image_paths(content, subdir)
            # Render mermaid if requested
            if mmdc_path and '```mermaid' in content:
                content, rendered = render_all_mermaid(content, filename, img_dir, mmdc_path, subdir)
                print(f"    Mermaid: {rendered} blocks rendered")

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
