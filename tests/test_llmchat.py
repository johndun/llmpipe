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


def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def greet(name: str) -> str:
    """Greet someone"""
    return f"Hello {name}!"

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


def test_llmchat_with_tools():
    """Test LLM chat with function calling"""
    chat = LlmChat(
        system_prompt="You are a helpful assistant.",
        tools=[add, greet]
    )
    
    # Verify tool registration
    assert len(chat.tool_schemas) == 2
    assert chat.tool_schemas[0]["function"]["name"] == "add"
    assert chat.tool_schemas[1]["function"]["name"] == "greet"
    
    # Mock a response with tool calls
    class MockFunction:
        def __init__(self):
            self.name = 'add'
            self.arguments = '{"a": 5, "b": 3}'
            
        def model_dump(self):
            return {
                'name': self.name,
                'arguments': self.arguments
            }
            
        def __iter__(self):
            return iter([('name', self.name), ('arguments', self.arguments)])

    class MockToolCall:
        def __init__(self):
            self.id = 'call1'
            self.function = MockFunction()

    mock_tool_call = MockToolCall()
    
    mock_response = type('MockResponse', (), {
        'choices': [
            type('Choice', (), {
                'message': type('Message', (), {
                    'content': 'Let me calculate that for you.',
                    'tool_calls': [mock_tool_call],
                    'role': 'assistant',
                    'model_dump': lambda: {
                        'role': 'assistant',
                        'content': 'Let me calculate that for you.',
                        'tool_calls': [{
                            'id': 'call1',
                            'function': {
                                'name': 'add',
                                'arguments': '{"a": 5, "b": 3}'
                            }
                        }]
                    }
                })
            })
        ],
        'usage': type('Usage', (), {
            'prompt_tokens': 30,
            'completion_tokens': 15
        })
    })

    # Test chat interaction with tool calls
    with patch('llmpipe.llmchat.completion') as mock_completion:
        # First response uses tool
        mock_completion.return_value = mock_response
        response = chat("What is 5 + 3?")
        
        # Verify tool call was processed
        assert "Tool call:" in response
        assert '"name": "add"' in response
        assert "Tool response:" in response
        assert "8" in response
        
        # Verify history includes tool interaction
        tool_message = next(msg for msg in chat.history if msg.get('role') == 'tool')
        assert tool_message['name'] == 'add'
        assert tool_message['content'] == 8
