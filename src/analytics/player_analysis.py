"""
Player-level analytical summaries for IPL matches.

This module provides reusable player-wise analytics derived from the
processed match metadata dataset.

It analyzes Player of the Match awards across seasons, teams,
venues, and match types without modifying the input dataframe.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.aggregations import (
    count_by_group,
    multi_group_count,
)
from src.analytics.validators import (
    validate_required_columns,
)
from src.schemas.columns import (
    MATCH_TYPE_COL,
    PLAYER_OF_MATCH_COL,
    SEASON_COL,
    VENUE_COL,
    WINNER_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "analyze_players",
]

REQUIRED_COLUMNS = {
    PLAYER_OF_MATCH_COL,
    SEASON_COL,
    VENUE_COL,
    WINNER_COL,
    MATCH_TYPE_COL,
}

def _player_of_match_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count Player of the Match awards won by each player.
    """
    awards = df[
        df[PLAYER_OF_MATCH_COL].notna()
    ]

    return count_by_group(
        df=awards,
        group_col=PLAYER_OF_MATCH_COL,
        count_name="awards",
    ).rename(
        columns={
            PLAYER_OF_MATCH_COL: "player",
        }
    )

def _season_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute Player of the Match awards by season.
    """
    awards = df[
        df[PLAYER_OF_MATCH_COL].notna()
    ]

    return (
        multi_group_count(
            df=awards,
            group_cols=[
                SEASON_COL,
                PLAYER_OF_MATCH_COL,
            ],
            count_name="awards",
        )
        .rename(
            columns={
                PLAYER_OF_MATCH_COL: "player",
            }
        )
    )

def _team_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute Player of the Match awards by winning team.
    """
    awards = df[
        df[PLAYER_OF_MATCH_COL].notna()
    ]

    return (
        multi_group_count(
            df=awards,
            group_cols=[
                WINNER_COL,
                PLAYER_OF_MATCH_COL,
            ],
            count_name="awards",
        )
        .rename(
            columns={
                WINNER_COL: "team",
                PLAYER_OF_MATCH_COL: "player",
            }
        )
    )

def _venue_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute Player of the Match awards by venue.
    """
    awards = df[
        df[PLAYER_OF_MATCH_COL].notna()
    ]

    return (
        multi_group_count(
            df=awards,
            group_cols=[
                VENUE_COL,
                PLAYER_OF_MATCH_COL,
            ],
            count_name="awards",
        )
        .rename(
            columns={
                VENUE_COL: "venue",
                PLAYER_OF_MATCH_COL: "player",
            }
        )
    )

def _match_type_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute Player of the Match awards by match type.
    """
    awards = df[
        df[PLAYER_OF_MATCH_COL].notna()
    ]

    return (
        multi_group_count(
            df=awards,
            group_cols=[
                MATCH_TYPE_COL,
                PLAYER_OF_MATCH_COL,
            ],
            count_name="awards",
        )
        .rename(
            columns={
                MATCH_TYPE_COL: "match_type",
                PLAYER_OF_MATCH_COL: "player",
            }
        )
    )

def analyze_players(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate player-level analytical summaries.

    Parameters
    ----------
    df : pd.DataFrame
        Processed match-level dataframe.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing reusable player analytics.
    """
    logger.info("Starting player analysis...")

    validate_required_columns(
        df,
        REQUIRED_COLUMNS,
    )

    results = {
        "awards": _player_of_match_summary(df),
        "season": _season_summary(df),
        "team": _team_summary(df),
        "venue": _venue_summary(df),
        "match_type": _match_type_summary(df),
    }

    logger.info("Player analysis completed.")

    return results