"""
Notes:

- All inputs should be Option type, even if no default is provided
- `run_small_lm_finetuning` can be used to finetune a huggingface model supported by AutoModelForSequenceClassification.
- This file serves only as a template. Significant modification may be needed for specific model training tasks.
"""
from typing import Annotated
from pathlib import Path

import typer
from typer import Option

from llmpipe import read_data, write_data
from llmpipe.data_science_agent.finetune import split_data, run_small_lm_finetuning


# Note the syntax for defining defaults.
def train_model(
    data_path: Annotated[str, Option(help="Input dataset")],
    output_basepath: Annotated[str, Option(help="Path to save artifacts")],
    model_path: Annotated[str, Option(help="Local or HuggingFace model path")] = "roberta-base",
    input_field: Annotated[str, Option(help="The field to use as input to the transformer")] = "text",
    label_field: Annotated[str, Option(help="The field to use as the target for the transformer")] = "label",
    num_epochs: Annotated[int, Option(help="Number of training epochs")] = 1,
    learning_rate: Annotated[float, Option(help="Learning rate")] = 0.00001,
    batch_size: Annotated[int, Option(help="Batch size for training and evaluation")] = 8,
    val_prop: Annotated[float, Option(help="The proportion of samples to use for validation")] = 0.2
):
    """Run a script on a dataset."""
    output_basepath = str(Path(output_basepath).expanduser())

    data = read_data(data_path)  # Infers file type; returns a list of dicts

    # Randomly shuffle a list of dictionaries and split it into sublists according to given proportions.
    print("\n1. Creating validation split...\n")
    train_data, val_data = split_data(data, proportions=[1-val_prop, val_prop])

    # Run finetuning
    print("\n2. Run fine tuning...\n")
    run_small_lm_finetuning(
        train_data=train_data,
        val_data=val_data,
        test_data=None,
        input_field=input_field,
        label_field=label_field,
        model_path=model_path,
        output_path=output_basepath,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        batch_size=batch_size
    )


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(train_model)
    app()
