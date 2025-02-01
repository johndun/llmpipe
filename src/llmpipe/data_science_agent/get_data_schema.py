import json
import random
from typing import Any, Dict, List, Annotated

import typer
from typer import Option

from llmpipe.data import read_data
from llmpipe.field import Input, Output
from llmpipe.prompt_module import PromptModule
from llmpipe.constants import DEFAULT_MODEL



def infer_type(value):
    """
    Infer the type of a value, handling special cases like arrays and nested objects.
    """
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        if not value:  # Empty array
            return "array"
        # Get type of first element for array type
        element_type = infer_type(value[0])
        return f"array<{element_type}>"
    elif isinstance(value, dict):
        return "object"
    else:
        return "unknown"


def generate_schema(data, parent_path=""):
    """
    Generate a schema from a list of dictionaries, handling nested structures.

    Args:
        data: List of dictionaries containing the data
        parent_path: String representing the current path in nested structures

    Returns:
        List of dictionaries containing schema information
    """
    if not data:
        return []

    schema = []
    # Use the first record to get all possible keys
    sample_record = data[0]

    for key, value in sample_record.items():
        current_path = f"{parent_path}.{key}" if parent_path else key

        if isinstance(value, dict):
            # Add the object field itself
            schema.append({
                "name": current_path,
                "type": "object",
                "nullable": any(key not in record or record[key] is None for record in data)
            })
            # Then add its nested fields
            nested_schema = generate_schema([value], current_path)
            schema.extend(nested_schema)

        elif isinstance(value, list) and value and isinstance(value[0], dict):
            # Add the array field itself
            schema.append({
                "name": current_path,
                "type": "array<object>",
                "nullable": any(key not in record or record[key] is None for record in data)
            })
            # Then add schema for the object inside the array
            nested_schema = generate_schema([value[0]], f"{current_path}[]")
            schema.extend(nested_schema)

        else:
            # Check all records for this field to handle potential type variations
            field_types = set()
            for record in data:
                if key in record and record[key] is not None:
                    field_types.add(infer_type(record[key]))

            # If multiple types are found, use "mixed"
            field_type = "mixed" if len(field_types) > 1 else (field_types.pop() if field_types else "null")

            schema.append({
                "name": current_path,
                "type": field_type,
                "nullable": any(key not in record or record[key] is None for record in data)
            })

    return schema


def get_data_schema(
    data_path: Annotated[str, Option(help="Dataset path")],
    output_path: Annotated[str, Option(help="Path to save the schema")] = None
):
    """Generate a basic data schema."""
    # Read the data
    samples = read_data(data_path)

    schema = generate_schema(samples)

    schema_str = ""
    for field in schema:
        schema_str += f"Field: {field['name']}\n"
        schema_str += f"  Type: {field['type']}\n"
        schema_str += f"  Nullable: {field['nullable']}\n"
        schema_str += "\n"

    # Save schema if output path provided
    if output_path:
        with open(output_path, "w") as f:
            f.write(schema_str)
        print(f"\nSaved schema to {output_path}")
    else:
        print(schema_str)

    return schema

if __name__ == "__main__":
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(get_data_schema)
    app()
