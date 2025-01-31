from typing import Annotated
from pathlib import Path
import typer
from typer import Option

from llmpipe.data_science_agent.initialize_repo import initialize_repo
from llmpipe.data_science_agent.get_data_sample import get_data_sample
from llmpipe.data_science_agent.generate_data_schema import generate_data_schema
from llmpipe.data_science_agent.git_commit import git_commit
from llmpipe.constants import DEFAULT_MODEL


def initialize_project(
    repo_path: Annotated[str, Option(help="Directory to initialize project in")],
    data_path: Annotated[str, Option(help="Dataset path")],
    model: Annotated[str, Option(help="A LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
):
    """Initialize a project."""
    print("\n=== Initializing Project ===")
    
    print("\n1. Initializing git repository...")
    initialize_repo(
        repo_path=repo_path
    )
    
    print("\n2. Getting data samples...")
    get_data_sample(
        data_path=data_path,
        n_samples=3,
        output_path=f"{repo_path}/sample_data.md"
    )
    
    print("\n3. Generating data schema...")
    generate_data_schema(
        data_sample_path=f"{repo_path}/sample_data.md",
        output_path=f"{repo_path}/data_schema.md",
        model=model,
        verbose=verbose
    )
    
    print("\n4. Creating initial commit...")
    git_commit(
        repo_path=repo_path,
        commit_message="Initial commit"
    )
    
    print("\n=== Project initialization complete! ===\n")



if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(initialize_project)
    app()
