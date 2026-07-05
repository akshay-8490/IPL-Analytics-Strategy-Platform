"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: validators.py

Description:
    Validates cleaned and normalized IPL datasets before
    feature engineering.

Purpose:
    - Validate required columns
    - Validate toss decisions
    - Validate overs configuration
    - Validate winning margins
    - Perform dataframe-level validation

===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.etl.constants import (
    REQUIRED_MATCH_COLUMNS,
    VALID_TOSS_DECISIONS,
    DEFAULT_BALLS_PER_OVER,
)


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str] | tuple[str, ...] = REQUIRED_MATCH_COLUMNS,
) -> None:
    """
    Validate that all required columns exist.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

def validate_toss_decision(
    df: pd.DataFrame,
    column: str = "toss_decision",
) -> None:
    """
    Validate toss decision values.
    """
    if column not in df.columns:
        return

    invalid = (
        df.loc[
            ~df[column].isin(VALID_TOSS_DECISIONS),
            column,
        ]
        .dropna()
        .unique()
    )

    if len(invalid):
        raise ValueError(
            f"Invalid toss decisions found: {invalid.tolist()}"
        )


def validate_overs(
    df: pd.DataFrame,
    column: str = "balls_per_over",
) -> None:
    """
    Validate balls per over.
    """
    if column not in df.columns:
        return

    invalid = (
        df.loc[
            df[column] != DEFAULT_BALLS_PER_OVER,
            column,
        ]
        .dropna()
        .unique()
    )

    if len(invalid):
        raise ValueError(
            f"Invalid balls_per_over values: {invalid.tolist()}"
        )

def validate_margin_fields(df: pd.DataFrame) -> None:
    """
    Validate winner margin columns.
    """
    if not {
        "winner_runs",
        "winner_wickets",
    }.issubset(df.columns):
        return

    invalid = df[
        df["winner_runs"].notna()
        & df["winner_wickets"].notna()
    ]

    if not invalid.empty:
        raise ValueError(
            "A match cannot have both winner_runs "
            "and winner_wickets populated."
        )

def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all dataframe validations.
    """
    validate_required_columns(df)
    validate_toss_decision(df)
    validate_overs(df)
    validate_margin_fields(df)

    return df


__all__ = [
    "validate_required_columns",
    "validate_toss_decision",
    "validate_overs",
    "validate_margin_fields",
    "validate_dataframe",
]