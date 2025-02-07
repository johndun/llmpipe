"""
Template for exploratory data analysis python scripts.

- All inputs should have defaults. Update the defaults with more appropriate ones based on the paths and data schema provided. Data paths should be absolute paths.
- Only create charts, graphs or datasets when explicitly asked to. Prioritize printing the outputs needed by the task. These printed outputs should be clearly labeled.
- Small, non-dataset outputs, such as graph image files, should be saved to the path given by `output_basepath`. All artifacts should have fixed filenames. DO NOT use timestamps in artifact file names.
- Only base python3.10 packages, along with: pandas, scipy, numpy, matplotlib, seaborn, transformers, torch, datasets. Do not use any additional packages that need to be installed!
"""
import os
import pathlib
from typing import Annotated

import typer
from typer import Option

from llmpipe import read_data


LOG_PATH = "artifacts/" + pathlib.Path(__file__).stem
os.makedirs(LOG_PATH, exist_ok=True)


# Note the syntax for defining defaults.
def example_script(
        data_path: Annotated[str, Option(help="Input dataset")] = "~/data/dat.jsonl",
        output_basepath: Annotated[str, Option(help="Path to save (non-dataset) artifacts")] = LOG_PATH
):
    """Run a script on a dataset."""
    data = read_data(data_path)  # Infers file type; returns a list of dicts
    ...


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(example_script)
    app()
