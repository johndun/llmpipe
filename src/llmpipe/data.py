import glob
import json
import gzip
from typing import List, Dict, Any
import os

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
        pl.from_dicts(samples, infer_schema_length=100000).write_ndjson(path)
    elif path.endswith(".txt"):
        pl.from_dicts(samples, infer_schema_length=100000).write_csv(path, separator="\t")
    elif path.endswith(".csv"):
        pl.from_dicts(samples, infer_schema_length=100000).write_csv(path)
    else:
        raise ValueError("Unsupported file type, try .txt (tab-separated), .csv (comma-separated), or .jsonl (json lines)")


def load_json_files(directory_path: str) -> List[Dict[Any, Any]]:
    """
    Load all JSON/JSONL files (including gzipped variants) from a specified directory.

    Args:
        directory_path (str): Path to the directory containing JSON files

    Returns:
        List[Dict[Any, Any]]: List of JSON objects from all files

    Raises:
        FileNotFoundError: If directory doesn't exist
        json.JSONDecodeError: If JSON parsing fails
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    # Define file patterns to match
    patterns = [
        '*.json',
        '*.jsonl',
        '*.js',
        '*.json.gz',
        '*.jsonl.gz',
        '*.js.gz'
    ]

    all_records = []

    # Iterate through each pattern
    for pattern in patterns:
        file_pattern = os.path.join(directory_path, pattern)
        matching_files = glob.glob(file_pattern)

        for file_path in matching_files:
            try:
                # Check if file is gzipped
                is_gzipped = file_path.endswith('.gz')

                # Open file with appropriate method
                opener = gzip.open if is_gzipped else open
                mode = 'rt' if is_gzipped else 'r'

                with opener(file_path, mode) as f:
                    # Read file line by line
                    for line in f:
                        line = line.strip()
                        if line:  # Skip empty lines
                            try:
                                record = json.loads(line)
                                all_records.append(record)
                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON in file {file_path} at line: {line}")
                                print(f"Error details: {str(e)}")
                                continue

            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                continue

    return all_records