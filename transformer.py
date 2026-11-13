import json
from pathlib import Path
from datetime import datetime
from typing import Any
def load_config(config_path: str | Path = "config.json") -> dict:
    """
    Load column mappings and data type configurations from JSON.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        Dictionary containing configuration details.
    """
    path = Path(config_path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
def standardize_columns(
    rows: list[dict[str, Any]],
    mapping: dict[str, str]
) -> list[dict[str, Any]]:
    """
    Rename dataset columns according to the standard schema.

    Args:
        rows: List of dataset records.
        mapping: Dictionary containing original and standard column names.

    Returns:
        List of dictionaries with standardized column names.
    """
    standardized_rows = []
    for row in rows:
        standardized_row = {}
        for column, value in row.items():
            new_column = mapping.get(column, column)
            standardized_row[new_column] = value
        standardized_rows.append(standardized_row)
    return standardized_rows
def convert_data_types(
    rows: list[dict[str, Any]],
    type_mapping: dict[str, str]
) -> list[dict[str, Any]]:
    """
    Convert configured columns into float or datetime values.
    Args:
        rows: List of dataset records.
        type_mapping: Dictionary specifying required data types.
    Returns:
        List of records with converted data types.
    """
    converted_rows = []
    for row in rows:
        converted_row = row.copy()
        for column, data_type in type_mapping.items():
            if column not in converted_row:
                continue
            value = converted_row[column]
            if value is None or value == "":
                converted_row[column] = None
            elif data_type == "float":
                converted_row[column] = float(value)
            elif data_type == "datetime":
                converted_row[column] = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
        converted_rows.append(converted_row)
    return converted_rows
def calculate_order_totals(
    rows: list[dict[str, Any]]
) -> dict[str, float]:
    """
    Calculate total price and freight for each order_id.
    Args:
        rows: List of order item records.
    Returns:
        Dictionary containing order IDs and their total amounts.
    """
    order_totals: dict[str, float] = {}
    for row in rows:
        order_id = row["order_id"]
        price = float(row.get("price") or 0)
        freight = float(row.get("freight") or 0)
        item_total = price + freight
        if order_id not in order_totals:
            order_totals[order_id] = 0.0
        order_totals[order_id] += item_total
    return order_totals