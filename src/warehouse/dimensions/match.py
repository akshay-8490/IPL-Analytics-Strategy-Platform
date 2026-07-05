"""
Match dimension builder.
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def build_match_dimension(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Match dimension.
    """
    logger.info("Building Match dimension.")

    required_columns = [
        "match_id",
        "season",
        "date",
        "team1",
        "team2",
        "toss_winner",
        "toss_decision",
        "winner",
        "win_type",
        "winning_margin",
        "venue",
        "city",
        "player_of_match",
        "match_type",
        "method",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in matches_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns for Match dimension: "
            f"{missing_columns}"
        )

    match_dimension = (
        matches_df[required_columns]
        .drop_duplicates(subset="match_id")
        .sort_values("match_id")
        .reset_index(drop=True)
    )

    logger.info(
        "Built Match dimension with %d matches.",
        len(match_dimension),
    )

    return match_dimension

