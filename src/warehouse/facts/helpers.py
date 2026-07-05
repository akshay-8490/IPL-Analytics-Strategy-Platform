"""
Helpers for fact building.
"""

from __future__ import annotations

from typing import Any
import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def validate_lookup_columns(
    *,
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """
    Validate required columns before key replacement.
    """
    missing = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


def replace_lookup_values(
    *,
    dataframe: pd.DataFrame,
    column: str,
    lookup: dict[Any, int],
) -> pd.Series:
    """
    Replace natural keys with surrogate keys.
    """
    logger.info(
        "Replacing natural keys for %s.",
        column,
    )
    return dataframe[column].map(lookup)
