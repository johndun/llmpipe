from pathlib import Path
from typing import Annotated, Dict, List
import random
import yaml

import typer
from typer import Option
import polars as pl

from llmpipe.constants import DEFAULT_MODEL
from llmpipe.prompt_module import PromptModule
from llmpipe.data import read_data, write_data


def run_annotation(
    config: Dict,
    samples: List[Dict],
    n_samples: int = None,
    num_proc: int = 1,
    model: str = DEFAULT_MODEL,
    verbose: bool = False,
    allowed_labels: List[Dict] = None,
) -> List[Dict]:
    """Run annotation on a dataset using the provided config.
    
    Args:
        config: Prompt configuration dictionary
        samples: List of samples to annotate
        n_samples: Number of random samples to process
        num_proc: Number of processes to use
        model: LiteLLM model identifier
        verbose: Stream output to stdout
        allowed_labels: List of allowed label dictionaries with 'label' and 'description' fields
        
    Returns:
        List of annotated samples
    """
    # Update config with runtime parameters
    config["model"] = model
    config["verbose"] = verbose
    
    # Initialize prompt
    prompt = PromptModule(**config)
    if verbose:
        print(prompt.prompt)
    
    # Sample if requested
    if n_samples is not None:
        n_samples = min(n_samples, len(samples))
        samples = random.sample(samples, n_samples)

    data = pl.from_dicts(samples).to_dict(as_series=False)
    
    # Process allowed classes if provided
    if allowed_labels:
        classes_md = "\n".join([f"- {c['label']}: {c['description']}" for c in allowed_labels])
        data["allowed_labels"] = [classes_md] * len(samples)
    
    # Run prompt and return results
    return pl.from_dict(prompt(**data, num_proc=num_proc)).to_dicts()


def annotate(
    prompt_yaml_path: Annotated[str, Option(help="Path to yaml file with prompt config")] = "scripts/ex_annotation_prompt.yaml",
    input_data_path: Annotated[str, Option(help="Path to input dataset")] = "~/data/taskmaster2/taskmaster2_dialogs.jsonl",
    output_data_path: Annotated[str, Option(help="Path to save annotated dataset")] = "~/data/taskmaster2/taskmaster2_dialogs_annotated.jsonl",
    n_samples: Annotated[int, Option(help="Number of random samples to process")] = None,
    num_proc: Annotated[int, Option(help="Number of processes to use")] = 1,
    model: Annotated[str, Option(help="LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    allowed_labels_path: Annotated[str, Option(help="Path to jsonlines file containing allowed labels")] = None
):
    """CLI entry point to run annotation on a dataset."""
    # Expand user paths
    input_data_path = str(Path(input_data_path).expanduser())
    output_data_path = str(Path(output_data_path).expanduser())
    
    # Load config
    with open(prompt_yaml_path) as f:
        config = yaml.safe_load(f)
    
    # Load data
    samples = read_data(input_data_path)
    
    # Load allowed labels if provided
    allowed_labels = None
    if allowed_labels_path:
        allowed_labels_path = str(Path(allowed_labels_path).expanduser())
        allowed_labels = read_data(allowed_labels_path)
    
    # Run annotation
    results = run_annotation(
        config=config,
        samples=samples,
        n_samples=n_samples,
        num_proc=num_proc,
        model=model,
        verbose=verbose,
        allowed_labels=allowed_labels
    )
    
    # Save results
    write_data(results, output_data_path)


def main():
    """CLI entry point."""
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(annotate)
    app()


if __name__ == "__main__":
    main()
