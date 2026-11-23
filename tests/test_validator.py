import pandas as pd
import pytest

from dq_gate.validator import run_quality_gate  # pyright: ignore[reportMissingImports]


def base_schema() -> dict:
    return {
        "required_columns": ["id", "data", "status", "qtd"],
        "unique_columns": ["id"],
        "not_null_columns": ["id", "data", "status"],
        "date_columns": ["data"],
        "numeric_columns": {"qtd": {"min": 0}},
        "allowed_values": {"status": ["OK", "FALHA"]},
    }


def test_all_valid_rows():
    df = pd.DataFrame(
        [
            {"id": "1", "data": "2026-11-10", "status": "OK", "qtd": "5"},
            {"id": "2", "data": "2026-11-11", "status": "FALHA", "qtd": "0"},
        ]
    )
    report = run_quality_gate(df, base_schema())
    assert report.passed is True
    assert report.valid_rows_count == 2
    assert report.rejected_rows_count == 0


def test_detects_duplicates_nulls_and_invalid_values():
    df = pd.DataFrame(
        [
            {"id": "1", "data": "2026-11-10", "status": "OK", "qtd": "5"},
            {"id": "1", "data": "2026-11-10", "status": "OK", "qtd": "5"},
            {"id": "2", "data": "", "status": "INVALIDO", "qtd": "-2"},
        ]
    )
    report = run_quality_gate(df, base_schema())
    assert report.passed is False
    assert report.valid_rows_count == 1
    assert report.rejected_rows_count == 2
    rules = {i.rule for i in report.issues}
    assert {"unique", "not_null", "allowed_values", "min_value"}.issubset(rules)


def test_missing_required_column_raises():
    df = pd.DataFrame([{"id": "1"}])
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        run_quality_gate(df, base_schema())
