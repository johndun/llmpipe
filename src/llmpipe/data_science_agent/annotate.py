from pathlib import Path
from typing import Annotated, Dict, List
import yaml
import json
import os
import random
import polars as pl
from itertools import chain
import typer
from typer import Option

from llmpipe.constants import DEFAULT_MODEL
from llmpipe.data import read_data, write_data
from llmpipe.prompt_module import PromptModule
from llmpipe.field import Input, Output, JsonlinesOutput


def run_annotation(
    prompt_module: PromptModule,
    samples: List[Dict],
    n_samples: int = None,
    num_proc: int = 1,
    allowed_labels: List[Dict] = None,
) -> List[Dict]:
    """Run annotation on a dataset using the provided config.

    Args:
        samples: List of samples to annotate
        n_samples: Number of random samples to process
        num_proc: Number of processes to use
        model: LiteLLM model identifier
        verbose: Stream output to stdout
        allowed_labels: List of allowed label dictionaries with 'label' and 'description' fields

    Returns:
        List of annotated samples
    """
    # Sample if requested
    if n_samples and n_samples > 0 and n_samples < len(samples):
        samples = random.sample(samples, n_samples)

    data = pl.from_dicts(samples).to_dict(as_series=False)

    # Process allowed classes if provided
    if allowed_labels:
        classes_md = "\n".join([f"- {c['label']}: {c['description']}" for c in allowed_labels])
        data["allowed_labels"] = [classes_md] * len(samples)

    # Run prompt and return results
    return pl.from_dict(prompt_module(**data, num_proc=num_proc)).to_dicts()


def annotate(
    data_path: Annotated[str, Option(help="Path to input dataset")] = "~/data/taskmaster2/taskmaster2_dialogs.jsonl",
    output_data_path: Annotated[str, Option(help="Path to save annotated dataset")] = "~/data/taskmaster2/taskmaster2_dialogs_annotated.jsonl",
    n_samples: Annotated[int, Option(help="Number of random samples to process")] = None,
    annotation_batch_size: Annotated[int, Option(help="Number of samples to annotate at one time")] = 1,
    num_proc: Annotated[int, Option(help="Number of processes to use")] = 1,
    model: Annotated[str, Option(help="LiteLLM model identifier")] = DEFAULT_MODEL,
    verbose: Annotated[bool, Option(help="Stream output to stdout")] = False,
    task: Annotated[str, Option(help="Annotation task prompt")] = "",
    context_field: Annotated[str, Option(help="The field to annotate")] = "",
    output_field: Annotated[str, Option(help="Name of the output field")] = "label",
    allowed_labels_path: Annotated[str, Option(help="Path to yaml file containing allowed labels")] = None,
):
    """Run annotation."""
    assert task and context_field
    data_path = str(Path(data_path).expanduser())
    output_data_path = str(Path(output_data_path).expanduser())

    # Load allowed labels if provided
    allowed_labels = None
    if allowed_labels_path:
        allowed_labels_path = str(Path(allowed_labels_path).expanduser())
        with open(allowed_labels_path, "r") as f:
            allowed_labels = yaml.safe_load(f)["labels"]

    os.makedirs(os.path.dirname(os.path.abspath(output_data_path)), exist_ok=True)

    id_field = "row_id"

    # Configure annotation prompt
    if annotation_batch_size == 1:
        output = Output(
            "label",
            "A label selected from `allowed_labels`",
            inputs=[
                Input(context_field, ""),
                Input("allowed_labels", "The set of allowed labels")
            ]
        )
        prompt = PromptModule(
            task=task,
            inputs=output.inputs,
            outputs=[output],
            model=model,
            verbose=verbose
        )
    else:
        output = JsonlinesOutput(
            "labels",
            "A table with annotated labels",
            fields=[
                Output(id_field, "An id from `annotation_inputs`"),
                Output("label", "A label selected from `allowed_labels`")
            ]
        )
        prompt = PromptModule(
            task=task,
            inputs=[
                Input("annotation_inputs", "A table with annotation inputs"),
                Input("allowed_labels", "The set of allowed labels")
            ],
            outputs=[output],
            model=model,
            verbose=verbose
        )

    print("\nStarting annotation phase...")
    print(f"Using model: {model}")
    print(f"Annotation batch size: {annotation_batch_size}")
    # Load the data
    samples = read_data(data_path, as_df=True).with_row_index(id_field).to_dicts()

    if not verbose:
        from datasets.utils.logging import disable_progress_bar
        disable_progress_bar()

    if annotation_batch_size == 1:
        annotated_samples = run_annotation(
            prompt_module=prompt,
            samples=samples,
            n_samples=n_samples,
            num_proc=num_proc,
            allowed_labels=allowed_labels
        )
        annotated_samples = pl.from_dicts(annotated_samples)
    else:
        batches = []
        for i in range(0, len(samples), annotation_batch_size):
            batch = [{k: x[k] for k in (id_field, context_field)} for x in samples[i: i + annotation_batch_size]]
            batches.append("\n".join([json.dumps(x) for x in batch]))

        batched_samples = [{"annotation_inputs": x} for x in batches]

        batch_annotated_samples = run_annotation(
            prompt_module=prompt,
            samples=batched_samples,
            n_samples=n_samples,
            num_proc=num_proc,
            allowed_labels=allowed_labels
        )

        labels = list(chain(*[x["labels"] for x in batch_annotated_samples if x["labels"] is not None]))
        annotated_samples = pl.from_dicts(samples).join(
            pl.from_dicts(labels).with_columns(pl.col(id_field).cast(pl.UInt32).alias(id_field)),
            on=id_field, how="inner"
        )

    for k in ("thinking", "allowed_labels"):
        if k in annotated_samples.columns:
            annotated_samples = annotated_samples.drop(k)

    annotated_samples = annotated_samples.rename({"label": output_field})
    annotated_samples = annotated_samples.to_dicts()

    print(f"Writing output to {output_data_path}")
    write_data(annotated_samples, output_data_path)


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(annotate)
    app()
