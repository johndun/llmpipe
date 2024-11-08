from llmpipe.evaluations.max_chars import MaxCharacters


def test_max_chars_pass():
    """Test passing case for MaxCharacters"""
    eval = MaxCharacters(field="text", max_chars=10)
    result = eval(text="Hello")
    assert result.evaluation_result == "PASS"
    assert result.field == "text"
    assert result.requirement == "Has at most 10 characters"
    assert result.reason == ""


def test_max_chars_fail():
    """Test failing case for MaxCharacters"""
    eval = MaxCharacters(field="text", max_chars=5)
    result = eval(text="Too long")
    assert result.evaluation_result == "FAIL"
    assert result.field == "text"
    assert result.requirement == "Has at most 5 characters"
    assert result.reason == "Should have at most 5 chars, but has 8"


def test_max_chars_custom_requirement():
    """Test MaxCharacters with custom requirement message"""
    eval = MaxCharacters(
        field="text",
        max_chars=10,
        requirement="Must be brief"
    )
    result = eval(text="Hello")
    assert result.requirement == "Must be brief"


def test_max_chars_edge_cases():
    """Test edge cases for MaxCharacters"""
    eval = MaxCharacters(field="text", max_chars=5)
    
    # Empty string
    result = eval(text="")
    assert result.evaluation_result == "PASS"
    
    # Exact length
    result = eval(text="12345")
    assert result.evaluation_result == "PASS"
