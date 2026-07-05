"""
Reusable aggregation utilities for analytics modules.

This module provides generic aggregation helpers built on top of
pandas groupby operations. The functions are intentionally
domain-agnostic and can be reused across season, team, player,
venue, and match analyses.

The module performs aggregations only and never modifies the
input dataframe.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from src.analytics.validators import (
    validate_groupby_column,
    validate_required_columns,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "count_by_group",
    "unique_count_by_group",
    "mean_by_group",
    "pivot_count",
    "multi_group_count",
    "percentage_by_group",
]

def count_by_group(
    df: pd.DataFrame,
    group_col: str,
    count_name: str,
) -> pd.DataFrame:
    validate_groupby_column(df, group_col)

    return (
        df.groupby(group_col, observed=True)
        .size()
        .reset_index(name=count_name)
        .sort_values(group_col)
        .reset_index(drop=True)
    )

def unique_count_by_group(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    count_name: str,
) -> pd.DataFrame:

    validate_required_columns(
        df,
        [group_col, value_col],
    )

    return (
        df.groupby(group_col, observed=True)[value_col]
          .nunique()
          .reset_index(name=count_name)
          .sort_values(group_col)
          .reset_index(drop=True)
    )

def mean_by_group(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    mean_name: str,
) -> pd.DataFrame:

    validate_required_columns(
        df,
        [group_col, value_col],
    )

    return (
        df.groupby(group_col, observed=True)[value_col]
          .mean()
          .round(2)
          .reset_index(name=mean_name)
          .sort_values(group_col)
          .reset_index(drop=True)
    )

def pivot_count(
    df: pd.DataFrame,
    index_col: str,
    column_col: str,
) -> pd.DataFrame:

    validate_required_columns(
        df,
        [index_col, column_col],
    )

    return (
        df.groupby(
            [index_col, column_col],
            observed=True,
        )
        .size()
        .unstack(fill_value=0)
        .rename_axis(columns=None)
        .reset_index()
        .sort_values(index_col)
        .reset_index(drop=True)
    )

def multi_group_count(
    df: pd.DataFrame,
    group_cols: Sequence[str],
    count_name: str,
) -> pd.DataFrame:
    validate_required_columns(
    df,
    group_cols,
)

    return (
        df.groupby(
            list(group_cols),
            observed=True,
        )
        .size()
        .reset_index(name=count_name)
    )

def percentage_by_group(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    count_name: str = "count",
    percentage_name: str = "percentage",
) -> pd.DataFrame:
    """
    Compute counts and percentages for values within each group.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    group_col : str
        Column used for grouping.

    value_col : str
        Column whose value distribution will be calculated
        within each group.

    count_name : str, default="count"
        Name of the count column.

    percentage_name : str, default="percentage"
        Name of the percentage column.

    Returns
    -------
    pd.DataFrame
        DataFrame containing group values, counts,
        and percentages.

    Examples
    --------
    >>> percentage_by_group(
    ...     matches,
    ...     "season",
    ...     "toss_decision"
    ... )

      season toss_decision  count  percentage
    0   2008           bat     28       47.46
    1   2008         field     31       52.54
    """
    validate_required_columns(
        df,
        [group_col, value_col],
    )

    result = (
        df.groupby(
            [group_col, value_col],
            observed=True,
        )
        .size()
        .reset_index(name=count_name)
    )

    totals = (
        result.groupby(group_col)[count_name]
        .transform("sum")
    )

    result[percentage_name] = (
        result[count_name]
        .div(totals)
        .mul(100)
        .round(2)
    )

    return (
        result.sort_values(
            by=[group_col, count_name],
            ascending=[True, False],
        )
        .reset_index(drop=True)
    )