from typing import Annotated
from pathlib import Path
import typer
from typer import Option

from llmpipe.data_science_agent.initialize_repo import initialize_repo
from llmpipe.data_science_agent.git_commit import git_commit
from llmpipe.data_science_agent.write_script import write_script
from llmpipe.constants import DEFAULT_MODEL




def initialize_project(
    repo_path: Annotated[str, Option(help="Directory to initialize project in")],
    data_path: Annotated[str, Option(help="Dataset path")],
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    use_cot: Annotated[bool, Option(help="Use chain of thought prompting")] = True
):
    """Initialize a project."""
    print("\n=== Initializing Project ===")
    
    print("\n1. Initializing git repository...\n")
    initialize_repo(
        repo_path=repo_path
    )

    print("\n2. Creating initial commit...\n")
    git_commit(
        repo_path=repo_path,
        commit_message="Initial commit"
    )

    print("\n3. Running univariate analysis...\n")
    write_script(
        task_file=f"{repo_path}/univariate_summaries_task.yaml",
        repo_path=repo_path,
        data_path=data_path,
        model=model,
        verbose=verbose,
        use_cot=use_cot,
        max_revisions=2
    )
    
    print("\n=== Project initialization complete! ===\n")



if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(initialize_project)
    app()
