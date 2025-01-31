import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL


def generate_data_schema(
    data_sample_path: Annotated[str, Option(help="Path to dataset samples")],
    output_path: Annotated[str, Option(help="Path to save the schema")] = None,
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
):
    """Print random samples from a dataset with truncated long values."""
    # Read the data
    with open(data_sample_path, "r") as f:
        data_sample = f.read()

    module = PromptModule(
        task="Generate a schema for a dataset as a markdown table. Columns should include name, type, and description.",
        inputs=[
            Input("data_samples", "A small set of examples from a dataset"),
        ],
        outputs=[
            Output("thinking", "Begin by thinking step by step"),
            Output("data_schema", "The data schema as a markdown table")
        ],
        model=model,
        verbose=verbose
    )
    response = module(data_samples=data_sample)

    # Save schema if output path provided
    if output_path:
        with open(output_path, "w") as f:
            f.write("The data schema:\n\n")
            f.write(response["data_schema"])
        print(f"\nSaved schema to {output_path}")
    else:
        print(response["data_schema"])

if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(generate_data_schema)
    app()
