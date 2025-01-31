import os
import shutil
from pathlib import Path
from typing import Annotated

import git
import typer
from typer import Option


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
    
    # Create logs subdirectory
    (output_path / "logs").mkdir()

    # Create notes subdirectory
    (output_path / "notes").mkdir()
    
    # Get current directory path
    current_dir = Path(__file__).parent
    
    # Copy template files from current directory
    shutil.copy(current_dir / "cli_script_template.py", output_path / "cli_script_template.py")
    shutil.copy(current_dir / "data_io_template.py", output_path / "data_io_template.py")
    
    # Initialize git repository
    git.Repo.init(output_path)
    
    typer.echo(f"Initialized empty git repository in {output_path}")


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(initialize_repo)
    app()
