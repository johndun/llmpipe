"""
A template for scripts to perform LLM-based data annotation.

This template provides a basic structure for creating annotation scripts using typer and the llmpipe annotation functionality.

The annotate method from llmpipe provides an interface to conduct annotation. A dataset containing the annotated labels will be saved to output_data_path.

Inputs:

- data_path: Path to input dataset
- output_data_path: Path to save annotated dataset
- task: Annotation task prompt
- allowed_labels_path: Optional path to yaml file containing allowed labels. File should contain a single top level key 'labels' with a list of dictionaries with 'label' and 'description' fields.
- context_field: The field to annotate
- output_field: Name of the output field in the resulting dataset.
- n_samples: An optional number of random samples to process.
- annotation_batch_size: Number of samples to annotate at one time. Defaults to 1.
- num_proc: Number of processes to use. Defaults to 1.
- model: LiteLLM model identifier. Defaults to DEFAULT_MODEL.
- verbose: Stream output to stdout. Defaults to False.

Additional Guidelines and Rules:

- Update the defaults below with more appropriate ones based on the paths and data schema provided
- Data paths should be absolute paths. The allowed labels yaml file should be in the same directory as the script.
- Be careful when constructing yaml files. Enclose longer or more complex descriptions in double quotes, or use multiline syntax.
"""

from pathlib import Path
import typer
from typer import Option
from typing import Annotated

from llmpipe.constants import DEFAULT_MODEL
from llmpipe.data_science_agent.annotate import annotate


# Note the syntax for defining defaults.
def annotate_data(
    data_path: Annotated[str, Option(help="Path to input dataset")] = "~/data/input.jsonl",
    output_data_path: Annotated[str, Option(help="Path to save annotated dataset")] = "~/data/output.jsonl",
    # A description of the annotation task to be used at the top of the annotation prompt
    task: Annotated[str, Option(help="Annotation task prompt")] = "...",
    # An optional yaml file containing allowed labels. Annotation will be free form if not provided.
    allowed_labels_path: Annotated[str, Option(help="Path to jsonlines file with allowed labels")] = None,
    context_field: Annotated[str, Option(help="The field containing the inputs to annotate")] = "",
    output_field: Annotated[str, Option(help="The field name for the annotations")] = "label",
    n_samples: Annotated[int, Option(help="Number of random samples to process")] = 4,
    annotation_batch_size: Annotated[int, Option(help="Number of samples to annotate at one time")] = 1,
    num_proc: Annotated[int, Option(help="Number of processes to use")] = 1,
    model: Annotated[str, Option(help="LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
):
    """
    Run annotation on a dataset.
    
    This script provides a command-line interface for running annotations using llmpipe.
    It supports both single and batch annotation modes.
    """
    # Run annotation
    annotate(
        data_path=data_path,
        output_data_path=output_data_path,
        task=task,
        allowed_labels_path=allowed_labels_path,
        context_field=context_field,
        output_field=output_field,
        n_samples=n_samples,
        annotation_batch_size=annotation_batch_size,
        num_proc=num_proc,
        model=model,
        verbose=verbose
    )
    print(f"\nAnnotation complete. Results saved to: {output_data_path}")


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(annotate_data)
    app()
