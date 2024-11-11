import pytest
from llmpipe.evaluations.is_in_string import IsInString


def test_is_in_string_direct():
    """Test IsInString with direct target string"""
    eval = IsInString(field="word", target_string="The quick brown fox")
    
    # Test successful cases
    assert eval(word="quick").evaluation_result == "PASS"
    assert eval(word="fox").evaluation_result == "PASS"
    assert eval(word="brown").evaluation_result == "PASS"
    
    # Test case insensitivity
    assert eval(word="QUICK").evaluation_result == "PASS"
    assert eval(word="Fox").evaluation_result == "PASS"
    
    # Test failure cases
    result = eval(word="slow")
    assert result.evaluation_result == "FAIL"
    assert "not found in the target string" in result.reason


def test_is_in_string_field_reference():
    """Test IsInString with field reference"""
    eval = IsInString(field="word", target_string_field="text")
    
    # Test successful cases
    assert eval(word="dog", text="The dog barks").evaluation_result == "PASS"
    assert eval(word="barks", text="The dog barks").evaluation_result == "PASS"
    
    # Test case insensitivity
    assert eval(word="DOG", text="The dog barks").evaluation_result == "PASS"
    assert eval(word="Dog", text="the DOG barks").evaluation_result == "PASS"
    
    # Test failure cases
    result = eval(word="cat", text="The dog barks")
    assert result.evaluation_result == "FAIL"
    assert "not found in the target string" in result.reason


def test_is_in_string_edge_cases():
    """Test IsInString edge cases"""
    eval = IsInString(field="word", target_string="test string")
    
    # Test empty input
    result = eval(word="")
    assert result.evaluation_result == "PASS"  # Empty string is substring of any string
    
    # Test None or missing target string field
    eval_field = IsInString(field="word", target_string_field="missing")
    result = eval_field(word="test")
    assert result.evaluation_result == "FAIL"
    
    # Test whitespace handling
    eval_space = IsInString(field="word", target_string="  spaced  text  ")
    assert eval_space(word="spaced").evaluation_result == "PASS"
    assert eval_space(word="  spaced  ").evaluation_result == "PASS"


def test_is_in_string_requirement_message():
    """Test requirement message generation"""
    # Test direct string requirement
    eval1 = IsInString(field="word", target_string="target")
    assert eval1.requirement == "Must be contained in: target"
    
    # Test field reference requirement
    eval2 = IsInString(field="word", target_string_field="text")
    assert eval2.requirement == "Must be contained in: {{text}}"
    
    # Test custom requirement
    eval3 = IsInString(field="word", target_string="target", requirement="Custom requirement")
    assert eval3.requirement == "Custom requirement"
