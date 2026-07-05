"""
Season-level analytical summaries for IPL matches.

This module provides reusable season-wise analytics derived from the
processed match metadata dataset.

It performs aggregations only and does not generate visualizations
or modify the input dataframe.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.aggregations import (
    count_by_group,
    pivot_count,
    unique_count_by_group,
)
from src.analytics.validators import (
    validate_required_columns,
)
from src.schemas.columns import (
    PLAYER_OF_MATCH_COL,
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    TOSS_DECISION_COL,
    TOSS_WINNER_COL,
    VENUE_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
    WINNER_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "analyze_seasons",
]

REQUIRED_COLUMNS = {
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    WINNER_COL,
    PLAYER_OF_MATCH_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
}

    
def _matches_per_season(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Count matches played each season."""
    return count_by_group(
        df=df,
        group_col=SEASON_COL,
        count_name="matches",
    )

def _teams_per_season(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count unique participating teams in each season.
    """
    teams = pd.concat(
        [
            df[[SEASON_COL, TEAM1_COL]].rename(
                columns={TEAM1_COL: "team"}
            ),
            df[[SEASON_COL, TEAM2_COL]].rename(
                columns={TEAM2_COL: "team"}
            ),
        ],
        ignore_index=True,
    )

    return (
        teams.groupby(
            SEASON_COL,
            observed=True,
        )["team"]
        .nunique()
        .reset_index(name="teams")
        .sort_values(SEASON_COL)
        .reset_index(drop=True)
    )

def _venues_per_season(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Count unique venues used each season."""
    return unique_count_by_group(
        df=df,
        group_col=SEASON_COL,
        value_col=VENUE_COL,
        count_name="venues",
    )

def _player_of_match_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count unique Player of the Match award winners per season.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Season-wise count of unique Player of the Match winners.
    """
    return unique_count_by_group(
    df=df,
    group_col=SEASON_COL,
    value_col=PLAYER_OF_MATCH_COL,
    count_name="unique_player_of_match_winners",
)

def _toss_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize toss decisions by season."""
    return pivot_count(
        df=df,
        index_col=SEASON_COL,
        column_col=TOSS_DECISION_COL,
    )

def _match_outcome_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize match outcomes by season.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Season-wise outcome summary.
    """
    outcome_summary = (
        df.groupby(SEASON_COL, observed=True)
        .agg(
            wins_by_runs=(
                WIN_BY_RUNS_COL,
                lambda x: (x > 0).sum(),
            ),
            wins_by_wickets=(
                WIN_BY_WICKETS_COL,
                lambda x: (x > 0).sum(),
            ),
            no_results=(
                WINNER_COL,
                lambda x: x.isna().sum(),
            ),
        )
        .reset_index()
        .sort_values(SEASON_COL)
        .reset_index(drop=True)
    )

    return outcome_summary

def _margin_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute average winning margins for each season.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Season-wise average win margins.
    """
    margin_summary = (
        df.groupby(SEASON_COL, observed=True)
        .agg(
            avg_runs_margin=(
                WIN_BY_RUNS_COL,
                "mean",
            ),
            avg_wicket_margin=(
                WIN_BY_WICKETS_COL,
                "mean",
            ),
        )
        .round(2)
        .reset_index()
        .sort_values(SEASON_COL)
        .reset_index(drop=True)
    )

    return margin_summary

def analyze_seasons(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate season-level analytical summaries.

    Parameters
    ----------
    df : pd.DataFrame
        Processed match-level dataframe.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing season-level analytical tables.
    """
    logger.info("Starting season analysis...")

    validate_required_columns(df,REQUIRED_COLUMNS,)

    results = {
        "matches": _matches_per_season(df),
        "teams": _teams_per_season(df),
        "venues": _venues_per_season(df),
        "player_of_match": _player_of_match_summary(df),
        "toss": _toss_summary(df),
        "outcomes": _match_outcome_summary(df),
        "margins": _margin_summary(df),
    }

    logger.info("Season analysis completed.")

    return results