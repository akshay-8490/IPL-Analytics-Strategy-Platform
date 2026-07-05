"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: dataframe_utils.py

Description:
    Utility functions for working with pandas DataFrames.

Purpose:
    - Convert dataclass objects to DataFrames.
    - Reorder DataFrame columns.
    - Optimize DataFrame memory usage.
    - Generate simple DataFrame summaries.

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

import pandas as pd


def objects_to_dataframe(objects: list[Any]) -> pd.DataFrame:
    """
    Convert a list of dataclass objects into a pandas DataFrame.

    Parameters
    ----------
    objects : list[Any]

    Returns
    -------
    pd.DataFrame
    """

    if not objects:
        return pd.DataFrame()

    records = []

    for obj in objects:

        if is_dataclass(obj):

            records.append(asdict(obj))

        else:

            records.append(obj)

    return pd.DataFrame(records)


def reorder_columns(
    dataframe: pd.DataFrame,
    columns: list[str]
) -> pd.DataFrame:
    """
    Reorder DataFrame columns.

    Parameters
    ----------
    dataframe : pd.DataFrame

    columns : list[str]

    Returns
    -------
    pd.DataFrame
    """

    existing = [column for column in columns if column in dataframe.columns]

    remaining = [
        column
        for column in dataframe.columns
        if column not in existing
    ]

    return dataframe[
        existing + remaining
    ]


def optimize_dataframe(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage.

    Parameters
    ----------
    dataframe : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    return dataframe.convert_dtypes()


def dataframe_summary(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Return a simple DataFrame summary.

    Parameters
    ----------
    dataframe : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    return pd.DataFrame(
        {
            "Column": dataframe.columns,
            "Data Type": dataframe.dtypes.astype(str).values,
            "Missing Values": dataframe.isna().sum().values,
            "Unique Values": dataframe.nunique().values,
        }
    )
