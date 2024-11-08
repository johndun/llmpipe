from llmpipe.evaluations.is_in import IsInAllowList


def test_is_in_allow_list_pass():
    """Test that allowed terms pass"""
    evaluation = IsInAllowList(field="text", allowed_terms=["apple", "banana", "cherry"])
    result = evaluation(text="apple")
    assert result.evaluation_result == "PASS"
    assert result.field == "text"
    assert "Must be one of the following terms" in result.requirement


def test_is_in_allow_list_fail():
    """Test that non-allowed terms fail"""
    evaluation = IsInAllowList(field="text", allowed_terms=["apple", "banana", "cherry"])
    result = evaluation(text="orange")
    assert result.evaluation_result == "FAIL"
    assert "orange" in result.reason
    assert result.field == "text"


def test_is_in_allow_list_case_insensitive():
    """Test case insensitive matching"""
    evaluation = IsInAllowList(field="text", allowed_terms=["Apple", "Banana"])
    result = evaluation(text="apple")
    assert result.evaluation_result == "PASS"


def test_is_in_allow_list_from_field():
    """Test using allowed terms from an input field"""
    evaluation = IsInAllowList(field="text", allowed_terms_field="allowed")
    result = evaluation(text="apple", allowed=["apple", "banana"])
    assert result.evaluation_result == "PASS"


def test_is_in_allow_list_custom_requirement():
    """Test custom requirement message"""
    evaluation = IsInAllowList(
        field="text",
        allowed_terms=["apple"],
        requirement="Must be a valid fruit"
    )
    result = evaluation(text="apple")
    assert result.requirement == "Must be a valid fruit"


def test_is_in_allow_list_empty_allowed_list():
    """Test with empty allowed list"""
    evaluation = IsInAllowList(field="text", allowed_terms=[])
    result = evaluation(text="anything")
    assert result.evaluation_result == "FAIL"
