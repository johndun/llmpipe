import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL

from llmpipe.data_science_agent.collect_files import collect_files


def generate_research_summary(
    repo_path: Annotated[str, Option(help="Working directory")],
    output_path: Annotated[str, Option(help="Path to save the outputs")] = None,
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
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
        txt.append(f"### {k}\n\n{v}")
    eda_results = "\n\n".join(txt)

    module = PromptModule(
        task="Write a document summarizing the results from exploratory data analyses. Use markdown headers for organization. Tone should be scientific, professional, and explanatory. Use a narrative format with minimal lists. Liberally incorporate statistics, metrics and tables",
        inputs=[
            Input("data_samples", "A small set of examples from a dataset"),
            Output("data_schema", "The data schema as a markdown table"),
            Input("eda_results", "Current data analysis results"),
        ],
        outputs=[
            Output("review", "Begin by reviewing the provided inputs"),
            Output("outline", "A draft outline"),
            Output("document", "A research summary document")
        ],
        model=model,
        verbose=verbose
    )
    if verbose:
        print(module.prompt)
    response = module(
        data_samples=data_samples,
        data_schema=data_schema,
        eda_results=eda_results
    )

    # Save if output path provided
    doc = response["document"] + "\n\n# Appendix 1: Exploratory Data Analysis Results\n\n" + eda_results
    if output_path:
        with open(output_path, "w") as f:
            f.write(doc)
        print(f"\nSaved to {output_path}")
    else:
        print(doc)

if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(generate_research_summary)
    app()
