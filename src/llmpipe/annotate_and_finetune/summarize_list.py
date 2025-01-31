from typing import List, Dict, Union, Optional, TypeVar
import statistics
from collections import Counter
import re


T = TypeVar('T', int, float, str)
NestedList = List[Optional[Union[T, List[Optional[T]]]]]


def summarize_list(values: NestedList, n_examples: int = 10) -> str:
    """
    Generate a statistical summary of a list that may contain None values and nested lists.
    For numeric lists, includes statistical measures. For all lists, includes
    a value count table showing the top n_examples most frequent values.
    For nested lists, includes statistics about the sublists.

    Args:
        values: List of integers, floats, strings, or lists of these types (may contain None values)
        n_examples: Number of most frequent values to show in count table

    Returns:
        str: A descriptive summary of the list's statistical properties
    """
    # Check if we have a list of lists
    has_nested_lists = any(isinstance(x, list) for x in values if x is not None)

    if not has_nested_lists:
        return _summarize_flat_list(values, n_examples)

    return _summarize_nested_list(values, n_examples)


def _summarize_flat_list(values: List[Optional[T]], n_examples: int) -> str:
    """Helper function to summarize a flat list (original functionality)."""
    # Count total items and None values
    total_items = len(values)
    none_count = sum(1 for x in values if x is None)

    # Get list of non-None values
    valid_values = [x for x in values if x is not None]

    # If no valid values, return early summary
    if not valid_values:
        return f"Contains {total_items} items, all of which are None values."

    # Check if values are numeric (int or float)
    is_numeric = all(isinstance(x, (int, float)) for x in valid_values)

    # Create initial summary
    summary = f"Contains {total_items} items, including {none_count} None "
    summary += f"value{'s' if none_count != 1 else ''}. "

    if is_numeric:
        # Calculate statistics for numeric data
        min_val = min(valid_values)
        max_val = max(valid_values)
        mean_val = statistics.mean(valid_values)
        median_val = statistics.median(valid_values)
        std_dev = statistics.stdev(valid_values) if len(valid_values) > 1 else 0

        summary += (f"Among the {len(valid_values)} numeric value{'s' if len(valid_values) != 1 else ''}, "
                   f"the minimum is {min_val:.2f} and the maximum is {max_val:.2f}. The mean is "
                   f"{mean_val:.2f} with a median of {median_val:.2f}")

        # Add standard deviation if there are at least 2 values
        if len(valid_values) > 1:
            summary += f" and a standard deviation of {std_dev:.2f}"

        summary += "."
    else:
        # Summary for string data
        summary += f"There are {len(valid_values)} non-None value{'s' if len(valid_values) != 1 else ''} "
        summary += f"with {len(set(valid_values))} unique value{'s' if len(set(valid_values)) != 1 else ''}."

    # Add value counts table
    summary += _create_value_counts_table(valid_values, none_count, is_numeric, n_examples)

    return summary


def _summarize_nested_list(values: List[Optional[List[Optional[T]]]], n_examples: int) -> str:
    """Helper function to summarize a list of lists."""
    # Count total lists and None values at top level
    total_lists = len(values)
    none_count = sum(1 for x in values if x is None)
    valid_lists = [x for x in values if x is not None]

    if not valid_lists:
        return f"The nested structure contains {total_lists} lists, all of which are None values."

    # Calculate list size statistics
    list_sizes = [len(lst) for lst in valid_lists]
    avg_size = statistics.mean(list_sizes)
    min_size = min(list_sizes)
    max_size = max(list_sizes)

    # Create initial summary
    summary = (f"The nested structure contains {total_lists} lists, including {none_count} None "
              f"value{'s' if none_count != 1 else ''}.\n\n")

    summary += (f"List size statistics:\n"
                f"- Average size: {avg_size:.2f}\n"
                f"- Minimum size: {min_size}\n"
                f"- Maximum size: {max_size}\n\n")

    # Flatten all values for statistical analysis
    all_values = [item for sublist in valid_lists for item in sublist]
    none_count_inner = sum(1 for x in all_values if x is None)
    valid_values = [x for x in all_values if x is not None]

    if not valid_values:
        # Add None count table even when all values are None
        return summary + "All nested lists contain only None values." + _create_value_counts_table([], none_count_inner, False, n_examples)

    # Check if values are numeric
    is_numeric = all(isinstance(x, (int, float)) for x in valid_values)

    if is_numeric:
        # Calculate statistics for numeric data
        min_val = min(valid_values)
        max_val = max(valid_values)
        mean_val = statistics.mean(valid_values)
        median_val = statistics.median(valid_values)
        std_dev = statistics.stdev(valid_values) if len(valid_values) > 1 else 0

        summary += (f"Among all nested values, there are {len(valid_values)} numeric values. "
                   f"The minimum is {min_val:.2f} and the maximum is {max_val:.2f}. The mean is "
                   f"{mean_val:.2f} with a median of {median_val:.2f}")

        if len(valid_values) > 1:
            summary += f" and a standard deviation of {std_dev:.2f}"

        summary += "."
    else:
        # Summary for string data
        summary += (f"Among all nested values, there are {len(valid_values)} non-None values "
                   f"with {len(set(valid_values))} unique values.")

    # Add value counts table
    summary += _create_value_counts_table(valid_values, none_count_inner, is_numeric, n_examples)

    return summary

def _create_value_counts_table(valid_values: List[T], none_count: int, is_numeric: bool, n_examples: int) -> str:
    """Helper function to create the value counts table."""
    value_counts = Counter(valid_values)
    # Sort by count (descending), then by value (ascending)
    sorted_counts = sorted(value_counts.items(), key=lambda x: (-x[1], x[0]))

    # Take only the top n_examples
    sorted_counts = sorted_counts[:n_examples]

    # Create markdown table
    table = "\n\n**Value Counts (Top "
    table += f"{min(n_examples, len(sorted_counts))}" if len(sorted_counts) < n_examples else f"{n_examples}"
    table += "):**\n\n"
    table += "| Value | Count |\n"
    table += "|------:|------:|\n"

    for value, count in sorted_counts:
        if is_numeric:
            table += f"| {value:.2f} | {count} |\n"
        else:
            value = value.replace('\n', '<br>')
            table += f"| {value} | {count} |\n"

    if none_count > 0:
        table += f"| None | {none_count} |\n"

    return table
