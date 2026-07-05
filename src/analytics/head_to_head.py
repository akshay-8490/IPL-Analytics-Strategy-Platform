"""
Head-to-head analytical summaries for IPL matches.

This module provides reusable head-to-head analytics derived from
the processed match metadata dataset.

It analyzes match frequency, winning records, seasonal trends,
venue distribution, and winning margins between pairs of teams
without modifying the input dataframe.
"""
from __future__ import annotations

import pandas as pd

from src.analytics.aggregations import (
    multi_group_count,
)
from src.analytics.transformations import (
    build_team_pair_dataset,
    TEAM_A_COL,
    TEAM_B_COL,
    TEAM_COL,
)
from src.analytics.validators import (
    validate_required_columns,
)
from src.schemas.columns import (
    TEAM1_COL,
    TEAM2_COL,
    WINNER_COL,
    SEASON_COL,
    VENUE_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# ============================================================================
# Derived Analytical Columns
# ============================================================================

MATCHES_COL = "matches"
WINS_COL = "wins"

__all__ = [
    "analyze_head_to_head",
]

REQUIRED_COLUMNS = {
    TEAM1_COL,
    TEAM2_COL,
    WINNER_COL,
    SEASON_COL,
    VENUE_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
}

def _matches_summary(
    pair_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count matches played between each team pair.
    """
    return multi_group_count(
        df=pair_df,
        group_cols=[
            TEAM_A_COL,
            TEAM_B_COL,
        ],
        count_name=MATCHES_COL,
    )

def _wins_summary(
    pair_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count wins for each team within every head-to-head matchup.
    """
    return (
        multi_group_count(
            df=pair_df,
            group_cols=[
                TEAM_A_COL,
                TEAM_B_COL,
                WINNER_COL,
            ],
            count_name=WINS_COL,
        )
        .rename(
            columns={
                WINNER_COL: TEAM_COL,
            }
        )
    )

def _season_summary(
    pair_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count head-to-head matches by season.
    """
    return multi_group_count(
        df=pair_df,
        group_cols=[
            TEAM_A_COL,
            TEAM_B_COL,
            SEASON_COL,
        ],
        count_name=MATCHES_COL,
    )

def _venue_summary(
    pair_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count head-to-head matches by venue.
    """
    return multi_group_count(
        df=pair_df,
        group_cols=[
            TEAM_A_COL,
            TEAM_B_COL,
            VENUE_COL,
        ],
        count_name=MATCHES_COL,
    )

def _margin_summary(
    pair_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute average winning margins for each team matchup.
    """
    return (
        pair_df.groupby(
            [
                TEAM_A_COL,
                TEAM_B_COL,
            ],
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
        .sort_values(
            [
                TEAM_A_COL,
                TEAM_B_COL,
            ]
        )
        .reset_index(drop=True)
    )

def analyze_head_to_head(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate head-to-head analytical summaries.

    Parameters
    ----------
    df : pd.DataFrame
        Processed match-level dataframe.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing reusable head-to-head analytics.
    """
    logger.info("Starting head-to-head analysis...")

    validate_required_columns(
        df,
        REQUIRED_COLUMNS,
    )

    pair_df = build_team_pair_dataset(df)

    results = {
        "matches": _matches_summary(pair_df),
        "wins": _wins_summary(pair_df),
        "season": _season_summary(pair_df),
        "venue": _venue_summary(pair_df),
        "margins": _margin_summary(pair_df),
    }

    logger.info("Head-to-head analysis completed.")

    return results