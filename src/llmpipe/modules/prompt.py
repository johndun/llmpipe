from typing import Annotated

import typer
from typer import Option, Argument

from llmpipe import LlmChat


def prompt(
        input_file_path: Annotated[str, Argument(help="File containing a prompt")] = None,
        output_file_path: Annotated[str, Option(help="Path to save response. If not provided, response will be appended to the input file")] = None,
        verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
        model: Annotated[str, Option(help="A LiteLLM model identifier")] = "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"
):
    """Load a file containing a prompt and append LLM response."""

    # If an output file path was not provided, set it to input file path
    output_file_path = output_file_path or input_file_path

    # Read the prompt from the input file path
    with open(input_file_path, "r") as f:
        prompt = f.read()

    # Initialize the chat module instance
    chat = LlmChat(model=model, stream=verbose)

    # Generate the response
    response = chat(prompt)
    if verbose:
        # Print the response stream
        response_text = ""
        for chunk in response:
            print(chunk, flush=True, end="")
            response_text += chunk
        print()
    else:
        response_text = response

    # Write or append the output to the target output file location
    with open(
            output_file_path,
            "a" if output_file_path == input_file_path else "w"
    ) as f:
        f.write("\n\n")
        f.write(response_text)


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals = False)
    app.command()(prompt)
    app()
