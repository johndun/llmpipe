from llmpipe.evaluations.no_long_words import NoLongWords


def test_no_long_words_pass():
    """Test that words under max length pass"""
    evaluation = NoLongWords(field="text")
    result = evaluation(text="These are some short words")
    assert result.evaluation_result == "PASS"
    assert result.field == "text"
    assert "Contains no words with more than 10 characters" in result.requirement


def test_no_long_words_fail():
    """Test that words over max length fail"""
    evaluation = NoLongWords(field="text")
    result = evaluation(text="A supercalifragilistic word")
    assert result.evaluation_result == "FAIL"
    assert "supercalifragilistic" in result.reason
    assert result.field == "text"


def test_no_long_words_custom_max():
    """Test custom maximum word length"""
    evaluation = NoLongWords(field="text", max_chars=5)
    result = evaluation(text="short longer longest")
    assert result.evaluation_result == "FAIL"
    assert "longer, longest" in result.reason


def test_no_long_words_custom_requirement():
    """Test custom requirement message"""
    evaluation = NoLongWords(
        field="text",
        requirement="All words must be concise"
    )
    result = evaluation(text="short")
    assert result.requirement == "All words must be concise"


def test_no_long_words_empty_string():
    """Test empty string input"""
    evaluation = NoLongWords(field="text")
    result = evaluation(text="")
    assert result.evaluation_result == "PASS"


def test_no_long_words_special_chars():
    """Test words with special characters"""
    evaluation = NoLongWords(field="text", max_chars=5)
    result = evaluation(text="hello!! super-long-word")
    assert result.evaluation_result == "FAIL"
    assert "super-long-word" in result.reason
