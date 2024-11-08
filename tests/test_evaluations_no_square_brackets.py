from llmpipe.evaluations.no_square_brackets import NoSquareBrackets


def test_no_square_brackets_pass():
    """Test that text without square brackets passes"""
    eval = NoSquareBrackets(field="text")
    result = eval(text="This is normal text without brackets")
    assert result.evaluation_result == "PASS"
    assert result.field == "text"
    assert not result.reason


def test_no_square_brackets_fail():
    """Test that text with square brackets fails"""
    eval = NoSquareBrackets(field="text")
    result = eval(text="This has [placeholder] brackets")
    assert result.evaluation_result == "FAIL"
    assert result.field == "text"
    assert "Should not contain square brackets: [placeholder]" in result.reason


def test_no_square_brackets_multiple_fail():
    """Test that multiple square brackets are all reported"""
    eval = NoSquareBrackets(field="text")
    result = eval(text="Multiple [brackets] in [text] here")
    assert result.evaluation_result == "FAIL"
    assert result.field == "text"
    assert "[brackets], [text]" in result.reason


def test_no_square_brackets_empty():
    """Test that empty brackets still fail"""
    eval = NoSquareBrackets(field="text")
    result = eval(text="Text with [] empty brackets")
    assert result.evaluation_result == "FAIL"
    assert result.field == "text"
    assert "[]" in result.reason
