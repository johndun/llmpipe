import os
import shutil
from pathlib import Path
from typing import Annotated

import git
import typer
from typer import Option


UNIVARIATE_SUMMARY_TASK = """\
script_name: univariate_summaries.py
task: Write an exploratory data analysis script that prints univariate summary statistics. Include missing value counts. Include distinct value counts. Include a table of frequency counts for fields with fewer than 20 distinct values.
"""


def initialize_repo(
    repo_path: Annotated[str, Option(help="Directory to initialize git repo")] = "~/ds_tmp"
):
    """Initialize an empty git repository in the specified directory.
    If the directory exists, it will be emptied. If not, it will be created.
    """
    # Expand user path and convert to Path object
    output_path = Path(os.path.expanduser(repo_path))
    
    # If directory exists, remove it and its contents
    if output_path.exists():
        shutil.rmtree(output_path)
    
    # Create fresh directory
    output_path.mkdir(parents=True)
    
    # Create artifacts subdirectory
    (output_path / "artifacts").mkdir()

    # Create notes subdirectory
    (output_path / "notes").mkdir()

    # Create univariate summaries path
    with open(output_path / "univariate_summaries_task.yaml", "w") as f:
        f.write(UNIVARIATE_SUMMARY_TASK)
    
    # Get current directory path
    current_dir = Path(__file__).parent
    
    # Copy template files from current directory
    shutil.copy(current_dir / "cli_script_template.py", output_path / "cli_script_template.py")
    
    # Initialize git repository
    git.Repo.init(output_path)
    
    typer.echo(f"Initialized empty git repository in {output_path}")


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(initialize_repo)
    app()
