import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL


def summarize_script_output(
    repo_path: Annotated[str, Option(help="Working directory")],
    script_name: Annotated[str, Option(help="Script name (with .py extension)")] = None,
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    use_cot: Annotated[bool, Option(help="Use chain of thought prompting")] = True
):
    """Draft document text using EDA results."""
    script_name = script_name[:-3]
    # Read the data
    with open(f"{repo_path}/artifacts/{script_name}/task.yaml", "r") as f:
        script_task = f.read()
    with open(f"{repo_path}/artifacts/{script_name}/output.log", "r") as f:
        script_log = f.read()
    with open(f"{repo_path}/{script_name}.py", "r") as f:
        script = f.read()
    with open(f"{repo_path}/data_schema.md", "r") as f:
        data_schema = f.read()

    outputs=[
        Output("thinking", "Begin by thinking step by step"),
        Output("document", "A document containing a detailed, comprehensive summary. No title.")
    ]
    if "deepseek-reasoner" in model or not use_cot:
        outputs = [outputs[-1]]

    module = PromptModule(
        task="Summarize the contents of an output log from a python script. Include no information other than what is in the script and the script log. For exmaple, if the log is empty, then just say that. Use markdown headers for organization. Incorporate all of the relevant information from the results. Focus on coverage of the content in the script log. Include tables where appropriate. Include methodology and explainers for any statistical techniques used. Include a section on insights and takeaways when appropriate.",
        inputs=[
            Input("data_schema", "The data schema"),
            Input("script_task", "The task associated with a python script"),
            Input("script", "A python script"),
            Input("script_log", "Output log from the script")

        ],
        outputs=outputs,
        model=model,
        verbose=verbose
    )
    response = module(
        data_schema=data_schema,
        script_log=script_log,
        script_task=script_task,
        script=script
    )

    output_path = f"{repo_path}/notes/{script_name}.md"
    with open(output_path, "w") as f:
        f.write(response["document"])
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(summarize_script_output)
    app()
