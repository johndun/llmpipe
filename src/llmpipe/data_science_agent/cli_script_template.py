from typing import Annotated

import typer
from typer import Option

from llmpipe import read_data, write_data


# All inputs should be Option type, even if no default is provided
# Dataset outputs should be saved in the directory containing the input data (`os.path.dirname(data_path)`)
def example_script(
        data_path: Annotated[str, Option(help="Input dataset")],
        output_basepath: Annotated[str, Option(help="Path to save (non-dataset) artifacts")],

        # Additional arguments should have defaults (the verbose arg is an example, you do not need to use it)
        verbose: Annotated[bool, Option(help="Stream output to stdout")] = False
):
    """Run a script on a dataset."""
    samples = read_data(data_path)  # Infers file type; returns a list of dicts
    ...
    # write_data takes a list of dicts and a path
    write_data(samples, "path/to/output.jsonl")  # or csv or txt


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(example_script)
    app()
