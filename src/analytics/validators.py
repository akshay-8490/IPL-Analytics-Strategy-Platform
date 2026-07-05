"""
Validation utilities for analytics modules.

This module contains reusable validation helpers used by
the analytics package. These functions validate analysis
inputs and dataframe schemas before business computations
are performed.

Unlike ETL validation, this module assumes that the
incoming data has already passed preprocessing and quality
checks.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "validate_dataframe",
    "validate_required_columns",
    "validate_groupby_column",
]

def _validate_dataframe_type(
    df: pd.DataFrame,
) -> None:
    """
    Validate dataframe type.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame, "
            f"received {type(df).__name__}."
        )
    
def _validate_dataframe_not_empty(
    df: pd.DataFrame,
) -> None:
    """
    Validate dataframe is not empty.
    """
    if df.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )
    
def _validate_columns_exist(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """
    Validate required columns exist.
    """
    missing = set(required_columns).difference(df.columns)

    if missing:
        raise KeyError(
            "Missing required columns: "
            f"{sorted(missing)}"
        )
    
def validate_dataframe(
    df: pd.DataFrame,
) -> None:
    """
    Validate dataframe before analytics.
    """
    _validate_dataframe_type(df)
    _validate_dataframe_not_empty(df)

def validate_required_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """
    Validate dataframe schema.
    """
    validate_dataframe(df)

    _validate_columns_exist(
        df,
        required_columns,
    )

def validate_groupby_column(
    df: pd.DataFrame,
    column: str,
) -> None:
    """
    Validate grouping column exists.
    """
    validate_required_columns(
        df,
        [column],
    )