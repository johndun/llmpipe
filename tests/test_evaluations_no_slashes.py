import pytest

from llmpipe.evaluations.no_slashes import NoSlashes


def test_no_slashes_pass():
    """Test cases where text should pass the no slashes check"""
    evaluator = NoSlashes(field="text")
    
    test_cases = [
        "normal text",
        "hyphenated-word",
        "text with spaces",
        "text with numbers 123",
        "text with punctuation!",
    ]
    
    for text in test_cases:
        result = evaluator(text=text)
        assert result.evaluation_result == "PASS"
        assert result.field == "text"
        assert "slash" in result.requirement.lower()


def test_no_slashes_fail():
    """Test cases where text should fail the no slashes check"""
    evaluator = NoSlashes(field="text")
    
    test_cases = [
        "input/output",
        "read/write access",
        "true/false value",
        "multiple/slashes/here",
    ]
    
    for text in test_cases:
        result = evaluator(text=text)
        assert result.evaluation_result == "FAIL"
        assert result.field == "text"
        assert "slash" in result.requirement.lower()
        assert "should not contain slash constructions" in result.reason


def test_no_slashes_mixed_content():
    """Test text with both valid and invalid constructions"""
    evaluator = NoSlashes(field="text")
    
    result = evaluator(text="normal text with input/output and more text")
    assert result.evaluation_result == "FAIL"
    assert "input/output" in result.reason

    result = evaluator(text="multiple issues: read/write and true/false")
    assert result.evaluation_result == "FAIL"
    assert "read/write" in result.reason
    assert "true/false" in result.reason
