import random
from typing import List, Dict, Any


def split_data(data: List[Dict[Any, Any]], proportions: List[float]) -> List[List[Dict[Any, Any]]]:
    """
    Randomly shuffle a list of dictionaries and split it into sublists according to given proportions.

    Args:
        data: List of dictionaries to be split
        proportions: List of float values that sum to 1, representing the proportion of data for each split

    Returns:
        List of lists, where each inner list contains dictionaries according to the specified proportions

    Raises:
        ValueError: If proportions don't sum to 1 (within floating point precision)
        ValueError: If any proportion is negative
        ValueError: If proportions list is empty
    """
    # Input validation
    if not proportions:
        raise ValueError("Proportions list cannot be empty")

    if any(p < 0 for p in proportions):
        raise ValueError("Proportions cannot be negative")

    if not 0.99999 <= sum(proportions) <= 1.00001:  # Account for floating point imprecision
        raise ValueError(f"Proportions must sum to 1, got {sum(proportions)}")

    # Handle empty input data
    if not data:
        return [[] for _ in proportions]

    # Create a copy and shuffle it
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)

    # Calculate the actual number of items for each split
    total_items = len(shuffled_data)
    split_sizes = []

    # Convert proportions to actual counts
    remaining_items = total_items
    for i, proportion in enumerate(proportions[:-1]):  # Handle all but the last proportion
        size = round(proportion * total_items)
        split_sizes.append(size)
        remaining_items -= size

    # Add the remaining items to the last split to ensure we use all items
    split_sizes.append(remaining_items)

    # Split the data according to calculated sizes
    result = []
    start_idx = 0

    for size in split_sizes:
        result.append(shuffled_data[start_idx:start_idx + size])
        start_idx += size

    return result
