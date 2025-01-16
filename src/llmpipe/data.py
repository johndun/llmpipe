from typing import List, Dict

import polars as pl


def read_data(path: str, as_df: bool = False, **kwargs) -> List[Dict]:
    """Reads tab separated (with header, .txt) or json lines (.jsonl) data from disk.

    Args:
        path: Path to the data file
        as_df: If true, return a polars dataframe
        kwargs: Arguments based to polars read data function

    Returns:
        List[Dict]: Data records/samples as a list of dictionaries
    """
    if path.endswith(".jsonl"):
        df = pl.read_ndjson(path, infer_schema_length=100000, **kwargs)
    elif path.endswith(".txt"):
        if "utf16" in path:
            df = pl.read_csv(path, infer_schema_length=100000, separator="\t", encoding="utf16", **kwargs)
        else:
            df = pl.read_csv(path, infer_schema_length=100000, separator="\t", **kwargs)
    elif path.endswith(".csv"):
        df = pl.read_csv(path, infer_schema_length=100000, separator=",", **kwargs)
    else:
        raise ValueError("Unsupported file type, try .txt (tab-separated), .csv (comma-separated), or .jsonl (json lines)")
    if as_df:
        return df
    return df.to_dicts()


def write_data(samples: List[Dict], path: str):
    """Writes data as tab separated (with header, .txt) or json lines (.jsonl) to disk.

    Args:
        samples: Data records/samples as a list of dictionaries
        path: Path to the data file
    """
    if path.endswith(".jsonl"):
        pl.from_dicts(samples).write_ndjson(path)
    elif path.endswith(".txt"):
        pl.from_dicts(samples).write_csv(path, separator="\t")
    elif path.endswith(".csv"):
        pl.from_dicts(samples).write_csv(path)
    else:
        raise ValueError("Unsupported file type, try .txt (tab-separated), .csv (comma-separated), or .jsonl (json lines)")