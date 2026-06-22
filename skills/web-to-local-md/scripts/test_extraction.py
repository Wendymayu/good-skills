"""Tests for web-to-local-md content extraction functions."""
import pytest
import sys
import os

# Add scripts directory to path for import
sys.path.insert(0, os.path.dirname(__file__))

from web_to_local_md import extract_main_content, strip_noise, fetch_url, html_to_markdown, extract_image_urls, fix_image_paths

# Helper to generate sufficiently long content for threshold tests
# Must exceed 200 chars text AND 500 chars HTML
LONG_TEXT = ("This is a paragraph with enough content to exceed the two hundred character "
             "threshold that the extract_main_content function uses to filter out navigation "
             "bars, sidebar snippets, and other noise elements. The text must be substantial "
             "enough to represent real article content, not just a preview or a label. Adding "
             "more text to ensure the total HTML string length also exceeds five hundred chars.")

EXTRA_TEXT = " Additional paragraph to pad the HTML length above five hundred characters total."


def test_extract_article_tag():
    """Content inside <article> should be extracted."""
    html = '<html><body><nav>Navigation bar with links</nav><article><h1>Title</h1><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p></article><footer>Footer copyright notice</footer></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert '<h1>Title</h1>' in result
    assert 'enough content' in result


def test_extract_role_main():
    """Content inside role=main should be extracted when no <article>."""
    html = '<html><body><nav>Navigation bar with links here</nav><div role="main"><h2>Heading</h2><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p></div></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert '<h2>Heading</h2>' in result
    assert 'enough content' in result


def test_extract_main_tag():
    """Content inside <main> should be extracted."""
    html = '<html><body><header>Header with logo and navigation links</header><main><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p></main></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'enough content' in result


def test_extract_known_class():
    """Known content class names should be found."""
    html = '<html><body><div class="sidebar">Sidebar content that should be skipped entirely and not extracted</div><div class="article-content"><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p></div></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'enough content' in result


def test_extract_cnblogs_id():
    """Blog-specific IDs like cnblogs_post_body should be found."""
    html = '<html><body><div id="header">Blog header with navigation elements</div><div id="cnblogs_post_body"><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p></div></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'enough content' in result


def test_fallback_to_body():
    """When no specific container found, fall back to <body>."""
    html = '<html><head><title>Test Page Title Here</title></head><body><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p><p>Yet another paragraph to ensure enough content is available.</p></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'enough content' in result


def test_empty_html():
    """Empty or very short HTML should return None."""
    html = '<html><body></body></html>'
    result = extract_main_content(html)
    assert result is None


def test_short_html():
    """HTML with less than 200 chars of text should return None."""
    html = '<html><body><p>Short</p></body></html>'
    result = extract_main_content(html)
    assert result is None


def test_strip_scripts_and_styles():
    """Script and style tags should be removed."""
    html = '<div><script>alert("xss")</script><style>.foo{color:red}</style><p>Keep this paragraph of text content.</p></div>'
    result = strip_noise(html)
    assert 'alert' not in result
    assert '.foo' not in result
    assert 'Keep this' in result

def test_strip_nav_header_footer():
    """Nav, header, footer tags should be removed."""
    html = '<div><nav><a href="/home">Home navigation link</a></nav><p>Content here that is meaningful and worth keeping for reading.</p><footer>Copyright 2024 notice in footer area</footer></div>'
    result = strip_noise(html)
    assert 'Home navigation' not in result
    assert 'Copyright' not in result
    assert 'Content here' in result

def test_strip_aside():
    """Aside tags should be removed."""
    html = '<div><aside><p>Sidebar note that should be removed from the content.</p></aside><p>Main text paragraph that we want to preserve in output.</p></div>'
    result = strip_noise(html)
    assert 'Sidebar note' not in result
    assert 'Main text' in result

def test_strip_noise_classes():
    """Elements with noise class names should be removed."""
    html = '<div><div class="breadcrumb"><a>Home breadcrumb trail</a></div><div class="cookie-banner">Accept cookies notice banner text</div><p>Real content paragraph that should survive stripping.</p></div>'
    result = strip_noise(html)
    assert 'breadcrumb' not in result
    assert 'Accept cookies' not in result
    assert 'Real content' in result

