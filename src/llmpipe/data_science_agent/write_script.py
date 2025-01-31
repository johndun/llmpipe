import os
import shutil
import subprocess
from typing import Annotated

import git
import typer
from typer import Option

from llmpipe.data_science_agent.summarize_script_output import summarize_script_output
from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL


def run_command(command_str: str, working_dir: str = "."):
    try:
        subprocess.run(
            command_str,
            shell=True,
            capture_output=False,
            text=True,
            cwd=working_dir
        )
        return None

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit status {e.returncode}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def run_aider(
    message_file: Annotated[str, Option(help="Message file to send to aider")],
    script_path: Annotated[str, Option(help="Script name (or path relative to repo_path)")],
    working_dir: Annotated[str, Option(help="Working directory to run the command in")],
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL
):
    """
    Executes a command line script and returns its output.

    Args:
        message_file (str): Message to send to aider.
        working_dir (str): The directory to run the command in.
    """
    command_str = f"""aider --map-tokens 500 --no-analytics --no-show-model-warnings --stream --model {model} --message-file {message_file} --yes --read cli_script_template.py --read data_io_template.py {script_path}"""
    run_command(command_str, working_dir)


AIDER_MESSAGE_TEMPLATE = """\
Write a python script to complete a task.

Script inputs:

- data-path: Script should input a single dataset (schema defined below, no default).
- output-basepath: Directory in which to save script outputs, such as graph images. Defaults to artifacts/{script_name}
- Script may have additional command line arguments. These should all have defaults.

Outputs:

- Printed outputs should be clearly labeled.
- If the task requires creating charts or graphs, they should be created in `output_basepath`.
- Artifacts should have fixed filenames. DO NOT use timestamps in artifact file names.

Guidelines:

- Follow any implementation patterns provided to you in read-only _template.py files.
- Make sure to: `os.makedirs(output_basepath, exist_ok=True)`
- Only base python3.10 packages, along with pandas, scipy, nltk, numpy, matplotlib, and seaborn may be used.
- Only create charts, graphs, or other data artifaccts when explicitly asked to. Print the outputs needed by the task.

<task>
{task}
</task>

script_name: {script_name}
data_path: {data_path}

data_schema:

{schema}

data_samples:

{data_samples}
"""


def write_script(
    task: Annotated[str, Option(help="Task (ignored if task_file is provided)")],
    repo_path: Annotated[str, Option(help="Working directory")],
    data_path: Annotated[str, Option(help="Dataset path")],
    script_name: Annotated[str, Option(help="Script name (with .py extension)")] = None,
    task_file: Annotated[str, Option(help="Optional file containing task description")] = None,
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    max_revisions: Annotated[int, Option(help="Maximum number of revisions")] = 0
):
    """Generate detailed requirements for a data science EDA task using an LLM."""
    # Read task from file if specified
    if task_file:
        with open(task_file, "r") as f:
            task = f.read()

    # Read the schema
    with open(f"{repo_path}/data_schema.md", "r") as f:
        schema = f.read()

    # Read the data samples
    with open(f"{repo_path}/sample_data.md", "r") as f:
        data_samples = f.read()

    # Generate a script name
    if not script_name:
        script_name_module = PromptModule(
            task="Given a data science task, generate a python script name (with .py extension).",
            inputs=[Input("task", "A data science task")],
            outputs=[Output("script_name", "Python script name")],
            model=model,
            verbose=verbose
        )
        script_name = script_name_module(task=task)["script_name"]

    assert script_name

    # Write the script
    message = AIDER_MESSAGE_TEMPLATE.format(
        task=task,
        data_path=data_path,
        schema=schema,
        script_name=script_name,
        data_samples=data_samples
    )
    if verbose:
        print(message)
    message_file = f"{repo_path}/prompt.txt"
    with open(message_file, "w") as f:
        f.write(message)
    run_aider(
        message_file=message_file,
        working_dir=repo_path,
        model=model,
        script_path=script_name
    )

    # Run the script and write the output to a log file
    script_name_stem = script_name[:-3]
    log_dir = os.path.join(repo_path, "artifacts", script_name_stem)
    log_path = os.path.join(log_dir, "output.log")
    task_path = os.path.join(log_dir, "task.md")
    log_path_rel = os.path.join("artifacts", script_name_stem, "output.log")

    os.makedirs(log_dir, exist_ok=True)
    
    # Write task to task.md
    with open(task_path, "w") as f:
        f.write(task)
    
    # Run script and write output to artifacts/scriptname/output.log
    run_command(f"python {script_name} --data-path {data_path} > {log_path_rel} 2>&1", repo_path)

    # Debug and revise
    last_git_hash = git.Repo(repo_path).head.commit.hexsha
    n_tries = 0
    bugfree = False
    while not bugfree and n_tries < max_revisions:
        bugfix_cmd = f"aider --map-tokens 500 --no-analytics --no-show-model-warnings --stream --model {model} --message \"Review the script outputs and fix errors encountered. Do not make efficiency or minor formatting changes. Do not address warnings.\" --yes --read {log_path_rel} {script_name} data_schema.md"
        run_command(bugfix_cmd, repo_path)
        new_git_hash = git.Repo(repo_path).head.commit.hexsha
        if new_git_hash == last_git_hash:
            bugfree = True
        else:
            run_command(f"python {script_name} --data-path {data_path} > {log_path_rel} 2>&1", repo_path)
            last_git_hash = new_git_hash
            n_tries += 1

    summarize_script_output(
        repo_path=repo_path,
        script_name=script_name,
        model=model,
        verbose=verbose
    )


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(write_script)
    app()
