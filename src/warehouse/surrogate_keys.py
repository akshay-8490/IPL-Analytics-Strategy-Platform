"""
Warehouse Surrogate Key Generator
=================================

Assign surrogate integer keys to warehouse dimensions.

Responsibilities
----------------
- Assign surrogate keys to dimensions
- Create lookup dictionaries
- Preserve natural business keys

Notes
-----
- This module does not build dimensions.
- This module does not build fact tables.
- This module does not perform SQL operations.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ============================================================================
# Module Constants
# ============================================================================

TEAM_KEY = "team_key"
PLAYER_KEY = "player_key"
MATCH_KEY = "match_key"
VENUE_KEY = "venue_key"
SEASON_KEY = "season_key"

def _assign_surrogate_key(
    *,
    dataframe: pd.DataFrame,
    key_column: str,
) -> pd.DataFrame:
    """
    Assign sequential surrogate keys to a dimension.

    Parameters
    ----------
    dataframe : pd.DataFrame

    key_column : str

    Returns
    -------
    pd.DataFrame
    """

    logger.info(
        "Assigning surrogate keys (%s).",
        key_column,
    )

    dataframe = dataframe.copy()

    dataframe.insert(
        0,
        key_column,
        range(1, len(dataframe) + 1),
    )

    logger.info(
        "Assigned %d surrogate keys.",
        len(dataframe),
    )

    return dataframe

def _create_lookup_map(
    *,
    dataframe: pd.DataFrame,
    natural_key: str,
    surrogate_key: str,
) -> dict[Any, int]:
    """
    Create a lookup map from natural keys to surrogate keys.
    """

    logger.info(
        "Creating lookup map for %s.",
        surrogate_key,
    )

    lookup = dict(
        zip(
            dataframe[natural_key],
            dataframe[surrogate_key],
        )
    )

    logger.info(
        "Created lookup containing %d records.",
        len(lookup),
    )

    return lookup

def add_team_keys(
    *,
    team_dimension: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Add surrogate keys to the Team dimension.

    Parameters
    ----------
    team_dimension : pd.DataFrame

    Returns
    -------
    tuple
        (dimension_with_keys, lookup_map)
    """

    logger.info("Assigning Team surrogate keys.")

    team_dimension = _assign_surrogate_key(
        dataframe=team_dimension,
        key_column=TEAM_KEY,
    )

    lookup = _create_lookup_map(
        dataframe=team_dimension,
        natural_key="team_name",
        surrogate_key=TEAM_KEY,
    )

    return team_dimension, lookup

