import pytest
from llmpipe.evaluations.contains_one import ContainsOne
from llmpipe.evaluations.core import EvalResult


def test_contains_one_init():
    eval = ContainsOne(field="text", required_terms=["apple", "banana"])
    assert eval.field == "text"
    assert eval.required_terms == ["apple", "banana"]
    assert "Must contain at least one of: apple, banana" in eval.requirement
    assert eval.type == "deterministic"


def test_contains_one_custom_requirement():
    eval = ContainsOne(
        field="text",
        required_terms=["apple", "banana"],
        requirement="Must have a fruit"
    )
    assert eval.requirement == "Must have a fruit"


def test_contains_one_pass():
    eval = ContainsOne(field="text", required_terms=["apple", "banana"])
    result = eval(text="I like apple pie")
    assert isinstance(result, EvalResult)
    assert result.evaluation_result == "PASS"
    assert result.field == "text"


def test_contains_one_pass_case_insensitive():
    eval = ContainsOne(field="text", required_terms=["Apple", "Banana"])
    result = eval(text="i like apple pie")
    assert result.evaluation_result == "PASS"


def test_contains_one_fail():
    eval = ContainsOne(field="text", required_terms=["apple", "banana"])
    result = eval(text="I like orange pie")
    assert result.evaluation_result == "FAIL"
    assert "does not contain any of the required values" in result.reason


def test_contains_one_empty_input():
    eval = ContainsOne(field="text", required_terms=["apple", "banana"])
    result = eval(text="")
    assert result.evaluation_result == "FAIL"


def test_contains_one_missing_field():
    eval = ContainsOne(field="text", required_terms=["apple", "banana"])
    result = eval(other_field="I like apple pie")
    assert result.evaluation_result == "FAIL"


def test_contains_one_non_string_input():
    eval = ContainsOne(field="number", required_terms=["123"])
    result = eval(number=123)
    assert result.evaluation_result == "PASS"


def test_contains_one_init_validation():
    with pytest.raises(AssertionError):
        ContainsOne(field="text", required_terms=None)
