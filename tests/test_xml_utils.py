import pytest
from llmpipe.xml_utils import XmlBlock, parse_text_for_tags, parse_text_for_tag, parse_text_for_one_tag

def test_xml_block_basic():
    text = "<test>content</test>"
    blocks = parse_text_for_tags(text)
    assert len(blocks) == 1
    assert blocks[0].tag == "test"
    assert blocks[0].content == "content"

def test_xml_block_repr():
    block = XmlBlock(tag="test", content="content")
    assert repr(block) == "<test>content</test>"
    

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

def test_parse_text_for_one_tag_basic():
    text = "<test>content</test>"
    result = parse_text_for_one_tag(text, "test")
    assert result == "content"

def test_parse_text_for_one_tag_multiple():
    text = """
    <test>first</test>
    <other>middle</other>
    <test>last</test>
    """
    result = parse_text_for_one_tag(text, "test")
    assert result == "last"  # Should return the last matching tag

def test_parse_text_for_one_tag_empty():
    assert parse_text_for_one_tag("", "test") == ""
    assert parse_text_for_one_tag("<other>content</other>", "test") == ""
