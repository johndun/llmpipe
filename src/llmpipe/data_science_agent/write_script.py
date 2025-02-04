import json
import os
import shutil
import subprocess
import yaml
from typing import Annotated

import git
import typer
from typer import Option

from llmpipe.data_science_agent.get_data_sample import get_data_sample
from llmpipe.data_science_agent.get_data_schema import get_data_schema
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
    script_template: Annotated[str, Option(help="The script template to include in the aider command")] = "cli_script_template.py",
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL
):
    """
    Executes a command line script and returns its output.

    Args:
        message_file (str): Message to send to aider.
        working_dir (str): The directory to run the command in.
    """
    command_str = f"""aider --no-analytics --no-show-model-warnings --stream --model {model} --message-file {message_file} --yes --read {script_template} {script_path}"""
    run_command(command_str, working_dir)


SCRIPT_TEMPLATE_SELECTION_TASK = """\
Given a task, select the most appropriate python script template:

finetune_template.py: A template for ML model training and fine tuning tasks.
annotation_script_template.py: A template for scripts to perform LLM-based data annotation.
eda_script_template.py: Template for exploratory data analysis python scripts.
data_transform_script_template.py: Template for data transformation python scripts.
"""

AIDER_MESSAGE_TEMPLATE = """\
Write a python script to complete a task. Follow any implementation patterns provided to you in read-only _template.py files.

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
    repo_path: Annotated[str, Option(help="Working directory")],
    data_path: Annotated[str, Option(help="Dataset path")],
    task: Annotated[str, Option(help="Task (ignored if task_file is provided)")] = "",
    script_name: Annotated[str, Option(help="Script name (with .py extension)")] = None,
    task_file: Annotated[str, Option(help="Optional yaml file containing parameters")] = None,
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    max_revisions: Annotated[int, Option(help="Maximum number of revisions")] = 0
):
    """Generate detailed requirements for a data science EDA task using an LLM."""
    assert task or task_file
    # Read task from file if specified
    if task_file:
        with open(task_file, "r") as f:
            config = yaml.safe_load(f)
            task = config["task"]
            script_name = config.get("script_name", script_name)

    # Read the schema
    schema_raw = get_data_schema(data_path=data_path)
    schema = ""
    for field in schema_raw:
        schema += f"Field: {field['name']}\n"
        schema += f"  Type: {field['type']}\n"
        schema += f"  Nullable: {field['nullable']}\n"
        schema += "\n"

    # Read the data samples
    data_samples = json.dumps(get_data_sample(data_path=data_path), indent=2)

    # Generate a script name
    if not script_name:
        script_name_module = PromptModule(
            task="Given a task to write a python script, generate a name for the script (with .py extension).",
            inputs=[Input("task", "A task")],
            outputs=[Output("script_name", "Python script name")],
            model=model,
            verbose=verbose
        )
        script_name = script_name_module(task=task)["script_name"]
    assert script_name

    # Select the best script template
    template_selection_module = PromptModule(
        task=SCRIPT_TEMPLATE_SELECTION_TASK,
        inputs=[Input("task", "A task")],
        outputs=[Output("script_template", "Python script template. Must exactly match one of the python template file names.")],
        model=model,
        verbose=verbose
    )
    script_template = template_selection_module(task=task)["script_template"]
    assert script_template

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
        script_path=script_name,
        script_template=script_template
    )

    # Run the script and write the output to a log file
    script_name_stem = script_name[:-3]
    log_dir = os.path.join(repo_path, "artifacts", script_name_stem)
    log_path = os.path.join(log_dir, "output.log")
    task_path = os.path.join(log_dir, "task.yaml")
    log_path_rel = os.path.join("artifacts", script_name_stem, "output.log")

    os.makedirs(log_dir, exist_ok=True)
    
    # Write task to task.yaml
    with open(task_path, "w") as f:
        f.write(yaml.dump({
            "task": task,
            "script_name": script_name
        }, default_flow_style=False, width=float('inf')))
    
    # Run script and write output to artifacts/scriptname/output.log
    run_command(f"python {script_name} --data-path {data_path} > {log_path_rel} 2>&1", repo_path)

    # Debug and revise
    last_git_hash = git.Repo(repo_path).head.commit.hexsha
    n_tries = 0
    bugfree = False
    while not bugfree and n_tries < max_revisions:
        # Get list of image files in log directory
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.gif']:
            image_files.extend([os.path.join("artifacts", script_name_stem, f) 
                              for f in os.listdir(log_dir) 
                              if f.lower().endswith(ext)])
        image_files_str = ' '.join(image_files[:4])
        
        bugfix_cmd = f"aider --no-analytics --no-show-model-warnings --stream --model {model} --message \"Review the script outputs and fix errors encountered. Do not make efficiency or minor formatting changes. Do not address warnings.\" --yes --read {log_path_rel} {script_name} {image_files_str}"
        run_command(bugfix_cmd, repo_path)
        new_git_hash = git.Repo(repo_path).head.commit.hexsha
        if new_git_hash == last_git_hash:
            bugfree = True
        else:
            run_command(f"python {script_name} --data-path {data_path} > {log_path_rel} 2>&1", repo_path)
            last_git_hash = new_git_hash
            n_tries += 1

    if script_template in("eda_script_template.py", "finetune_template.py"):
        summarize_script_output(
            repo_path=repo_path,
            data_path=data_path,
            script_name=script_name,
            model=model,
            verbose=verbose
        )


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(write_script)
    app()
