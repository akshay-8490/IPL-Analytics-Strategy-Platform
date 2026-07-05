"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: standardizers.py

Description:
    Standardizes categorical values across IPL datasets
    using canonical mappings.

Purpose:
    - Standardize team names
    - Standardize city names
    - Standardize venue names
    - Standardize season values
    - Provide reusable dataframe-level standardization

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.etl.constants import (
    TEAM_NAME_MAPPING,
    CITY_MAPPING,
    VENUE_MAPPING,
    SEASON_MAPPING,
)

def standardize_team_name(team: str | None) -> str | None:
    """
    Standardize an IPL team name using the canonical mapping.

    Parameters
    ----------
    team : str | None
        Original team name.

    Returns
    -------
    str | None
        Canonical team name if a mapping exists;
        otherwise returns the original value.
    """
    if pd.isna(team):
        return team

    team = str(team).strip()

    return TEAM_NAME_MAPPING.get(team, team)

def standardize_team_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...] = (
        "team1",
        "team2",
        "winner",
        "toss_winner",
    ),
) -> pd.DataFrame:
    """
    Standardize team names across multiple DataFrame columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    columns : list[str] | tuple[str, ...], optional
        Team-related columns to standardize.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized team names.
    """
    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(standardize_team_name)

    return df

def standardize_city(city: str | None) -> str | None:
    """
    Standardize an IPL city name using the canonical mapping.

    Parameters
    ----------
    city : str | None
        Original city name.

    Returns
    -------
    str | None
        Canonical city name if a mapping exists;
        otherwise returns the original value.
    """
    if pd.isna(city):
        return city

    city = str(city).strip()

    return CITY_MAPPING.get(city, city)

def standardize_city_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...] = ("city",),
) -> pd.DataFrame:
    """
    Standardize city names across DataFrame columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    columns : list[str] | tuple[str, ...], optional
        City-related columns to standardize.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized city names.
    """
    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(standardize_city)

    return df

def standardize_venue(venue: str | None) -> str | None:
    """
    Standardize an IPL venue name using the canonical mapping.

    Parameters
    ----------
    venue : str | None
        Original venue name.

    Returns
    -------
    str | None
        Canonical venue name if a mapping exists;
        otherwise returns the original value.
    """
    if pd.isna(venue):
        return venue

    venue = str(venue).strip()

    return VENUE_MAPPING.get(venue, venue)

def standardize_venue_columns(
    df: pd.DataFrame,
    columns: list[str] | tuple[str, ...] = ("venue",),
) -> pd.DataFrame:
    """
    Standardize venue names across DataFrame columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    columns : list[str] | tuple[str, ...], optional
        Venue-related columns to standardize.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized venue names.
    """
    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(standardize_venue)

    return df

def standardize_season(
    season: str | int | None,
) -> str | int | None:
    """
    Standardize IPL season values using the canonical mapping.

    Parameters
    ----------
    season : str | int | None
        Original season value.

    Returns
    -------
    str | int | None
        Canonical season value if a mapping exists;
        otherwise returns the original value.
    """
    if pd.isna(season):
        return season

    season = str(season).strip()

    return SEASON_MAPPING.get(season, season)

def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize all supported categorical fields in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized categorical values.
    """
    df = standardize_team_columns(df)
    df = standardize_city_columns(df)
    df = standardize_venue_columns(df)

    if "season" in df.columns:
        df = df.copy()
        df["season"] = df["season"].apply(standardize_season)

    return df

__all__ = [
    "standardize_team_name",
    "standardize_team_columns",
    "standardize_city",
    "standardize_city_columns",
    "standardize_venue",
    "standardize_venue_columns",
    "standardize_season",
    "standardize_dataframe",
]