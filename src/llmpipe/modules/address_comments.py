"""python -m llmpipe.modules.address_comments --help"""
import yaml
import re
from typing import List, Annotated

from typer import Option, Argument
import typer

from llmpipe import LlmPromptForMany


revisor_config = """
model: {model}
temperature: {temperature}
verbose: {verbose}
task: Revise the document to address a single comment.
outputs:
  - name: thinking
    description: Begin by thinking step by step
  - name: search
    description: One or more lines from `document` to be replaced
    inputs:
      - name: document
        description: A document with inline comments within <comment> XML tags
    evaluations:
      - type: is_in_string_field
        value: document
        label: Exactly matches one or more lines from `document`, including formatting, indentation, newlines, and comment XML blocks.
  - name: replace
    description: The replacement text for the preceding `search`. Can be empty.
  - name: resolved
    description: The comment that was resolved
    inputs:
      - name: document
        description: A document with inline comments within <comment> XML tags
    evaluations:
      - type: is_in_string_field
        value: document
        label: Exactly matches the text (without XML) from one of the comments in `document`
details: |-
  Address a single comment by generating pairs of search and replace blocks. Comments can be addressed in any order.

  To move text from one place in a document to another, use two pairs of search and replace blocks, one to delete the text from the current location and a second to add it to the target location.

  One of the search-replace pairs should delete the resolved comment XML block from the document.

  Comments may contain a description of the content to be added.
footer: Generate a single <thinking> block, one or more pairs of <search> and <replace> blocks, and a single <resolved> block
"""


def address_comments(
    file: Annotated[str, Argument(help="The file to revise")],
    file_out: Annotated[str, Option(help="Output path. Will overwrite if not provided.")] = None,
    model: Annotated[str, Option(help="A litellm model identifier: https://docs.litellm.ai/docs/providers")] = "anthropic/claude-3-5-sonnet-20241022",
    temperature: Annotated[str, Option(help="The sampling temperature to use for generation")] = 0.,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    max_iters: Annotated[int, Option(help="Maximum number of iterations")] = 10
):
    """Address comments in a document."""
    with open(file, "r") as f:
        text = f.read()

    reviser = LlmPromptForMany(**yaml.safe_load(revisor_config.format(
        model=model,
        temperature=temperature,
        verbose=verbose
    )))
    if verbose:
        print(reviser.prompt)

    idx = 0
    while "<comment>" in text and idx < max_iters:
        idx += 1
        response = reviser(document=text)
        response = response | reviser.revise(document=text, **response)

        for search, replace in zip(response["search"], response["replace"]):
            text = text.replace(search, replace) if search else text

        pattern = f'<comment>\\s*{response["resolved"][0]}\\s*</comment>\\n*'
        text = re.sub(pattern, '', text, flags=re.DOTALL)

        with open(file_out or file, "w") as f:
            f.write(text)
        print(f"Addressed: {response['resolved'][0]}")
        print(f"Tokens used: {reviser.tokens.total}")


if __name__ == "__main__":
    typer.run(address_comments)
