"""
Executive summary metrics for IPL matches.

This module computes high-level executive summary statistics from the
processed match metadata.
"""

from __future__ import annotations

from typing import Any
import pandas as pd

from src.schemas.columns import (
    MATCH_ID_COL,
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    CITY_COL,
    WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "compute_executive_summary",
]

def compute_executive_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute high-level executive summary metrics from the match dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Processed match-level dataframe.

    Returns
    -------
    dict[str, Any]
        Dictionary containing executive metrics.
    """
    logger.info("Computing executive summary metrics...")

    # Unique teams count
    all_teams = pd.concat([df[TEAM1_COL], df[TEAM2_COL]]).dropna().unique()
    total_teams = len(all_teams)

    # Result types
    win_by_runs_count = df[WIN_BY_RUNS_COL].notna().sum()
    win_by_wickets_count = df[WIN_BY_WICKETS_COL].notna().sum()
    total_completed = df[WINNER_COL].notna().sum()
    no_result_count = len(df) - total_completed

    # Toss statistics
    toss_field_count = (df[TOSS_DECISION_COL] == "field").sum()
    toss_bat_count = (df[TOSS_DECISION_COL] == "bat").sum()
    total_tosses = toss_field_count + toss_bat_count
    toss_field_pct = round((toss_field_count / total_tosses * 100), 2) if total_tosses > 0 else 0.0

    metrics = {
        "total_matches": int(df[MATCH_ID_COL].nunique()),
        "total_seasons": int(df[SEASON_COL].nunique()),
        "total_teams": int(total_teams),
        "total_venues": int(df[VENUE_COL].nunique()),
        "total_cities": int(df[CITY_COL].nunique(dropna=True)),
        "completed_matches": int(total_completed),
        "no_result_matches": int(no_result_count),
        "win_by_runs": int(win_by_runs_count),
        "win_by_wickets": int(win_by_wickets_count),
        "toss_field_percentage": float(toss_field_pct),
    }

    logger.info("Executive summary metrics computed.")
    return metrics