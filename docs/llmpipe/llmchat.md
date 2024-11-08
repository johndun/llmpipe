Module llmpipe.llmchat
======================

Classes
-------

`LlmChat(model: str = 'anthropic/claude-3-5-sonnet-20241022', system_prompt: str = '', max_tokens: int = 4096, top_p: float = 1.0, temperature: float = 0.0, tools: List[Callable] = None, max_tool_calls: int = 6, stream: bool = False)`
:   A class for facilitating a multi-turn chat with an LLM
    
    ### Usage
    
    ```
    chat = LlmChat(system_prompt="Talk like a pirate")
    print(chat("Hello"))
    print(chat("How are you"))
    print(chat.tokens.total)
    ```

    ### Class variables

    `max_tokens: int`
    :   The maximum number of tokens to generate (default: 4,096)

    `max_tool_calls: int`
    :   The maximum number of sequential tool calls (default: 6)

    `model: str`
    :   A litellm model identifier: https://docs.litellm.ai/docs/providers

    `stream: bool`
    :   If true, use streaming API mode

    `system_prompt: str`
    :   A system prompt (default: )

    `temperature: float`
    :   The sampling temperature to use for generation (default: 0.)

    `tools: List[Callable]`
    :   An optional list of tools as python functions (default: None)

    `top_p: float`
    :   The cumulative probability for top-p sampling (default: 1.)

    ### Instance variables

    `model_args`
    :

    ### Methods

    `clear_history(self)`
    :   Clears and re initializes the history

    `get_tool_responses(self, tool_calls)`
    :

`Tokens(last_input_tokens: int = 0, last_output_tokens: int = 0, input_tokens: int = 0, output_tokens: int = 0)`
:   Counts tokens

    ### Class variables

    `input_tokens: int`
    :

    `last_input_tokens: int`
    :

    `last_output_tokens: int`
    :

    `output_tokens: int`
    :

    ### Instance variables

    `last`
    :   Returns formatted string containing last message token counts

    `total`
    :   Returns formatted string containing total token counts

    ### Methods

    `add(self, input_tokens, output_tokens)`
    :