import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from validator import to_snake_case
from transformer import (
    standardize_columns,
    calculate_order_totals
)

def test_to_snake_case():
    assert to_snake_case("Customer ID") == "customer_id"
    assert to_snake_case("OrderDate") == "order_date"


def test_standardize_columns():
    rows = [
        {
            "order_status": "delivered",
            "customer_id": "C101"
        }
    ]
    mapping = {
        "order_status": "status"
    }
    result = standardize_columns(rows, mapping)
    assert result[0]["status"] == "delivered"
    assert result[0]["customer_id"] == "C101"


def test_calculate_order_totals():
    rows = [
        {"order_id": "A101", "price": 200.0, "freight": 20.0},
        {"order_id": "A101", "price": 300.0, "freight": 30.0},
        {"order_id": "A102", "price": 400.0, "freight": 40.0}
    ]
    result = calculate_order_totals(rows)
    assert result["A101"] == 550.0
    assert result["A102"] == 440.0
