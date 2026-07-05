"""
Player-Match fact builder.
"""

from __future__ import annotations

from typing import Any
import pandas as pd

from src.utils.logging_utils import get_logger
from src.warehouse.facts.helpers import (
    replace_lookup_values,
    validate_lookup_columns,
)

logger = get_logger(__name__)


def build_player_match_fact(
    *,
    deliveries_df: pd.DataFrame,
    lookup_maps: dict[str, dict[Any, int]],
) -> pd.DataFrame:
    """
    Build the Player-Match fact table.
    """
    logger.info("Building Player-Match fact table.")

    df = deliveries_df.copy()

    # The columns present in processed deliveries are:
    required_columns = [
        "match_id",
        "season",
        "striker",
        "runs_off_bat",
    ]

    validate_lookup_columns(
        dataframe=df,
        required_columns=required_columns,
    )

    # --------------------------------------------------------
    # Compute Indicators
    # --------------------------------------------------------
    df["is_four"] = (df["runs_off_bat"] == 4).astype(int)
    df["is_six"] = (df["runs_off_bat"] == 6).astype(int)
    df["is_wicket"] = df["player_dismissed"].notna().astype(int) if "player_dismissed" in df.columns else df["is_wicket"]

    # Group by striker (batter) to compile player stats
    fact_player_match = (
        df
        .groupby(
            [
                "match_id",
                "season",
                "striker",
            ],
            as_index=False,
        )
        .agg(
            batting_runs=("runs_off_bat", "sum"),
            balls_faced=("striker", "count"),
            fours=("is_four", "sum"),
            sixes=("is_six", "sum"),
            dismissals=("is_wicket", "sum"),
        )
    )

    # --------------------------------------------------------
    # Replace Natural Keys with Surrogate Keys
    # --------------------------------------------------------
    fact_player_match["match_key"] = replace_lookup_values(
        dataframe=fact_player_match,
        column="match_id",
        lookup=lookup_maps["match_lookup"],
    )

    fact_player_match["season_key"] = replace_lookup_values(
        dataframe=fact_player_match,
        column="season",
        lookup=lookup_maps["season_lookup"],
    )

    fact_player_match["player_key"] = replace_lookup_values(
        dataframe=fact_player_match,
        column="striker",
        lookup=lookup_maps["player_lookup"],
    )

    fact_player_match = fact_player_match[
        [
            "match_key",
            "player_key",
            "batting_runs",
            "balls_faced",
            "fours",
            "sixes",
            "dismissals",
        ]
    ]

    logger.info(
        "Built Player-Match fact table with %d rows.",
        len(fact_player_match),
    )

    return fact_player_match
