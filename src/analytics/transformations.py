"""
Reusable dataframe transformation utilities for analytics modules.

This module provides reusable dataframe reshaping operations used
across multiple analytics modules. These transformations prepare
normalized analytical datasets but do not perform any aggregations
or business computations.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.validators import validate_required_columns
from src.schemas.columns import (
    MATCH_ID_COL,
    SEASON_COL,
    DATE_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    CITY_COL,
    WINNER_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
    PLAYER_OF_MATCH_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "build_team_dataset",
    "build_team_pair_dataset",
]

# ============================================================================
# Derived Analytical Columns
# ============================================================================

TEAM_COL = "team"
OPPONENT_COL = "opponent"
TEAM_ROLE_COL = "team_role"
TEAM_A_COL = "team_a"
TEAM_B_COL = "team_b"

TEAM_DATASET_REQUIRED_COLUMNS = {
    MATCH_ID_COL,
    SEASON_COL,
    DATE_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    CITY_COL,
    WINNER_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
    PLAYER_OF_MATCH_COL,
}

def build_team_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a normalized team-level dataset.

    Each IPL match is expanded into two rows—one for each
    participating team.

    Parameters
    ----------
    df : pd.DataFrame
        Match-level dataframe.

    Returns
    -------
    pd.DataFrame
        Team-level dataframe with one row per team per match.
    """
    validate_required_columns(
        df,
        TEAM_DATASET_REQUIRED_COLUMNS,
    )

    team1 = (
        df[
            [
                MATCH_ID_COL,
                SEASON_COL,
                DATE_COL,
                VENUE_COL,
                CITY_COL,
                TEAM1_COL,
                TEAM2_COL,
                WINNER_COL,
                TOSS_WINNER_COL,
                TOSS_DECISION_COL,
                WIN_BY_RUNS_COL,
                WIN_BY_WICKETS_COL,
                PLAYER_OF_MATCH_COL,
            ]
        ]
        .rename(
            columns={
                TEAM1_COL: TEAM_COL,
                TEAM2_COL: OPPONENT_COL,
            }
        )
        .assign(**{TEAM_ROLE_COL: TEAM1_COL})
    )

    team2 = (
        df[
            [
                MATCH_ID_COL,
                SEASON_COL,
                DATE_COL,
                VENUE_COL,
                CITY_COL,
                TEAM1_COL,
                TEAM2_COL,
                WINNER_COL,
                TOSS_WINNER_COL,
                TOSS_DECISION_COL,
                WIN_BY_RUNS_COL,
                WIN_BY_WICKETS_COL,
                PLAYER_OF_MATCH_COL,
            ]
        ]
        .rename(
            columns={
                TEAM2_COL: TEAM_COL,
                TEAM1_COL: OPPONENT_COL,
            }
        )
        .assign(**{TEAM_ROLE_COL: TEAM2_COL})
    )

    team_df = pd.concat(
        [team1, team2],
        ignore_index=True,
    )

    return team_df.sort_values(
        [MATCH_ID_COL, TEAM_ROLE_COL]
    ).reset_index(drop=True)

def build_team_pair_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a canonical team-pair dataset.

    Each match is represented by a deterministic pair of teams,
    ordered alphabetically to ensure that Team A vs Team B and
    Team B vs Team A are treated as the same matchup.

    Parameters
    ----------
    df : pd.DataFrame
        Match-level dataframe.

    Returns
    -------
    pd.DataFrame
        Match-level dataframe with canonical team pair columns.
    """
    validate_required_columns(
        df,
        {
            MATCH_ID_COL,
            TEAM1_COL,
            TEAM2_COL,
        },
    )
    df = df.copy()

    # Determine team_a and team_b alphabetically
    team_a = df[[TEAM1_COL, TEAM2_COL]].min(axis=1)
    team_b = df[[TEAM1_COL, TEAM2_COL]].max(axis=1)

    team_pairs = pd.DataFrame({
        TEAM_A_COL: team_a,
        TEAM_B_COL: team_b,
    })

    return pd.concat(
        [
            df.reset_index(drop=True),
            team_pairs,
        ],
        axis=1,
    )