import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option
import polars as pl

from llmpipe.data import read_data


def truncate_value(value: Any, max_len: int = 500, max_items: int = 5) -> Any:
    """Truncate long strings and lists/dicts to reasonable lengths."""
    if isinstance(value, str):
        if len(value) > max_len:
            return value[:max_len] + "..."
    elif isinstance(value, (list, tuple)):
        if len(value) > max_items:
            return list(value[:max_items]) + ["..."]
        return list(value)
    elif isinstance(value, dict):
        if len(value) > max_items:
            return {k: value[k] for k in list(value.keys())[:max_items]}
    return value


def truncate_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Truncate all values in a sample dictionary."""
    return {k: truncate_value(v) for k, v in sample.items()}


def get_data_sample(
    data_path: Annotated[str, Option(help="Dataset path")],
    n_samples: Annotated[int, Option("-n", "--n-samples", help="Number of samples to print")] = 5,
    output_path: Annotated[str, Option(help="Path to save the samples")] = None
):
    """Print random samples from a dataset with truncated long values and optionally save them."""
    # Read the data
    samples = read_data(data_path)
    
    # Convert to DataFrame
    df = pl.from_dicts(samples, infer_schema_length=100000)
    
    # Get random samples
    total_rows = len(df)
    n_samples = min(n_samples, total_rows)
    random_indices = random.sample(range(total_rows), n_samples)
    
    # Get samples
    samples = [df.row(idx, named=True) for idx in random_indices]
    truncated_samples = [truncate_sample(sample) for sample in samples]
    
    # Either print samples or save to file
    if output_path:
        with open(output_path, "w") as f:
            f.write(json.dumps(samples, indent=True))
        print(f"Saved {n_samples} samples to {output_path}")
    else:
        for i, truncated in enumerate(truncated_samples, 1):
            print(json.dumps(truncated, indent=2))


if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(get_data_sample)
    app()
