import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Callable, Union, Generator, Annotated
import yaml
import typer

from litellm import completion, ModelResponse, get_model_info, stream_chunk_builder
from litellm.utils import function_to_dict


logger = logging.getLogger(__name__)


@dataclass
class Tokens:
    """Counts tokens"""
    last_input_tokens: int = 0
    last_output_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other):
        return Tokens(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            last_input_tokens=self.last_input_tokens,
            last_output_tokens=self.last_output_tokens
        )

    def add(self, input_tokens, output_tokens):
        self.last_input_tokens = input_tokens
        self.input_tokens += input_tokens
        self.last_output_tokens = output_tokens
        self.output_tokens += output_tokens

    @property
    def last(self):
        """Returns formatted string containing last message token counts"""
        return f"in: {self.last_input_tokens:,.0f}, out: {self.last_output_tokens:,.0f}"

    @property
    def total(self):
        """Returns formatted string containing total token counts"""
        return f"in: {self.input_tokens:,.0f}, out: {self.output_tokens:,.0f}"


@dataclass
class LlmChat:
    """A class for facilitating a multi-turn chat with an LLM

    ### Usage

    ```
    chat = LlmChat(system_prompt="Talk like a pirate")
    print(chat("Hello"))
    print(chat("How are you"))
    print(chat.tokens.total)
    ```
    """
    model: str = "claude-3-5-sonnet-20241022"  #: A litellm model identifier: https://docs.litellm.ai/docs/providers
    system_prompt: str = ""  #: A system prompt (default: )
    max_tokens: int = 4096  #: The maximum number of tokens to generate (default: 4,096)
    top_p: float = 1.0  #: The cumulative probability for top-p sampling (default: 1.)
    top_k: int = 1  #: K for top-k sampling (default: 1)
    temperature: float = 0.0  #: The sampling temperature to use for generation (default: 0.)
    tools: List[Callable] = None  #: An optional list of tools as python functions (default: None)
    max_tool_calls: int = 6  #: The maximum number of sequential tool calls (default: 6)
    stream: bool = False  #: If true, use streaming API mode

    def __post_init__(self):
        assert not self.tools or not self.stream  # Disable tool calling in streaming mode
        self.history = []
        self.clear_history()
        self.tokens = Tokens()
        self.tool_schemas = []
        model_info = get_model_info(model=self.model)
        self.supports_assistant_prefill = model_info["supports_assistant_prefill"]
        self.supports_function_calling = model_info["supports_function_calling"]
        assert not self.tools or self.supports_function_calling
        if self.tools:
            self.tool_schemas = [
                {
                    "type": "function",
                    "function": function_to_dict(function)
                }
                for function in self.tools
            ]
            self.tools_map = {
                schema["function"]["name"]: function
                for schema, function in zip(self.tool_schemas, self.tools)
            }

    @property
    def model_args(self):
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "temperature": self.temperature
        }

    def clear_history(self):
        """Clears and re initializes the history"""
        self.history = []
        if self.system_prompt:
            self.history.append({"role": "system", "content": self.system_prompt})

    def get_tool_responses(self, tool_calls):
        response_text = ""
        for tool_call in tool_calls:
            response_text += "\n\n#### Tool call:\n\n" + json.dumps(dict(tool_call.function), indent=2)
            function_name = tool_call.function.name
            function_to_call = self.tools_map[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            response_text += "\n\n#### Tool response:\n\n" + str(function_response or "")
            self.history.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })
        return response_text + "\n\n"

    def _call(self, prompt: str = "", prefill: str = "", tool_call_depth: int = 0) -> ModelResponse:
        assert not prefill or self.supports_assistant_prefill
        if prompt:
            self.history.append({"role": "user", "content": prompt})
        messages = (
            self.history
            if not prefill else
            self.history + [{"role": "assistant", "content": prefill}]
        )
        completion_args = {"tools": self.tool_schemas} if self.tool_schemas else {}
        response = completion(
            model=self.model,
            messages=messages,
            top_p=self.top_p,
            # top_k=self.top_k,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **completion_args
        )
        response_text = prefill + (response.choices[0].message.content or "")
        response.choices[0].message.content = response_text
        self.history.append(response.choices[0].message.model_dump())
        self.tokens.add(response.usage.prompt_tokens, response.usage.completion_tokens)

        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            response_text += self.get_tool_responses(tool_calls)
            if tool_call_depth < self.max_tool_calls:
                response_text += self._call(tool_call_depth=tool_call_depth + 1)

        return response_text

    def _call_stream(self, prompt: str = "", prefill: str = "", tool_call_depth: int = 0) -> ModelResponse:
        assert not prefill or self.supports_assistant_prefill
        if prompt:
            self.history.append({"role": "user", "content": prompt})
        messages = (
            self.history
            if not prefill else
            self.history + [{"role": "assistant", "content": prefill}]
        )
        completion_args = {"tools": self.tool_schemas} if self.tool_schemas else {}

        response = completion(
            model=self.model,
            messages=messages,
            top_p=self.top_p,
            # top_k=self.top_k,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            stream_options={"include_usage": True},
            **completion_args
        )

        yield prefill
        chunks = []
        for chunk in response:
            chunks.append(chunk)
            chunk_text = chunk.choices[0].delta.content
            if chunk_text:
                yield chunk_text

        response = stream_chunk_builder(chunks, messages=messages)
        self.history.append(response.choices[0].message.model_dump())
        self.tokens.add(response.usage.prompt_tokens, response.usage.completion_tokens)

        # tool_calls = response.choices[0].message.tool_calls
        # if tool_calls:
        #     response_text += self.get_tool_responses(tool_calls)
        #     yield response_text
        #     if tool_call_depth < self.max_tool_calls:
        #         for chunk in self._call_stream(tool_call_depth=tool_call_depth + 1):
        #             yield response_text + chunk

    def __call__(self, prompt: str = "", prefill: str = "") -> Union[str, Generator]:
        if not self.stream:
            response = self._call(prompt=prompt, prefill=prefill)
            logger.info(f"LlmChat response: {response}")
            logger.info(f"Token counts - Last: {self.tokens.last}, Total: {self.tokens.total}")
            return response
        else:
            return self._call_stream(prompt=prompt, prefill=prefill)


def run_chat_prompt(
    prompt_path: Annotated[str, typer.Argument(help="Path to a text file containing the prompt")],
    model: Annotated[str, typer.Option(help="LiteLLM model identifier")] = "claude-3-5-sonnet-20241022",
    temperature: Annotated[float, typer.Option(help="Sampling temperature")] = 0.0,
    max_tokens: Annotated[int, typer.Option(help="Maximum tokens to generate")] = 4096,
    stream: Annotated[bool, typer.Option(help="Stream output to stdout")] = False
):
    """Run an LLM chat session with a prompt from a file"""
    # Read prompt from file
    with open(prompt_path, "r") as f:
        prompt_text = f.read()

    # Initialize chat with config
    chat = LlmChat(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream
    )

    # Run the chat with the prompt from file
    if not stream:
        response = chat(prompt=prompt_text)
        print(response)
    else:
        for chunk in chat(prompt=prompt_text):
            print(chunk, flush=True, end="")
        print()


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(run_chat_prompt)
    app()