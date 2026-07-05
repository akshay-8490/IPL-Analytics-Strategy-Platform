"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: normalizers.py

Description:
    Normalizes seasons, dates, numeric columns and derives
    calendar features for IPL datasets.

Purpose:
    - Normalize season values
    - Normalize date columns
    - Extract calendar features
    - Normalize numeric columns
    - Provide reusable dataframe-level normalization

===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.etl.constants import DATE_COLUMNS

NAType = type(pd.NA)

def normalize_season(season: str | int | None) -> int | NAType:
    """
    Normalize an IPL season to its starting calendar year.

    Parameters
    ----------
    season : str | int | None
        Original season value.

    Returns
    -------
    int | pd.NA
        Normalized season as an integer.
    """
    if pd.isna(season):
        return pd.NA

    season = str(season).strip()

    if "/" in season:
        start_year = season.split("/")[0]

        try:
            return int(start_year) + 1
        except ValueError:
            return pd.NA

    try:
        return int(season)
    except ValueError:
        return pd.NA
    
def normalize_date_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...] = DATE_COLUMNS,
) -> pd.DataFrame:
    """
    Normalize date columns to pandas datetime format.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    columns : list[str] | tuple[str, ...], optional
        Date columns to normalize.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized datetime columns.
    """
    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

    return df

def extract_calendar_features(
    df: pd.DataFrame,
    date_column: str = "date",
) -> pd.DataFrame:
    """
    Extract calendar features from a datetime column.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    date_column : str, optional
        Date column.

    Returns
    -------
    pd.DataFrame
        DataFrame with additional calendar features.
    """
    if date_column not in df.columns:
        return df

    df = df.copy()

    dates = df[date_column]

    df["match_year"] = dates.dt.year
    df["match_month"] = dates.dt.month
    df["match_day"] = dates.dt.day
    df["day_of_week"] = dates.dt.day_name()
    df["week_of_year"] = dates.dt.isocalendar().week.astype("Int64")
    df["quarter"] = dates.dt.quarter
    df["is_weekend"] = dates.dt.dayofweek >= 5

    return df

def normalize_numeric_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...],
) -> pd.DataFrame:
    """
    Normalize numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    columns : list[str] | tuple[str, ...]
        Numeric columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized numeric columns.
    """
    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = (
                pd.to_numeric(
                    df[column],
                    errors="coerce",
                )
                .astype("Int64")
            )

    return df

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all normalization steps to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        Fully normalized DataFrame.
    """
    df = df.copy()

    if "season" in df.columns:
        df["season"] = df["season"].apply(normalize_season).astype("Int64")

    df = normalize_date_columns(df)
    df = extract_calendar_features(df)

    numeric_columns = (
        "match_id",
        "match_number",
        "target_runs",
        "winner_runs",
        "winner_wickets",
        "balls_per_over",
        "team_type",
    )

    df = normalize_numeric_columns(
        df,
        columns=numeric_columns,
    )

    return df

__all__ = [
    "normalize_season",
    "normalize_date_columns",
    "extract_calendar_features",
    "normalize_numeric_columns",
    "normalize_dataframe",
]