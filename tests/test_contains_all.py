import pytest
from llmpipe.evaluations.contains_all import ContainsAll


def test_contains_all_basic():
    """Test basic functionality with all terms present"""
    eval = ContainsAll(
        field="text",
        value=["apple", "banana"],
        requirement="Must contain both fruits",
        type="contains_all"
    )
    result = eval(text="I have an apple and a banana")
    assert result.passed
    assert "contains all required values" in result.explanation


def test_contains_all_missing_terms():
    """Test when some terms are missing"""
    eval = ContainsAll(
        field="text",
        value=["apple", "banana", "orange"],
        requirement="Must contain all fruits",
        type="contains_all"
    )
    result = eval(text="I have an apple and a banana")
    assert not result.passed
    assert "missing required values" in result.explanation
    assert "orange" in result.explanation


def test_contains_all_case_insensitive():
    """Test case insensitive matching"""
    eval = ContainsAll(
        field="text",
        value=["APPLE", "BaNaNa"],
        requirement="Must contain fruits (case insensitive)",
        type="contains_all"
    )
    result = eval(text="i have an Apple and a banana")
    assert result.passed


def test_contains_all_empty_input():
    """Test with empty input text"""
    eval = ContainsAll(
        field="text",
        value=["apple"],
        requirement="Must contain apple",
        type="contains_all"
    )
    result = eval(text="")
    assert not result.passed


def test_contains_all_missing_field():
    """Test with missing input field"""
    eval = ContainsAll(
        field="missing_field",
        value=["apple"],
        requirement="Must contain apple",
        type="contains_all"
    )
    result = eval(text="I have an apple")
    assert not result.passed


def test_contains_all_empty_values():
    """Test with empty values list"""
    eval = ContainsAll(
        field="text",
        value=[],
        requirement="No required values",
        type="contains_all"
    )
    result = eval(text="Any text here")
    assert result.passed


def test_contains_all_non_string_values():
    """Test with non-string values"""
    eval = ContainsAll(
        field="text",
        value=[123, True],
        requirement="Must contain non-string values",
        type="contains_all"
    )
    result = eval(text="Contains 123 and True")
    assert result.passed
