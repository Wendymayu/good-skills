"""Tests for web-to-local-md content extraction functions."""
import pytest
import sys
import os

# Add scripts directory to path for import
sys.path.insert(0, os.path.dirname(__file__))

from web_to_local_md import extract_main_content

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
