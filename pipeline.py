import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml


def load_config(config_path):

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def setup_logging(log_dir):

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"pipeline_{timestamp}.log"

    logger = logging.getLogger("DataPipeline")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def calculate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_manifest(manifest_path):

    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as file:
            return json.load(file)

    return {"processed_files": {}}


def save_manifest(manifest, manifest_path):

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)


def clean_dataframe(df, cleaning_config):

    if cleaning_config.get("trim_string_values", True):
        string_columns = df.select_dtypes(include=["object", "string"]).columns

        for column in string_columns:
            df[column] = df[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    if cleaning_config.get("remove_empty_rows", True):
        df = df.dropna(how="all")

    if cleaning_config.get("remove_duplicates", False):
        df = df.drop_duplicates()

    return df


def save_output(df, file_path, output_dir):

    output_name = file_path.stem

    csv_path = output_dir / f"{output_name}_cleaned.csv"
    json_path = output_dir / f"{output_name}_cleaned.json"

    df.to_csv(csv_path, index=False)

    df.to_json(json_path, orient="records", indent=4, date_format="iso")


def run_pipeline(config_path="config.yaml"):

    start_time = time.time()

    config = load_config(config_path)

    input_dir = Path(config["paths"]["input_dir"])
    output_dir = Path(config["paths"]["output_dir"])
    log_dir = Path(config["paths"]["log_dir"])

    manifest_path = Path(config["paths"]["manifest"])
    summary_path = Path(config["paths"]["summary"])

    output_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(log_dir)

    logger.info("Pipeline execution started")

    manifest = load_manifest(manifest_path)

    csv_files = sorted(input_dir.glob("*.csv"))

    summary = {
        "run_timestamp": datetime.now().isoformat(),
        "files_discovered": len(csv_files),
        "files_processed": 0,
        "files_skipped": 0,
        "files_failed": 0,
        "total_input_records": 0,
        "total_cleaned_records": 0,
        "total_rejected_records": 0,
        "duration_seconds": 0,
    }

    for file_path in csv_files:
        try:
            file_hash = calculate_hash(file_path)
            file_key = str(file_path.resolve())

            previous_hash = manifest["processed_files"].get(file_key)

            if previous_hash == file_hash:
                logger.info("Skipping previously processed file: %s", file_path.name)

                summary["files_skipped"] += 1
                continue

            logger.info("Processing file: %s", file_path.name)

            df = pd.read_csv(file_path)

            input_count = len(df)

            cleaned_df = clean_dataframe(df, config["cleaning"])

            cleaned_count = len(cleaned_df)

            save_output(cleaned_df, file_path, output_dir)

            manifest["processed_files"][file_key] = file_hash

            summary["files_processed"] += 1
            summary["total_input_records"] += input_count
            summary["total_cleaned_records"] += cleaned_count

            logger.info("Successfully processed %s", file_path.name)

        except Exception:
            summary["files_failed"] += 1
            logger.exception("Failed to process file: %s", file_path.name)

    save_manifest(manifest, manifest_path)

    summary["duration_seconds"] = round(time.time() - start_time, 3)

    with open(summary_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    logger.info("Pipeline execution completed")
    logger.info("Run summary: %s", summary)

    return summary
