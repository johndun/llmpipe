import pytest
from llmpipe.evaluations.not_in_blocked_list import NotInBlockedList
from llmpipe.evaluations.core import EvalResult


def test_not_in_blocked_list_static():
    """Test NotInBlockedList with a static blocked list"""
    eval = NotInBlockedList(field="color", blocked_list=["red", "green", "blue"])
    
    # Test passing case
    result = eval(color="yellow")
    assert isinstance(result, EvalResult)
    assert result.evaluation_result == "PASS"
    assert result.field == "color"
    
    # Test failing case
    result = eval(color="RED")  # Should fail case-insensitively
    assert result.evaluation_result == "FAIL"
    assert "is one of the blocked values" in result.reason
    
    # Test with spaces
    result = eval(color=" blue ")  # Should fail even with whitespace
    assert result.evaluation_result == "FAIL"


def test_not_in_blocked_list_dynamic():
    """Test NotInBlockedList with a dynamic blocked list field"""
    eval = NotInBlockedList(field="name", blocked_list_field="blocked_names")
    
    # Test passing case
    result = eval(name="Alice", blocked_names=["Bob", "Charlie"])
    assert result.evaluation_result == "PASS"
    
    # Test failing case
    result = eval(name="Bob", blocked_names=["Bob", "Charlie"])
    assert result.evaluation_result == "FAIL"
    
    # Test with empty blocked list
    result = eval(name="Bob", blocked_names=[])
    assert result.evaluation_result == "PASS"


def test_not_in_blocked_list_combined():
    """Test NotInBlockedList with both static and dynamic lists"""
    eval = NotInBlockedList(
        field="color",
        blocked_list=["red", "green"],
        blocked_list_field="more_colors"
    )
    
    # Test failing from static list
    result = eval(color="red", more_colors=["yellow"])
    assert result.evaluation_result == "FAIL"
    
    # Test failing from dynamic list
    result = eval(color="yellow", more_colors=["yellow", "purple"])
    assert result.evaluation_result == "FAIL"
    
    # Test passing case
    result = eval(color="purple", more_colors=["yellow"])
    assert result.evaluation_result == "PASS"


def test_not_in_blocked_list_requirements():
    """Test the requirement string generation"""
    # Test static requirement
    eval1 = NotInBlockedList(field="color", blocked_list=["red", "green"])
    assert "red, green" in eval1.requirement
    
    # Test dynamic requirement
    eval2 = NotInBlockedList(field="color", blocked_list_field="bad_colors")
    assert "{{bad_colors}}" in eval2.requirement
    
    # Test custom requirement
    custom_req = "Must not be a forbidden color"
    eval3 = NotInBlockedList(
        field="color",
        blocked_list=["red"],
        requirement=custom_req
    )
    assert eval3.requirement == custom_req
