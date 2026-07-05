"""
Team-level analytical summaries for IPL matches.

This module provides reusable team-wise analytics derived from the
processed match metadata dataset.

It computes participation, performance, seasonal trends, venue
distribution, and winning margin statistics without modifying the
input dataframe.
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
from src.analytics.transformations import (
    build_team_dataset,
    TEAM_COL,
)
from src.schemas.columns import (
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

# ============================================================================
# Derived Analytical Columns
# ============================================================================

MATCHES_COL = "matches"
WINS_COL = "wins"
TOSS_WINS_COL = "toss_wins"

__all__ = [
    "analyze_teams",
]

REQUIRED_COLUMNS = {
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    WINNER_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
}



def _participation_summary(
    teams_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute matches played by each team.
    """
    return count_by_group(
        df=teams_df,
        group_col=TEAM_COL,
        count_name=MATCHES_COL,
    )

def _wins_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute matches won by each team.
    """
    winners = df[df[WINNER_COL].notna()]

    return count_by_group(
        df=winners,
        group_col=WINNER_COL,
        count_name=WINS_COL,
    ).rename(
        columns={WINNER_COL: TEAM_COL}
    )

def _toss_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute toss wins by team.
    """
    return count_by_group(
        df=df,
        group_col=TOSS_WINNER_COL,
        count_name=TOSS_WINS_COL,
    ).rename(
        columns={TOSS_WINNER_COL: TEAM_COL}
    )

def _season_summary(
    teams_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute matches played by each team in every season.

    Parameters
    ----------
    teams_df : pd.DataFrame
        Team-level dataframe.

    Returns
    -------
    pd.DataFrame
        Season-wise team participation.
    """
    return multi_group_count(
        df=teams_df,
        group_cols=[
            TEAM_COL,
            SEASON_COL,
        ],
        count_name=MATCHES_COL,
    )

def _venue_summary(
    teams_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute matches played by each team at every venue.
    """
    return multi_group_count(
        df=teams_df,
        group_cols=[
            TEAM_COL,
            VENUE_COL,
        ],
        count_name=MATCHES_COL,
    )

def _margin_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute average winning margins for each winning team.

    Parameters
    ----------
    df : pd.DataFrame
        Match-level dataframe.

    Returns
    -------
    pd.DataFrame
        Average run and wicket margins by team.
    """
    winners = df[df[WINNER_COL].notna()]

    return (
        winners.groupby(
            WINNER_COL,
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
        .rename(columns={WINNER_COL: TEAM_COL})
        .sort_values(TEAM_COL)
        .reset_index(drop=True)
    )

def analyze_teams(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate team-level analytical summaries.

    Parameters
    ----------
    df : pd.DataFrame
        Processed match-level dataframe.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing reusable team analytics.
    """
    logger.info("Starting team analysis...")

    validate_required_columns(
        df,
        REQUIRED_COLUMNS,
    )

    teams_df = build_team_dataset(df)

    results = {
        "participation": _participation_summary(
            teams_df,
        ),
        "wins": _wins_summary(df),
        "toss": _toss_summary(df),
        "season": _season_summary(
            teams_df,
        ),
        "venue": _venue_summary(
            teams_df,
        ),
        "margins": _margin_summary(df),
    }

    logger.info(
        "Team analysis completed."
    )

    return results