"""
Notes:

- Inputs:
    - All inputs should be Option type, even if no default is provided
    - Script should input a single dataset as `data_path`. The schema is provided below.
    - Script may have additional command line arguments. These should all have defaults.
- Outputs:
    - Non-dataset small script outputs, such as graph image files, should be saved to the path given by `output_basepath`. The default value for `output_basepath` should point to artifacts/{script_name} (without the .py extension). Artifacts should have fixed filenames. DO NOT use timestamps in artifact file names.
    - Any dataset outputs should be saved in the same directory containing the input data (`os.path.dirname(data_path)`).
    - Only create charts, graphs, or datasets when explicitly asked to. Print the outputs needed by the task. Printed outputs should be clearly labeled.
- Other:
    - Only base python3.10 packages, along with: pandas, scipy, nltk, numpy, matplotlib, seaborn, transformers, torch, datasets. Do not use any additional packages that need to be installed!
"""
from typing import Annotated

import typer
from typer import Option

from llmpipe import read_data, write_data


def example_script(
        data_path: Annotated[str, Option(help="Input dataset")],
        output_basepath: Annotated[str, Option(help="Path to save (non-dataset) artifacts")],

        # Additional arguments should have defaults (the verbose arg is an example, you do not need to use it)
        verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
):
    """Run a script on a dataset."""
    os.makedirs(output_basepath, exist_ok=True)

    data = read_data(data_path)  # Infers file type; returns a list of dicts

    ...

    # write_data takes a list of dicts and a path
    output_data_path = os.path.dirname(data_path)
    write_data(data, f"{output_data_path}/output.jsonl")  # or csv or txt


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(example_script)
    app()
