import csv
import re
from datetime import datetime
from pathlib import Path

from schemas import (
    REQUIRED_FIELDS,
    NUMERIC_FIELDS,
    DATE_FIELDS,
    ALLOWED_ORDER_STATUS,
    ZIP_FIELDS,
    MAX_REJECTION_PERCENTAGE
)

# --------------------------------------------------
# 1. CUSTOM EXCEPTIONS
# --------------------------------------------------

class SchemaError(Exception):
    """Raised when required columns are missing."""
    pass


class FileFormatError(Exception):
    """Raised when a file has an invalid CSV format."""
    pass

# --------------------------------------------------
# 2. VALIDATION PATTERNS
# --------------------------------------------------

ID_PATTERN = re.compile(r"^[0-9a-fA-F]{32}$")
ZIP_PATTERN = re.compile(r"^\d{5}$")

# --------------------------------------------------
# 3. DATE VALIDATION
# --------------------------------------------------

def is_valid_date(value):
    if not value:
        return False
    date_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S"
    ]
    for date_format in date_formats:
        try:
            datetime.strptime(value.strip(), date_format)
            return True
        except ValueError:
            continue
    return False

# --------------------------------------------------
# 4. VALIDATE INDIVIDUAL ROW
# --------------------------------------------------

def validate_row(row, required_fields):
    errors = []
    for field, value in row.items():
        value = (value or "").strip()
        # Check empty required values
        if field in required_fields and not value:
            errors.append(f"{field} is empty")
            continue
        if not value:
            continue
        # Check IDs: exactly 32 hexadecimal characters
        if field.endswith("_id") and field != "order_item_id":
            if not ID_PATTERN.fullmatch(value):
                errors.append(
                    f"{field} must contain exactly 32 hexadecimal characters"
                )
        # Check ZIP prefixes
        if field in ZIP_FIELDS:
            if not ZIP_PATTERN.fullmatch(value):
                errors.append(
                    f"{field} must contain exactly 5 digits"
                )
        # Check numeric fields
        if field in NUMERIC_FIELDS:
            try:
                number = float(value)
                if not number == number:
                    raise ValueError
                if number in (float("inf"), float("-inf")):
                    raise ValueError
            except ValueError:
                errors.append(f"{field} must be numeric")
                continue
        # Business rule: price must be greater than zero
        if field == "price":
            try:
                if float(value) <= 0:
                    errors.append("price must be greater than 0")
            except ValueError:
                pass
        # Check date formats
        if field in DATE_FIELDS:
            if not is_valid_date(value):
                errors.append(f"{field} contains an invalid date")
        # Business rule: allowed order statuses
        if field == "order_status":
            if value.lower() not in ALLOWED_ORDER_STATUS:
                errors.append(
                    f"Invalid order_status: {value}"
                )
    return errors

# --------------------------------------------------
# 5. VALIDATE CSV FILE
# --------------------------------------------------

def validate_file(
    file_path,
    bad_records,
    max_rejection_percentage=MAX_REJECTION_PERCENTAGE
):
    file_path = Path(file_path)
    print(f"\nProcessing: {file_path.name}")
    summary = {
        "file_name": file_path.name,
        "total_rows": 0,
        "valid_rows": 0,
        "rejected_rows": 0,
        "rejection_percentage": 0,
        "status": ""
    }
    # Handle missing file
    if not file_path.exists():
        print("File not found. Skipping.")
        summary["status"] = "MISSING FILE"
        return summary
    # Handle empty file
    if file_path.stat().st_size == 0:
        print("File is empty. Skipping.")
        summary["status"] = "EMPTY FILE"
        return summary
    required_fields = REQUIRED_FIELDS.get(file_path.name)
    if required_fields is None:
        raise SchemaError(
            f"No schema defined for {file_path.name}"
        )
    try:
        with file_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                raise FileFormatError("CSV header is missing")
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise FileFormatError("Duplicate column names found")
            missing_fields = (
                set(required_fields) - set(reader.fieldnames)
            )
            if missing_fields:
                raise SchemaError(
                    f"Missing columns: {', '.join(sorted(missing_fields))}"
                )
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    errors = ["Row contains more values than the header"]
                elif any(value is None for value in row.values()):
                    errors = ["Row contains fewer values than the header"]
                else:
                    errors = validate_row(row, required_fields)
                summary["total_rows"] += 1
                if errors:
                    summary["rejected_rows"] += 1
                    bad_record = {
                        "source_file": file_path.name,
                        "row_number": row_number,
                        "reason": "; ".join(errors)
                    }
                    bad_record.update({
                        key: value
                        for key, value in row.items()
                        if key is not None
                    })
                    bad_records.append(bad_record)
                else:
                    summary["valid_rows"] += 1
    except (SchemaError, FileFormatError):
        raise
    except (csv.Error, UnicodeDecodeError, OSError) as error:
        raise FileFormatError(
            f"Unable to read {file_path.name}: {error}"
        ) from error
    # Calculate rejection percentage
    if summary["total_rows"] > 0:
        summary["rejection_percentage"] = (
            summary["rejected_rows"] /
            summary["total_rows"]
        ) * 100
    # Fail the entire file if rejected rows exceed threshold
    if summary["rejection_percentage"] > max_rejection_percentage:
        summary["status"] = "FAILED"
    else:
        summary["status"] = "PASSED"
    # Print individual file summary
    print("Total rows:", summary["total_rows"])
    print("Valid rows:", summary["valid_rows"])
    print("Rejected rows:", summary["rejected_rows"])
    print(
        "Rejection percentage:",
        f"{summary['rejection_percentage']:.2f}%"
    )
    print("Status:", summary["status"])
    return summary

# --------------------------------------------------
# 6. SAVE REJECTED RECORDS
# --------------------------------------------------

def save_bad_records(records, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        print("\nNo rejected records found.")
        return
    fieldnames = list(records[0].keys())
    with output_path.open(
        mode="w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(records)
    print(f"\nRejected records saved to: {output_path}")

# --------------------------------------------------
# 7. SAVE VALIDATION SUMMARY
# --------------------------------------------------

def save_summary(summaries, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "file_name",
        "total_rows",
        "valid_rows",
        "rejected_rows",
        "rejection_percentage",
        "status"
    ]
    with output_path.open(
        mode="w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(summaries)
    print(f"\nValidation summary saved to: {output_path}")