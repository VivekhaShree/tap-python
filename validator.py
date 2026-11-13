import re
from typing import Any
def to_snake_case(column_name: str) -> str:
    """
    Convert a column name into snake_case format.

    Args:
        column_name: Original column name.

    Returns:
        Column name converted into lowercase snake_case.
    """
    name = column_name.strip()
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_").lower()
def normalize_columns(
    rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Convert all dictionary column names into snake_case.

    Args:
        rows: List of dictionaries containing dataset records.

    Returns:
        List of dictionaries with normalized column names.
    """
    normalized_rows = []
    for row in rows:
        normalized_row = {}
        for column, value in row.items():
            new_column = to_snake_case(column)
            normalized_row[new_column] = value
        normalized_rows.append(normalized_row)
    return normalized_rows