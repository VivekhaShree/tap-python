# task 1 - day 5

# Olist Data Validation and Processing Pipeline

## Project Overview

This project implements a Python-based data validation and processing pipeline using the Brazilian Olist E-commerce dataset.

The pipeline reads CSV files, validates data, identifies invalid records, logs processing activities, and avoids unnecessary reprocessing using file hashing and a manifest.

## Features

1. Reads all configured Olist CSV files.
2. Config-driven column mapping.
3. Schema and data validation.
4. Bad records identification and export.
5. Custom exception handling.
6. Logging to a file.
7. Idempotent processing using SHA-256 hashing.
8. Automated unit testing.
9. Configuration-based adaptability.

## Project Structure

```text
Olist_Data_Pipeline/
│
├── data/
├── output/
├── logs/
├── tests/
├── day 5.ipynb
├── config.json
├── manifest.json
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or above
- Jupyter Notebook
- Pandas
- Pytest

## Environment Setup

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

Navigate to the project:

```bash
cd Olist_Data_Pipeline
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Dataset Setup

Place all nine Olist CSV files inside the data directory.

## Running the Notebook

Start Jupyter:

```bash
jupyter notebook
```

Open:

```text
day 5.ipynb
```

Execute all cells from top to bottom.

## Output Files

The pipeline generates:

- Validated CSV files.
- bad_records.csv
- processing_summary.csv
- pipeline.log
- manifest.json

## Idempotency

The pipeline calculates SHA-256 hashes for input files.

Unchanged files are skipped. Modified files are processed again.

## Configuration

Column mappings and validation rules are maintained in config.json.

New column names can be mapped to expected column names without modifying the pipeline code.

## Testing

Run the unit tests included in the notebook.

The tests cover column mapping, missing columns, numeric validation, positive value validation, file hashing, and manifest processing.

## Author

Vivekha Shree K
