import pytest
from llmpipe.evaluations.no_blocked_terms import NoBlockedTerms


def test_no_blocked_terms_basic():
    """Test basic blocked terms functionality"""
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms=["bad", "worse", "worst"]
    )
    
    # Test passing case
    result = evaluation(text="This is good text")
    assert result.evaluation_result == "PASS"
    
    # Test failing case - single word
    result = evaluation(text="This is bad text")
    assert result.evaluation_result == "FAIL"
    assert "bad" in result.reason
    
    # Test case sensitivity
    result = evaluation(text="This is BAD text")
    assert result.evaluation_result == "FAIL"
    assert "bad" in result.reason


def test_no_blocked_terms_phrases():
    """Test multi-word blocked terms"""
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms=["bad word", "worse phrase"]
    )
    
    # Test passing case
    result = evaluation(text="This is good text")
    assert result.evaluation_result == "PASS"
    
    # Test failing case - multi word phrase
    result = evaluation(text="This is a bad word in text")
    assert result.evaluation_result == "FAIL"
    assert "bad word" in result.reason


def test_no_blocked_terms_dynamic():
    """Test blocked terms from input field"""
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms_field="additional_blocked"
    )
    
    # Test with dynamic blocked terms
    result = evaluation(
        text="This contains forbidden word",
        additional_blocked=["forbidden"]
    )
    assert result.evaluation_result == "FAIL"
    assert "forbidden" in result.reason
    
    # Test with empty blocked terms
    result = evaluation(
        text="This is fine",
        additional_blocked=[]
    )
    assert result.evaluation_result == "PASS"


def test_no_blocked_terms_combined():
    """Test combination of static and dynamic blocked terms"""
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms=["static"],
        blocked_terms_field="dynamic"
    )
    
    # Test static term
    result = evaluation(
        text="This has static term",
        dynamic=[]
    )
    assert result.evaluation_result == "FAIL"
    assert "static" in result.reason
    
    # Test dynamic term
    result = evaluation(
        text="This has dynamic term",
        dynamic=["dynamic"]
    )
    assert result.evaluation_result == "FAIL"
    assert "dynamic" in result.reason
    
    # Test both passing
    result = evaluation(
        text="This is fine",
        dynamic=["not_present"]
    )
    assert result.evaluation_result == "PASS"


def test_no_blocked_terms_requirement():
    """Test requirement string generation"""
    # Test with static terms
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms=["term1", "term2"]
    )
    assert "term1, term2" in evaluation.requirement
    
    # Test with dynamic field
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms_field="blocked"
    )
    assert "{{blocked}}" in evaluation.requirement
    
    # Test with custom requirement
    custom_req = "Custom requirement text"
    evaluation = NoBlockedTerms(
        field="text",
        blocked_terms=["term"],
        requirement=custom_req
    )
    assert evaluation.requirement == custom_req
