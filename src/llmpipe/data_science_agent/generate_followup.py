import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL

from llmpipe.data_science_agent.collect_files import collect_files
from llmpipe.data_science_agent.write_script import write_script


def generate_followup(
    repo_path: Annotated[str, Option(help="Working directory")],
    data_path: Annotated[str, Option(help="Dataset path")],
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    max_revisions: Annotated[int, Option(help="Maximum number of revisions")] = 0,
    use_cot: Annotated[bool, Option(help="Use chain of thought prompting")] = True
):
    """Draft followups using EDA results."""
    # Read the schema
    schema_raw = get_data_schema(data_path=data_path)
    schema = ""
    for field in schema_raw:
        schema += f"Field: {field['name']}\n"
        schema += f"  Type: {field['type']}\n"
        schema += f"  Nullable: {field['nullable']}\n"
        schema += "\n"

    # Read the data samples
    data_samples = get_data_sample(data_path=data_path)

    logs = collect_files(f"{repo_path}/notes")
    txt = []
    for k, v in logs.items():
        txt.append(f"<{k}>\n{v}\n</{k}>")
    results = "\n\n".join(txt)

    outputs=[
        Output("thinking", "Begin by thinking step by step"),
        Output("followup_task", "A follow up exploratory data analysis task")
    ]
    if "deepseek-reasoner" in model or not use_cot:
        outputs = [outputs[-1]]

    module = PromptModule(
        task="Propose a follow up exploratory data analysis based on current results. Follow up analyses should be simple enough that they can be implemented in a single, manageable script. Only base python3.10 packages, along with pandas, scipy, nltk,  numpy, matplotlib, and seaborn may be used.",
        inputs=[
            Input("data_samples", "A small set of examples from a dataset"),
            Input("data_schema", "The data schema as a markdown table"),
            Input("results", "Current data analysis results"),
        ],
        outputs=outputs,
        model=model,
        verbose=verbose
    )
    response = module(
        data_samples=data_samples,
        data_schema=schema,
        results=results
    )
    followup_task = response["followup_task"]
    write_script(
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
