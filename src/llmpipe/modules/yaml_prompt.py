"""
python -m llmpipe.modules.yaml_prompt --help
"""
import yaml

from datasets import Dataset
from typing import Annotated

import typer
from typer import Option, Argument

from acj_ai_research_tools.core import read_data, write_data

from llmpipe import LlmChat, LlmPrompt, LlmPromptForMany


def yaml_prompt(
        prompt_path: Annotated[str, Option(help="Path to a yaml file containing the prompt configuration")] = None,
        input_data_path: Annotated[str, Option(help="Dataset to run prompt on")] = None,
        output_data_path: Annotated[str, Option(help="Path to save processed dataset")] = None,
        prompt_for_many: Annotated[bool, Option(help="If true, use `LlmPromptForMany`")] = False,
        num_proc: Annotated[int, Option(help="Number of processes to use is dataset mode")] = 1,
        max_samples: Annotated[int, Option(help="Optional maximum number of samples to run")] = None,
        max_revisions: Annotated[int, Option(help="Maxumim number of revisions")] = 6,
        verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
        deterministic_only: Annotated[bool, Option(help="If true, only revise for deterministic evaluations")] = False,
        model: Annotated[str, Option(help="A LiteLLM model identifier")] = "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"
):
    """Load a file containing a prompt and append LLM response."""

    # Read the prompt
    with open(prompt_path, "r") as f:
        prompt_config = yaml.safe_load(f.read())

    # Initialize the prompt
    prompt_config["model"] = model
    prompt_config["verbose"] = verbose
    prompt = LlmPrompt(**prompt_config)
    if verbose:
        print(prompt.prompt)

    # Read the data
    samples = read_data(input_data_path)
    dataset = Dataset.from_list(samples)

    # Run the prompt
    dataset = dataset.map(
        lambda sample: sample | prompt(**sample),
        num_proc=num_proc,
        batched=False
    )
    dataset = dataset.map(
        lambda sample: sample | prompt.revise(
            **sample,
            max_revisions=max_revisions,
            deterministic_only=deterministic_only

        ),
        num_proc=num_proc,
        batched=False
    )

    # Write the output to the target output file location
    write_data(dataset.to_list(), output_data_path)


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals = False)
    app.command()(yaml_prompt)
    app()
