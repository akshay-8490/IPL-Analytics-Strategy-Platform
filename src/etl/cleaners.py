"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: cleaners.py

Description:
    Generic dataframe cleaning utilities for the ETL layer.

Purpose:
    - Perform reusable dataframe cleaning operations.
    - Keep business logic separate from data cleaning.
    - Provide dataset-agnostic utilities for all ETL modules.

Used By:
    - match_info.py
    - deliveries.py
    - Future ETL pipelines

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.etl.constants import DEFAULT_MISSING_VALUES
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def clean_whitespace(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """
    Remove leading/trailing whitespace and collapse multiple
    internal spaces for the specified text columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    columns : list[str]
        List of text columns to clean.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe.

    Notes
    -----
    - Non-existent columns are ignored.
    - Only string values are modified.
    - Missing values remain unchanged.
    - Original dataframe is never modified.
    """

    df = df.copy()

    cleaned_columns = []

    for column in columns:

        if column not in df.columns:
            logger.warning("Column '%s' not found. Skipping.", column)
            continue

        df[column] = df[column].apply(
            lambda value: (
                " ".join(value.strip().split())
                if isinstance(value, str)
                else value
            )
        )

        cleaned_columns.append(column)

    logger.info(
        "Whitespace cleaned for %d column(s): %s",
        len(cleaned_columns),
        cleaned_columns,
    )

    return df

def normalize_missing_values(
    df: pd.DataFrame,
    missing_values: list[str] | None = None,
) -> pd.DataFrame:
    """
    Standardize common missing value representations to pd.NA.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    missing_values : list[str] | None, default=None
        String values to be treated as missing.
        If None, a default set of common missing value
        representations is used.

    Returns
    -------
    pd.DataFrame
        Dataframe with standardized missing values.

    Notes
    -----
    - Original dataframe is never modified.
    - Existing pd.NA/None values remain unchanged.
    - Replacement is applied only to string values.
    """

    df = df.copy()

    if missing_values is None:
        missing_values = DEFAULT_MISSING_VALUES

    replacements = 0

    for column in df.columns:

        mask = (
            df[column]
            .apply(lambda value: isinstance(value, str))
            & df[column].isin(missing_values)
        )

        replacements += mask.sum()

        df.loc[mask, column] = pd.NA

    logger.info(
        "Standardized %d missing value(s) to pd.NA.",
        replacements,
    )

    return df

def drop_duplicate_rows(
    df: pd.DataFrame,
    subset: list[str] | None = None,
    keep: str = "first",
) -> pd.DataFrame:
    """
    Remove duplicate rows from a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    subset : list[str] | None, default=None
        Columns to consider when identifying duplicates.
        If None, all columns are considered.

    keep : {"first", "last", False}, default="first"
        Determines which duplicates (if any) to keep.

    Returns
    -------
    pd.DataFrame
        Dataframe with duplicate rows removed.

    Notes
    -----
    - Original dataframe is never modified.
    - Supports both full-row and subset-based duplicate removal.
    """

    df = df.copy()

    initial_rows = len(df)

    df = df.drop_duplicates(
        subset=subset,
        keep=keep,
    )

    removed_rows = initial_rows - len(df)

    logger.info(
        "Removed %d duplicate row(s). Remaining rows: %d.",
        removed_rows,
        len(df),
    )

    return df

def convert_datetime_columns(
    df: pd.DataFrame,
    columns: list[str],
    date_format: str | None = None,
    errors: str = "coerce",
) -> pd.DataFrame:
    """
    Convert one or more dataframe columns to datetime.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    columns : list[str]
        Columns to convert.

    date_format : str | None, default=None
        Optional datetime format passed to pandas.

    errors : str, default="coerce"
        Error handling strategy passed to
        pandas.to_datetime().

    Returns
    -------
    pd.DataFrame
        Dataframe with converted datetime columns.

    Notes
    -----
    - Original dataframe is never modified.
    - Missing or invalid dates become NaT when
      errors="coerce".
    - Non-existent columns are skipped.
    """

    df = df.copy()

    converted_columns = []

    for column in columns:

        if column not in df.columns:
            logger.warning(
                "Column '%s' not found. Skipping datetime conversion.",
                column,
            )
            continue

        before_nulls = df[column].isna().sum()

        df[column] = pd.to_datetime(
            df[column],
            format=date_format,
            errors=errors,
        )

        after_nulls = df[column].isna().sum()

        logger.info(
            (
                "Converted '%s' to datetime "
                "(new missing values: %d)."
            ),
            column,
            after_nulls - before_nulls,
        )

        converted_columns.append(column)

    logger.info(
        "Datetime conversion completed for %d column(s).",
        len(converted_columns),
    )

    return df

def standardize_text_columns(
    df: pd.DataFrame,
    columns: list[str],
    case: str | None = None,
) -> pd.DataFrame:
    """
    Standardize text values in the specified columns.

    Operations performed
    --------------------
    - Remove leading/trailing whitespace.
    - Collapse multiple internal spaces.
    - Optionally normalize text case.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    columns : list[str]
        Columns to standardize.

    case : {"lower", "upper", "title"} | None, default=None
        Optional case conversion.

    Returns
    -------
    pd.DataFrame
        Dataframe with standardized text columns.

    Notes
    -----
    - Original dataframe is never modified.
    - Missing values remain unchanged.
    - Non-existent columns are skipped.
    """

    df = df.copy()

    standardized_columns = []

    for column in columns:

        if column not in df.columns:
            logger.warning(
                "Column '%s' not found. Skipping text standardization.",
                column,
            )
            continue

        def _standardize(value):

            if not isinstance(value, str):
                return value

            value = " ".join(value.strip().split())

            if case == "lower":
                value = value.lower()

            elif case == "upper":
                value = value.upper()

            elif case == "title":
                value = value.title()

            return value

        df[column] = df[column].apply(_standardize)

        standardized_columns.append(column)

    logger.info(
        "Standardized text for %d column(s): %s",
        len(standardized_columns),
        standardized_columns,
    )

    return df

def clean_dataframe(
    df: pd.DataFrame,
    whitespace_columns: list[str] | None = None,
    text_columns: list[str] | None = None,
    datetime_columns: list[str] | None = None,
    datetime_format: str | None = None,
    text_case: str | None = None,
    remove_duplicates: bool = True,
    normalize_missing: bool = True,
    duplicate_subset: list[str] | None = None,
) -> pd.DataFrame:
    """
    Apply standard cleaning steps to a DataFrame.
    """
    df = df.copy()

    # Fallback to default columns if none are provided
    if text_columns is None and whitespace_columns is None and datetime_columns is None:
        text_columns = ["team1", "team2", "venue", "city"]
        datetime_columns = ["date"]
        text_case = "title"
        duplicate_subset = ["match_id"]

    if normalize_missing:
        df = normalize_missing_values(df)

    if whitespace_columns:
        df = clean_whitespace(df, whitespace_columns)

    if text_columns:
        df = standardize_text_columns(df, text_columns, case=text_case)

    if datetime_columns:
        df = convert_datetime_columns(
            df,
            columns=datetime_columns,
            date_format=datetime_format,
        )

    if remove_duplicates:
        before = len(df)
        df = df.drop_duplicates(subset=duplicate_subset)
        after = len(df)
        if before - after > 0:
            logger.info("Removed %d duplicate rows.", before - after)

    return df