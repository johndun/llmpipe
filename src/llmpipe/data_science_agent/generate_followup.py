import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL

from llmpipe.data_science_agent.collect_files import collect_files
from llmpipe.data_science_agent.generate_eda_script import generate_eda_script


def generate_followup(
    repo_path: Annotated[str, Option(help="Working directory")],
    data_path: Annotated[str, Option(help="Dataset path")],
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    max_revisions: Annotated[int, Option(help="Maximum number of revisions")] = 0,
):
    """Draft followups using EDA results."""
    # Read the schema
    with open(f"{repo_path}/data_schema.md", "r") as f:
        data_schema = f.read()

    # Read the data samples
    with open(f"{repo_path}/sample_data.md", "r") as f:
        data_samples = f.read()

    logs = collect_files(f"{repo_path}/notes")
    txt = []
    for k, v in logs.items():
        txt.append(f"<{k}>\n{v}\n</{k}>")
    eda_results = "\n\n".join(txt)

    module = PromptModule(
        task="Propose a follow up exploratory data analysis based on current results. Follow up analyses should be simple enough that they can be implemented in a single, manageable script. Only base python3.10 packages, along with pandas, scipy, nltk, and numpy may be used. Only text-based summaries for now (so no graphs).",
        inputs=[
            Input("data_samples", "A small set of examples from a dataset"),
            Input("data_schema", "The data schema as a markdown table"),
            Input("eda_results", "Current data analysis results"),
        ],
        outputs=[
            Output("thinking", "Begin by thinking step by step"),
            Output("followup_task", "A follow up exploratory data analysis task")
        ],
        model=model,
        verbose=verbose
    )
    if verbose:
        print(module.prompt)
        print(data_schema)
        print(data_samples)
        print(eda_results)
    response = module(
        data_samples=data_samples,
        data_schema=data_schema,
        eda_results=eda_results
    )
    followup_task = response["followup_task"]
    generate_eda_script(
        task=followup_task,
        data_path=data_path,
        repo_path=repo_path,
        model=model,
        verbose=verbose,
        max_revisions=2
    )

if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(generate_followup)
    app()
