import pytest
from llmpipe.xml import XmlBlock, parse_text_for_tags, parse_text_for_tag

def test_xml_block_basic():
    text = "<test>content</test>"
    blocks = parse_text_for_tags(text)
    assert len(blocks) == 1
    assert blocks[0].tag == "test"
    assert blocks[0].content == "content"

def test_xml_block_nested():
    text = "<outer>before<inner>nested</inner>after</outer>"
    blocks = parse_text_for_tags(text)
    assert len(blocks) == 1
    assert blocks[0].tag == "outer"
    assert blocks[0].content == "before<inner>nested</inner>after"

def test_parse_text_for_tag():
    text = """
    <tag1>content1</tag1>
    <tag2>content2</tag2>
    <tag1>content3</tag1>
    """
    results = parse_text_for_tag(text, "tag1")
    assert len(results) == 2
    assert results[0] == "content1"
    assert results[1] == "content3"

def test_empty_text():
    assert parse_text_for_tags("") == []
    assert parse_text_for_tag("", "test") == []

def test_no_tags():
    text = "plain text without any tags"
    assert parse_text_for_tags(text) == []
    assert parse_text_for_tag(text, "test") == []
