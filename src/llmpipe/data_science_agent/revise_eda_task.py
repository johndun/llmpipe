import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL


def revise_eda_task(
    task: Annotated[str, Option(help="Task")],
    input_path: Annotated[str, Option(help="Input path")],
    output_path: Annotated[str, Option(help="Path to save output")] = None,
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL
):
    """Draft document text using EDA results."""
    # Read the data
    with open(input_path, "r") as f:
        eda_results = f.read()

    module = PromptModule(
        task="Evaluate exploratory data analysis results. Revise the task to improve the results, or finalize. The revised task should be similar in scope to the original task. The revised task should be self contained and include any necessary context from the original task. Limit tasks to analyses that can be implemented with pandas, scipy, nltk, and numpy.",
        inputs=[
            Input("task", "A data analysis task"),
            Input("eda_results", "Exploratory data analysis results"),
        ],
        outputs=[
            Output("thinking", "Begin by thinking step by step"),
            Output("revised_task", "A revised data analysis task. Contains the text FINALIZE if no revision is needed."),
        ],
        model=model
    )
    response = module(eda_results=eda_results)

    # Save if output path provided
    if output_path:
        with open(output_path, "w") as f:
            f.write(response["revised_task"])
        print(f"\nSaved to {output_path}")
    else:
        print(response["revised_task"])

if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(revise_eda_task)
    app()
