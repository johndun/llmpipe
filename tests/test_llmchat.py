import pytest
from llmpipe.llmchat import Tokens


def test_tokens_init():
    """Test initial token counter state"""
    tokens = Tokens()
    assert tokens.last_input_tokens == 0
    assert tokens.last_output_tokens == 0
    assert tokens.input_tokens == 0
    assert tokens.output_tokens == 0


def test_tokens_add():
    """Test adding token counts"""
    tokens = Tokens()
    
    # First addition
    tokens.add(10, 5)
    assert tokens.last_input_tokens == 10
    assert tokens.last_output_tokens == 5
    assert tokens.input_tokens == 10
    assert tokens.output_tokens == 5
    
    # Second addition
    tokens.add(20, 8)
    assert tokens.last_input_tokens == 20
    assert tokens.last_output_tokens == 8
    assert tokens.input_tokens == 30
    assert tokens.output_tokens == 13


def test_tokens_formatting():
    """Test token count string formatting"""
    tokens = Tokens()
    tokens.add(1234, 567)
    
    assert tokens.last == "in: 1,234, out: 567"
    assert tokens.total == "in: 1,234, out: 567"
    
    tokens.add(4321, 765)
    assert tokens.last == "in: 4,321, out: 765"
    assert tokens.total == "in: 5,555, out: 1,332"
