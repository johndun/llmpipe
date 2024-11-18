import yaml
from typing import List, Annotated

from typer import Option, Argument
import typer

from llmpipe import LlmPrompt


reviser_config = """
model: {model}
temperature: {temperature}
task: Revise a document based on inline comments
inputs:
  - name: document
    description: A document with inline comments with <comment> XML tags
outputs:
  - name: thinking
    description: Begin by thinking step by step
  - name: revised
    description: The revised document
    evaluations:
      - type: not_contains
        value:
          - "<comment>"
  - name: commit_message
    description: A single sentence message that describes the changes
"""


def revise_document(
    file: Annotated[str, Argument(help="The file to revise")],
    model: Annotated[str, Option(help="A litellm model identifier: https://docs.litellm.ai/docs/providers")] = "anthropic/claude-3-5-sonnet-20241022",
    temperature: Annotated[str, Option(help="The sampling temperature to use for generation")] = 0.
):
    """Revise a document containing comments within <comment> XML tags."""
    with open(file, "r") as f:
        text = f.read()
    reviser = LlmPrompt(**yaml.safe_load(reviser_config.format(model=model, temperature=temperature)))
    response = reviser(document=text)
    print(response)
    response = reviser.revise(document=text, revised=response["revised"])
    print(response)
    with open(file, "w") as f:
        f.write(response["revised"])


if __name__ == "__main__":
    typer.run(revise_document)
