"""
Template for data transformation python scripts.

- All inputs should have defaults. Update the defaults with more appropriate ones based on the paths and data schema provided. Data paths should be absolute paths.
- Dataset outputs should be saved to the same directory containing the input data
- Only base python3.10 packages, along with: pandas, scipy, nltk, numpy, transformers, torch, datasets. Do not use any additional packages that need to be installed!
"""
import os
import pathlib
from typing import Annotated

import typer
from typer import Option

from llmpipe import read_data, write_data


LOG_PATH = "artifacts/" + pathlib.Path(__file__).stem
os.makedirs(LOG_PATH, exist_ok=True)


# Note the syntax for defining defaults.
def example_script(
        data_path: Annotated[str, Option(help="Input dataset")] = "~/data/dat.jsonl",
        ...
        # verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
):
    """Run a script on a dataset."""
    data = read_data(data_path)  # Infers file type; returns a list of dicts

    ...


    output_data_path = os.path.dirname(data_path) + "/output.jsonl"  # or csv or txt
    print(f"Results saved to: {output_data_path}")
    # write_data takes a list of dicts and a path
    write_data(data, output_data_path)


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(example_script)
    app()