def test_preserve_code_blocks():
    """Pre/code blocks should NOT be stripped."""
    html = '<div><pre><code>def hello():\n    pass</code></pre><p>Text paragraph content for preservation.</p></div>'
    result = strip_noise(html)
    assert 'def hello()' in result
    assert 'Text paragraph' in result


def test_fetch_url_success():
    """fetch_url should return HTML for a valid URL."""
    result = fetch_url('https://httpbin.org/html')
    assert result is not None
    assert len(result) > 100

def test_fetch_url_404():
    """fetch_url should return None for 404 URLs."""
    result = fetch_url('https://httpbin.org/status/404')
    assert result is None


def test_html_to_markdown_basic():
    """Convert simple HTML to Markdown."""
    html = '<html><body><article><h1>Title</h1><p>' + LONG_TEXT + '</p><p>' + EXTRA_TEXT + '</p><ul><li>Item 1</li><li>Item 2</li></ul></article></body></html>'
    md, title, date_str, nested_imgs = html_to_markdown(html)
    assert md is not None
    assert '# Title' in md
    assert 'Item 1' in md

def test_html_to_markdown_with_code():
    """Convert HTML with code blocks to Markdown."""
    html = '<html><body><article><p>Example code follows:</p><pre><code>print("hello world")</code></pre><p>' + LONG_TEXT + '</p></article></body></html>'
    md, title, date_str, nested_imgs = html_to_markdown(html)
    assert md is not None
    assert '```' in md
    assert 'print' in md

def test_html_to_markdown_with_links():
    """Convert HTML with links to Markdown."""
    html = '<html><body><article><p>Read the <a href="https://example.com">docs</a> for details.</p><p>' + LONG_TEXT + '</p></article></body></html>'
    md, title, date_str, nested_imgs = html_to_markdown(html)
    assert md is not None
    assert '[docs](https://example.com)' in md

def test_html_to_markdown_empty():
    """Empty HTML should return (None, None, None, set())."""
    md, title, date_str, nested_imgs = html_to_markdown('')
    assert md is None

def test_html_to_markdown_short():
    """Very short HTML should return (None, None, None, set())."""
    md, title, date_str, nested_imgs = html_to_markdown('<p>Hi</p>')
    assert md is None


# ─── Image URL extraction tests ───

def test_extract_generic_cdn_images():
    """Should extract images from any CDN domain, not just oss.*."""
    md = 'See ![diagram](https://cdn.example.com/images/diagram.png) and ![logo](https://static.site.com/assets/logo.svg)'
    urls = extract_image_urls(md)
    assert 'https://cdn.example.com/images/diagram.png' in urls
    assert 'https://static.site.com/assets/logo.svg' in urls

def test_extract_aws_s3_images():
    """Should extract AWS S3 hosted images."""
    md = '![arch](https://docs.aws.amazon.com/images/arch-diagram.png)'
    urls = extract_image_urls(md)
    assert 'https://docs.aws.amazon.com/images/arch-diagram.png' in urls

def test_no_local_paths():
    """Should NOT extract local/relative paths."""
    md = '![local](images/local.png) and ![relative](../images/relative.svg)'
    urls = extract_image_urls(md)
    assert len(urls) == 0

def test_no_non_image_urls():
    """Should NOT extract non-image URLs like .html pages."""
    md = 'Visit [link](https://example.com/page.html) and [api](https://api.example.com/v1/data)'
    urls = extract_image_urls(md)
    assert len(urls) == 0

def test_fix_image_paths_generic():
    """Should replace any remote image URL with local path."""
    md = '![img](https://cdn.example.com/images/photo.png)'
    result = fix_image_paths(md, '')
    assert 'images/photo.png' in result
    assert 'cdn.example.com' not in result

def test_fix_image_paths_subdir():
    """Should use ../images/ prefix for subdir content."""
    md = '![img](https://docs.aws.amazon.com/assets/diagram.png)'
    result = fix_image_paths(md, 'agent')
    assert '../images/diagram.png' in result
