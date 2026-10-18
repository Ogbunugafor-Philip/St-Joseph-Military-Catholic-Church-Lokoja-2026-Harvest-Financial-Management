"""Prevent user-supplied spreadsheet formulas in CSV and XLSX exports."""

from __future__ import annotations

import pandas as pd

FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")


def spreadsheet_safe_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    if value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def safe_export_frame(frame: pd.DataFrame) -> pd.DataFrame:
    safe = frame.copy()
    for column in safe.select_dtypes(include=["object", "string"]).columns:
        safe[column] = safe[column].map(spreadsheet_safe_text)
    return safe


def safe_csv_bytes(frame: pd.DataFrame) -> bytes:
    return safe_export_frame(frame).to_csv(index=False).encode("utf-8")
