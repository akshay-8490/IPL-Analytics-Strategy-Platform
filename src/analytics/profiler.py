"""
Dataset profiling utilities.

This module provides reusable functions for profiling pandas DataFrames.
The generated profiling information is intended for exploratory analysis,
data quality assessment, warehouse design, and feature engineering.

The module follows a single-responsibility design:
it only profiles datasets and never modifies them.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def _validate_input(df: pd.DataFrame) -> None:
    """
    Validate the input DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe to profile.

    Raises
    ------
    TypeError
        If the input is not a pandas DataFrame.

    ValueError
        If the dataframe is empty.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame, "
            f"received {type(df).__name__}."
        )

    if df.empty:
        raise ValueError("Input DataFrame is empty.")
    
def _dataset_shape(df: pd.DataFrame) -> dict[str, int]:
    """
    Return the shape of the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    dict[str, int]
        Dictionary containing the number of rows and columns.
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
    }

def _dataset_memory(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate memory usage statistics for the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    dict[str, Any]
        Memory usage statistics.
    """
    memory = df.memory_usage(deep=True)

    return {
        "total_memory_mb": round(memory.sum() / (1024 ** 2), 2),
        "average_column_memory_kb": round(memory.mean() / 1024, 2),
        "memory_per_column": memory.sort_values(ascending=False),
    }

def _column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a comprehensive summary for each column in the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Column-level summary containing data types, missing values,
        uniqueness statistics, and cardinality metrics.
    """
    total_rows = len(df)

    summary = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str),
        "non_null": df.notna().sum().values,
        "null": df.isna().sum().values,
        "unique": df.nunique(dropna=True).values,
    })

    summary["null_pct"] = (
        summary["null"] / total_rows * 100
    ).round(2)

    summary["cardinality_pct"] = (
        summary["unique"] / total_rows * 100
    ).round(2)

    return summary.sort_values(
        by=["null_pct", "cardinality_pct"],
        ascending=[False, False],
        ignore_index=True,
    )

def _missing_summary(
    column_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract columns containing missing values.

    Parameters
    ----------
    column_summary : pd.DataFrame
        Output from _column_summary().

    Returns
    -------
    pd.DataFrame
        Missing value summary.
    """
    missing = (
        column_summary.loc[
            column_summary["null"] > 0,
            ["column", "null", "null_pct"],
        ]
        .sort_values(
            by="null_pct",
            ascending=False,
            ignore_index=True,
        )
    )

    return missing

def _duplicate_summary(
    df: pd.DataFrame,
) -> dict[str, float]:
    """
    Compute duplicate row statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    dict[str, float]
        Duplicate row statistics.
    """
    duplicate_rows = int(df.duplicated().sum())

    total_rows = len(df)

    duplicate_pct = (
        duplicate_rows / total_rows * 100
        if total_rows
        else 0.0
    )

    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round(duplicate_pct, 2),
    }

def _uniqueness_summary(
    column_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate uniqueness statistics for all columns.

    Parameters
    ----------
    column_summary : pd.DataFrame
        Output from _column_summary().

    Returns
    -------
    pd.DataFrame
        Summary of unique values and column cardinality.
    """
    return (
        column_summary[
            ["column", "unique", "cardinality_pct"]
        ]
        .sort_values(
            by="cardinality_pct",
            ascending=False,
            ignore_index=True,
        )
    )

def _numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate descriptive statistics for numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Statistical summary for numeric columns.
    """
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return pd.DataFrame()

    summary = pd.DataFrame(index=numeric_df.columns)

    summary["count"] = numeric_df.count()
    summary["missing"] = numeric_df.isna().sum()
    summary["missing_pct"] = (
        numeric_df.isna().mean() * 100
    ).round(2)

    summary["mean"] = numeric_df.mean()
    summary["median"] = numeric_df.median()

    summary["std"] = numeric_df.std()
    summary["variance"] = numeric_df.var()

    summary["min"] = numeric_df.min()
    summary["q1"] = numeric_df.quantile(0.25)
    summary["q3"] = numeric_df.quantile(0.75)
    summary["max"] = numeric_df.max()

    summary["iqr"] = summary["q3"] - summary["q1"]

    summary["skewness"] = numeric_df.skew()
    summary["kurtosis"] = numeric_df.kurt()

    return (
        summary
        .round(2)
        .reset_index(names="column")
    )

def _categorical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics for categorical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Summary of categorical columns.
    """
    categorical_df = df.select_dtypes(
        include=["object", "category"]
    )

    if categorical_df.empty:
        return pd.DataFrame()

    rows = []

    for column in categorical_df.columns:

        mode = categorical_df[column].mode(dropna=True)

        top_value = mode.iloc[0] if not mode.empty else None

        frequency = (
            categorical_df[column]
            .value_counts(dropna=True)
            .iloc[0]
            if top_value is not None
            else 0
        )

        rows.append({
            "column": column,
            "unique": categorical_df[column].nunique(dropna=True),
            "top": top_value,
            "frequency": frequency,
            "frequency_pct": round(
                frequency / len(df) * 100,
                2,
            ),
        })

    return pd.DataFrame(rows)

def _datetime_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics for datetime columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Summary of datetime columns.
    """
    datetime_df = df.select_dtypes(
        include=["datetime64[ns]", "datetimetz"]
    )

    if datetime_df.empty:
        return pd.DataFrame()

    rows = []

    for column in datetime_df.columns:

        minimum = datetime_df[column].min()
        maximum = datetime_df[column].max()

        rows.append({
            "column": column,
            "min_date": minimum,
            "max_date": maximum,
            "span_days": (
                (maximum - minimum).days
                if pd.notna(minimum)
                and pd.notna(maximum)
                else None
            ),
        })

    return pd.DataFrame(rows)

def profile_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a comprehensive profile for a dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    dict[str, Any]
        Complete dataset profile.
    """
    logger.info("Starting dataset profiling...")

    _validate_input(df)

    # ------------------------------------------------------------------
    # Dataset-level metadata
    # ------------------------------------------------------------------

    dataset_metadata = {
        "shape": _dataset_shape(df),
        "memory": _dataset_memory(df),
        "duplicates": _duplicate_summary(df),
    }

    # ------------------------------------------------------------------
    # Column-level summaries
    # ------------------------------------------------------------------

    column_summary = _column_summary(df)

    profiles = {
        "columns": column_summary,
        "missing": _missing_summary(column_summary),
        "uniqueness": _uniqueness_summary(column_summary),
        "numeric": _numeric_summary(df),
        "categorical": _categorical_summary(df),
        "datetime": _datetime_summary(df),
    }

    logger.info("Dataset profiling completed.")

    return {
        "metadata": dataset_metadata,
        "profiles": profiles,
    }

__all__ = [
    "profile_dataset",
]