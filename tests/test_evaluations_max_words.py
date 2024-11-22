from llmpipe.evaluations.max_words import MaxWords


def test_max_words_pass():
    """Test passing case for MaxWords"""
    eval = MaxWords(field="text", max_words=5)
    result = eval(text="These are four words")
    assert result.evaluation_result == "PASS"
    assert result.field == "text"
    assert result.requirement == "Has at most 5 words"
    assert result.reason == ""


def test_max_words_fail():
    """Test failing case for MaxWords"""
    eval = MaxWords(field="text", max_words=3)
    result = eval(text="This is too many words")
    assert result.evaluation_result == "FAIL"
    assert result.field == "text"
    assert result.requirement == "Has at most 3 words"
    assert result.reason == "Should have at most 3 words, but has 5"


def test_max_words_custom_requirement():
    """Test MaxWords with custom requirement message"""
    eval = MaxWords(
        field="text",
        max_words=5,
        requirement="Must be concise"
    )
    result = eval(text="Short text")
    assert result.requirement == "Must be concise"


def test_max_words_edge_cases():
    """Test edge cases for MaxWords"""
    eval = MaxWords(field="text", max_words=3)
    
    # Empty string
    result = eval(text="")
    assert result.evaluation_result == "PASS"
    
    # Single word
    result = eval(text="Hello")
    assert result.evaluation_result == "PASS"
    
    # Exact word count
    result = eval(text="One two three")
    assert result.evaluation_result == "PASS"
    
    # Extra whitespace
    result = eval(text="  One   two  three  ")
    assert result.evaluation_result == "PASS"
