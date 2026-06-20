"""Tests for web-to-local-md content extraction functions."""
import pytest
import sys
import os

# Add scripts directory to path for import
sys.path.insert(0, os.path.dirname(__file__))

from web_to_local_md import extract_main_content

def test_extract_article_tag():
    """Content inside <article> should be extracted."""
    html = '<html><body><nav>skip nav</nav><article><h1>Title</h1><p>Content paragraph that is long enough to pass the threshold check.</p></article><footer>skip footer</footer></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert '<h1>Title</h1>' in result
    assert '<p>Content paragraph' in result

def test_extract_role_main():
    """Content inside role=main should be extracted when no <article>."""
    html = '<html><body><nav>skip nav</nav><div role="main"><h2>Heading</h2><p>Main text here that is long enough to pass threshold.</p></div></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert '<h2>Heading</h2>' in result
    assert 'Main text here' in result

def test_extract_main_tag():
    """Content inside <main> should be extracted."""
    html = '<html><body><header>skip header text</header><main><p>Main content only that is long enough for threshold.</p></main></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'Main content only' in result

def test_extract_known_class():
    """Known content class names should be found."""
    html = '<html><body><div class="sidebar">skip sidebar text here</div><div class="article-content"><p>Article text that is long enough for threshold check.</p></div></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'Article text' in result

def test_extract_cnblogs_id():
    """Blog-specific IDs like cnblogs_post_body should be found."""
    html = '<html><body><div id="header">skip header text</div><div id="cnblogs_post_body"><p>Blog content that is long enough for threshold check to pass.</p></div></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'Blog content' in result

def test_fallback_to_body():
    """When no specific container found, fall back to <body>."""
    html = '<html><head><title>Test</title></head><body><p>Only body content that is sufficiently long for the threshold.</p></body></html>'
    result = extract_main_content(html)
    assert result is not None
    assert 'Only body content' in result

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
