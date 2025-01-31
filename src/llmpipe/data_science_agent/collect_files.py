import os
from pathlib import Path
from typing import Dict


def collect_files(directory_path: str) -> Dict[str, str]:
    """
    Collect contents of all text files in the given directory path and sort by creation time.

    Args:
        directory_path: Path to directory containing text files

    Returns:
        Dictionary with filenames (without extensions) as keys and file contents as values,
        sorted by file creation time
    """
    file_data = []
    path = Path(directory_path)

    if not path.exists():
        raise ValueError(f"Directory not found: {directory_path}")

    for file_path in path.rglob("*"):
        if file_path.is_file():
            try:
                # Read file content
                content = file_path.read_text(encoding='utf-8')

                # Get creation time
                try:
                    # Try to get actual creation time (birthtime) first
                    creation_time = os.stat(file_path).st_birthtime
                except AttributeError:
                    # Fallback to ctime if birthtime is not available
                    creation_time = os.stat(file_path).st_ctime

                # Store tuple of (creation_time, stem, content)
                file_data.append((creation_time, file_path.stem, content))

            except UnicodeDecodeError:
                # Skip files that can't be read as text
                continue

    # Sort by creation time and create dictionary
    contents = {
        stem: content
        for _, stem, content in sorted(file_data, key=lambda x: x[0])
    }

    return contents