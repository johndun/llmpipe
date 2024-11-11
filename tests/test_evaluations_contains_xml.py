import pytest
from llmpipe.evaluations.contains_xml import ContainsXml


def test_contains_xml_basic():
    """Test ContainsXml with basic XML content"""
    eval = ContainsXml(field="text", xml_tags=["summary", "details"])
    
    # Test successful case with all required tags
    assert eval(text="<summary>Test summary</summary><details>Test details</details>").evaluation_result == "PASS"
    
    # Test successful case with extra tags
    assert eval(text="<summary>Summary</summary><extra>Extra</extra><details>Details</details>").evaluation_result == "PASS"
    
    # Test failure case with missing tags
    result = eval(text="<summary>Only summary</summary>")
    assert result.evaluation_result == "FAIL"
    assert "<details>" in result.reason


def test_contains_xml_nested():
    """Test ContainsXml with nested XML content"""
    eval = ContainsXml(field="text", xml_tags=["outer", "inner"])
    
    # Test nested tags
    assert eval(text="<outer>Text<inner>Nested</inner></outer>").evaluation_result == "PASS"
    
    # Test separated nested tags
    assert eval(text="<outer>Text</outer><inner>Separate</inner>").evaluation_result == "PASS"


def test_contains_xml_edge_cases():
    """Test ContainsXml edge cases"""
    eval = ContainsXml(field="text", xml_tags=["tag"])
    
    # Test empty input
    result = eval(text="")
    assert result.evaluation_result == "FAIL"
    assert "<tag>" in result.reason
    
    # Test malformed XML
    assert eval(text="<tag>Unclosed").evaluation_result == "FAIL"
    
    # Test case sensitivity
    assert eval(text="<TAG>Upper case</TAG>").evaluation_result == "FAIL"
    
    # Test with whitespace
    assert eval(text="  <tag>  Spaced  </tag>  ").evaluation_result == "PASS"


def test_contains_xml_requirement_message():
    """Test requirement message generation"""
    # Test default requirement message
    eval1 = ContainsXml(field="text", xml_tags=["tag1", "tag2"])
    assert "Must contain the following XML blocks: <tag1>, <tag2>" in eval1.requirement
    
    # Test custom requirement message
    eval2 = ContainsXml(field="text", xml_tags=["tag"], requirement="Custom XML requirement")
    assert eval2.requirement == "Custom XML requirement"
    
    # Test no tags specified
    eval3 = ContainsXml(field="text")
    assert eval3.requirement is None
