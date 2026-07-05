"""
Season dimension builder.
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _build_season_summary(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build season-level summary information.
    """
    logger.info("Building season summary.")

    required_columns = {
        "season",
        "date",
        "match_id",
    }
    missing_columns = required_columns.difference(matches_df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns for season summary: "
            f"{sorted(missing_columns)}"
        )

    season_summary = (
        matches_df
        .groupby("season", as_index=False)
        .agg(
            season_start_date=("date", "min"),
            season_end_date=("date", "max"),
            total_matches=("match_id", "nunique"),
        )
        .sort_values("season")
        .reset_index(drop=True)
    )

    logger.info(
        "Built season summary for %d seasons.",
        len(season_summary),
    )

    return season_summary


def build_season_dimension(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Season dimension.
    """
    logger.info("Building Season dimension.")

    season_dimension = _build_season_summary(
        matches_df=matches_df,
    )

    logger.info(
        "Built Season dimension with %d seasons.",
        len(season_dimension),
    )

    return season_dimension
