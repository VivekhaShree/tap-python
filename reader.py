import csv
from pathlib import Path
from typing import Any
def read_csv(path: str | Path) -> list[dict[str, Any]]:
    """
    Read a CSV file and return its contents as a list of dictionaries.

    Args:
        path: Path of the CSV file.

    Returns:
        A list of dictionaries representing CSV rows.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        csv_reader = csv.DictReader(file)
        return [dict(row) for row in csv_reader]