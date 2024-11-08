import pytest
from unittest.mock import patch
from llmpipe.llmchat import Tokens, LlmChat


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


def test_llmchat_basic_call():
    """Test basic LLM chat interaction"""
    chat = LlmChat(system_prompt="You are a helpful assistant.")
    
    # Mock response data
    mock_response = type('MockResponse', (), {
        'choices': [
            type('Choice', (), {
                'message': type('Message', (), {
                    'content': 'Hello! How can I help you today?',
                    'tool_calls': None,
                    'model_dump': lambda: {
                        'role': 'assistant',
                        'content': 'Hello! How can I help you today?'
                    }
                })
            })
        ],
        'usage': type('Usage', (), {
            'prompt_tokens': 20,
            'completion_tokens': 10
        })
    })

    # Test chat interaction with mocked completion
    with patch('llmpipe.llmchat.completion', return_value=mock_response):
        response = chat("Hi there!")
        
        # Verify response content
        assert response == "Hello! How can I help you today?"
        
        # Verify token counting
        assert chat.tokens.last == "in: 20, out: 10"
        assert chat.tokens.total == "in: 20, out: 10"
        
        # Verify chat history
        assert len(chat.history) == 3  # system + user + assistant
        assert chat.history[0]['role'] == 'system'
        assert chat.history[1]['role'] == 'user'
        assert chat.history[1]['content'] == 'Hi there!'
        assert chat.history[2]['role'] == 'assistant'
        assert chat.history[2]['content'] == 'Hello! How can I help you today?'
