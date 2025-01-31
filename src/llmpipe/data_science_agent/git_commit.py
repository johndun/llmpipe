import os
from pathlib import Path
from typing import Annotated

import git
import typer
from typer import Option


def git_commit(
    commit_message: Annotated[str, Option(help="Commit message for the changes")],
    repo_path: Annotated[str, Option(help="Path to git repository")] = "~/test_repo"
):
    """Commit all current changes in the specified git repository.
    
    Args:
        commit_message: Message to use for the commit
        repo_path: Path to the git repository
    """
    # Expand user path and convert to Path object
    repo_path = Path(os.path.expanduser(repo_path))
    
    if not repo_path.exists():
        raise typer.BadParameter(f"Repository path {repo_path} does not exist")
        
    try:
        # Open existing repo
        repo = git.Repo(repo_path)
        
        # Add all changes
        repo.git.add(A=True)  # equivalent to 'git add -A'
        
        # Commit changes
        repo.index.commit(commit_message)
        
        typer.echo(f"Successfully committed changes with message: {commit_message}")
        
    except git.InvalidGitRepositoryError:
        raise typer.BadParameter(f"Not a valid git repository: {repo_path}")
    except Exception as e:
        raise typer.BadParameter(f"Error committing changes: {str(e)}")


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(git_commit)
    app()
