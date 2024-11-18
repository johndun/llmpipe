import pytest
from llmpipe.evaluations.contains_all import ContainsAll


def test_contains_all_basic():
    """Test basic functionality with all terms present"""
    eval = ContainsAll(
        field="text",
        required_terms=["apple", "banana"],
    )
    result = eval(text="I have an apple and a banana")
    assert result.evaluation_result == "PASS"


def test_contains_all_missing_terms():
    """Test when some terms are missing"""
    eval = ContainsAll(
        field="text",
        required_terms=["apple", "banana", "orange"],
    )
    result = eval(text="I have an apple and a banana")
    assert result.evaluation_result == "FAIL"
    assert "orange" in result.reason


def test_contains_all_case_insensitive():
    """Test case insensitive matching"""
    eval = ContainsAll(
        field="text",
        required_terms=["APPLE", "BaNaNa"],
    )
    result = eval(text="i have an Apple and a banana")
    assert result.evaluation_result == "PASS"


def test_contains_all_empty_input():
    """Test with empty input text"""
    eval = ContainsAll(
        field="text",
        required_terms=["apple"],
    )
    result = eval(text="")
    assert result.evaluation_result == "FAIL"


def test_contains_all_missing_field():
    """Test with missing input field"""
    eval = ContainsAll(
        field="missing_field",
        required_terms=["apple"],
    )
    result = eval(text="I have an apple")
    assert result.evaluation_result == "FAIL"


def test_contains_all_non_string_values():
    """Test with non-string values"""
    eval = ContainsAll(
        field="text",
        required_terms=[123, True],
    )
    result = eval(text="Contains 123 and True")
    assert result.evaluation_result == "PASS"
