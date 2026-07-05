"""
Venue-level analytical summaries for IPL matches.

This module provides reusable venue-wise analytics derived from the
processed match metadata dataset.

It computes venue utilization, participating teams, seasonal trends,
toss behavior, and winning margin statistics without modifying the
input dataframe.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.aggregations import (
    count_by_group,
    multi_group_count,
    pivot_count,
    unique_count_by_group,
)
from src.analytics.transformations import (
    build_team_dataset,
)
from src.analytics.validators import (
    validate_required_columns,
)
from src.schemas.columns import (
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    TOSS_DECISION_COL,
    VENUE_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
    WINNER_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "analyze_venues",
]

REQUIRED_COLUMNS = {
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
}

def _matches_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count matches hosted at each venue.
    """
    return count_by_group(
        df=df,
        group_col=VENUE_COL,
        count_name="matches",
    )

def _teams_summary(
    teams_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count unique teams that have played at each venue.
    """
    return unique_count_by_group(
        df=teams_df,
        group_col=VENUE_COL,
        value_col="team",
        count_name="teams",
    )

def _season_summary(
    teams_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count matches hosted by each venue in every season.
    """
    return multi_group_count(
        df=teams_df,
        group_cols=[
            VENUE_COL,
            SEASON_COL,
        ],
        count_name="matches",
    )

def _toss_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize toss decisions at each venue.
    """
    return pivot_count(
        df=df,
        index_col=VENUE_COL,
        column_col=TOSS_DECISION_COL,
    )

def _margin_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute average winning margins for each venue.
    """
    return (
        df.groupby(
            VENUE_COL,
            observed=True,
        )
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
        .sort_values(VENUE_COL)
        .reset_index(drop=True)
    )

def analyze_venues(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate venue-level analytical summaries.
    """
    logger.info("Starting venue analysis...")

    validate_required_columns(
        df,
        REQUIRED_COLUMNS,
    )

    teams_df = build_team_dataset(df)

    results = {
        "matches": _matches_summary(df),
        "teams": _teams_summary(teams_df),
        "season": _season_summary(teams_df),
        "toss": _toss_summary(df),
        "margins": _margin_summary(df),
    }

    logger.info("Venue analysis completed.")

    return results