def add_player_keys(
    *,
    player_dimension: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Add surrogate keys to the Player dimension.
    """

    logger.info("Assigning Player surrogate keys.")

    player_dimension = _assign_surrogate_key(
        dataframe=player_dimension,
        key_column=PLAYER_KEY,
    )

    lookup = _create_lookup_map(
        dataframe=player_dimension,
        natural_key="player_name",
        surrogate_key=PLAYER_KEY,
    )

    return player_dimension, lookup

def add_match_keys(
    *,
    match_dimension: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[int, int]]:
    """
    Add surrogate keys to the Match dimension.

    Parameters
    ----------
    match_dimension : pd.DataFrame
        Match dimension with natural keys.

    Returns
    -------
    tuple
        (dimension_with_keys, lookup_map)
    """

    logger.info("Assigning Match surrogate keys.")

    match_dimension = _assign_surrogate_key(
        dataframe=match_dimension,
        key_column=MATCH_KEY,
    )

    lookup = _create_lookup_map(
        dataframe=match_dimension,
        natural_key="match_id",
        surrogate_key=MATCH_KEY,
    )

    return match_dimension, lookup

def add_venue_keys(
    *,
    venue_dimension: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Add surrogate keys to the Venue dimension.

    Parameters
    ----------
    venue_dimension : pd.DataFrame
        Venue dimension with natural keys.

    Returns
    -------
    tuple
        (dimension_with_keys, lookup_map)
    """

    logger.info("Assigning Venue surrogate keys.")

    venue_dimension = _assign_surrogate_key(
        dataframe=venue_dimension,
        key_column=VENUE_KEY,
    )

    lookup = _create_lookup_map(
        dataframe=venue_dimension,
        natural_key="venue",
        surrogate_key=VENUE_KEY,
    )

    return venue_dimension, lookup

def add_season_keys(
    *,
    season_dimension: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Add surrogate keys to the Season dimension.

    Parameters
    ----------
    season_dimension : pd.DataFrame
        Season dimension with natural keys.

    Returns
    -------
    tuple
        (dimension_with_keys, lookup_map)
    """

    logger.info("Assigning Season surrogate keys.")

    season_dimension = _assign_surrogate_key(
        dataframe=season_dimension,
        key_column=SEASON_KEY,
    )

    lookup = _create_lookup_map(
        dataframe=season_dimension,
        natural_key="season",
        surrogate_key=SEASON_KEY,
    )

    return season_dimension, lookup

def assign_surrogate_keys(
    *,
    dimensions: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, dict[Any, int]],
]:
    """
    Assign surrogate keys to all warehouse dimensions.

    Parameters
    ----------
    dimensions : dict[str, pd.DataFrame]
        Dictionary containing all natural-key dimensions.

    Returns
    -------
    tuple
        (
            dimensions_with_surrogate_keys,
            lookup_maps,
        )
    """

    logger.info("Assigning surrogate keys to warehouse dimensions.")

    team_dimension, team_lookup = add_team_keys(
        team_dimension=dimensions["dim_team"],
    )

    player_dimension, player_lookup = add_player_keys(
        player_dimension=dimensions["dim_player"],
    )

    match_dimension, match_lookup = add_match_keys(
        match_dimension=dimensions["dim_match"],
    )

    venue_dimension, venue_lookup = add_venue_keys(
        venue_dimension=dimensions["dim_venue"],
    )

    season_dimension, season_lookup = add_season_keys(
        season_dimension=dimensions["dim_season"],
    )

    # Map natural keys to surrogate keys and rename/format columns for dim_match
    match_dimension = match_dimension.copy()
    match_dimension["season_key"] = match_dimension["season"].map(season_lookup)
    match_dimension["venue_key"] = match_dimension["venue"].map(venue_lookup)
    match_dimension["team1_key"] = match_dimension["team1"].map(team_lookup)
    match_dimension["team2_key"] = match_dimension["team2"].map(team_lookup)
    match_dimension["toss_winner_key"] = match_dimension["toss_winner"].map(team_lookup)
    match_dimension["winner_key"] = match_dimension["winner"].map(team_lookup)

    match_dimension = match_dimension.rename(columns={
        "date": "match_date",
        "winning_margin": "win_margin",
    })

    # Add outcome column with None/NULL values since it's not present in matches_df
    match_dimension["outcome"] = None

    # Filter to match the exact MySQL schema columns of dim_match
    match_dimension = match_dimension[
        [
            "match_key",
            "match_id",
            "season_key",
            "match_date",
            "venue_key",
            "team1_key",
            "team2_key",
            "toss_winner_key",
            "toss_decision",
            "winner_key",
            "win_type",
            "win_margin",
            "match_type",
            "player_of_match",
            "outcome",
            "method",
        ]
    ]

    dimensions_with_keys = {
        "dim_team": team_dimension,
        "dim_player": player_dimension,
        "dim_match": match_dimension,
        "dim_venue": venue_dimension,
        "dim_season": season_dimension,
    }

    lookup_maps = {
        "team_lookup": team_lookup,
        "player_lookup": player_lookup,
        "match_lookup": match_lookup,
        "venue_lookup": venue_lookup,
        "season_lookup": season_lookup,
    }

    logger.info(
        "Successfully assigned surrogate keys to %d dimensions.",
        len(dimensions_with_keys),
    )

    return dimensions_with_keys, lookup_maps

__all__ = [
    "add_team_keys",
    "add_player_keys",
    "add_match_keys",
    "add_venue_keys",
    "add_season_keys",
    "assign_surrogate_keys",
]