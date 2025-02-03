"""
Template for generating annotation scripts.

This template provides a basic structure for creating annotation scripts
using the llmpipe annotation functionality.

Generally, template is to be used with a yaml file containing a set of labels
"""

from pathlib import Path
import typer
from typer import Option
from typing import Annotated

from llmpipe.constants import DEFAULT_MODEL
from llmpipe.data_science_agent.annotate import annotate


def main(
    data_path: Annotated[str, Option(help="Path to input dataset")] = "data/input.jsonl",
    output_data_path: Annotated[str, Option(help="Path to save annotated dataset")] = "data/output.jsonl",
    n_samples: Annotated[int, Option(help="Number of random samples to process")] = 4,
    annotation_batch_size: Annotated[int, Option(help="Number of samples to annotate at one time")] = 1,
    num_proc: Annotated[int, Option(help="Number of processes to use")] = 1,
    model: Annotated[str, Option(help="LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    task: Annotated[str, Option(help="Annotation task prompt")] = "",
    context_field: Annotated[str, Option(help="The field to annotate")] = "",
    context_field_description: Annotated[str, Option(help="Description of the annotation field")] = "",
    id_field: Annotated[str, Option(help="Field containing unique identifier for each row")] = "id",
    allowed_labels_path: Annotated[str, Option(help="Path to jsonlines file with allowed labels")] = None,
    use_cot: Annotated[bool, Option(help="Use chain of thought prompting")] = True
):
    """
    Run annotation on a dataset.
    
    This script provides a command-line interface for running annotations using llmpipe.
    It supports both single and batch annotation modes.
    """
    # Run annotation
    annotated_samples = annotate(
        data_path=data_path,
        output_data_path=output_data_path,
        n_samples=n_samples,
        annotation_batch_size=annotation_batch_size,
        num_proc=num_proc,
        model=model,
        verbose=verbose,
        task=task,
        context_field=context_field,
        context_field_description=context_field_description,
        id_field=id_field,
        allowed_labels_path=allowed_labels_path,
        use_cot=use_cot
    )

    print(f"\nAnnotation complete. Results saved to: {output_data_path}")
    return annotated_samples


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(main)
    app()
