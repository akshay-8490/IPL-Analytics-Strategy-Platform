"""
Match fact builder.
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


def build_match_fact(
    *,
    deliveries_df: pd.DataFrame,
    lookup_maps: dict[str, dict[Any, int]],
) -> pd.DataFrame:
    """
    Build the Match fact table.
    """
    logger.info("Building Match fact table.")

    df = deliveries_df.copy()

    # The columns present in processed deliveries are used to compute match aggregations:
    required_columns = [
        "match_id",
        "season",
        "runs_off_bat",
        "extras",
        "innings",
        "ball",
    ]

    validate_lookup_columns(
        dataframe=df,
        required_columns=required_columns,
    )

    # --------------------------------------------------------
    # Compute Indicators
    # --------------------------------------------------------
    df["total_runs"] = df["runs_off_bat"].fillna(0) + df["extras"].fillna(0)
    df["is_wicket"] = df["player_dismissed"].notna().astype(int) if "player_dismissed" in df.columns else df["is_wicket"]
    df["is_four"] = (df["runs_off_bat"] == 4).astype(int)
    df["is_six"] = (df["runs_off_bat"] == 6).astype(int)
    df["is_boundary"] = df["runs_off_bat"].isin([4, 6]).astype(int)
    df["is_legal_delivery"] = (df["actual_delivery"].fillna(1) == 1).astype(int) if "actual_delivery" in df.columns else df["is_legal_delivery"]

    # Group by to compile match stats
    fact_match = (
        df
        .groupby(
            ["match_id", "season"],
            as_index=False,
        )
        .agg(
            total_runs=("total_runs", "sum"),
            total_wickets=("is_wicket", "sum"),
            total_boundaries=("is_boundary", "sum"),
            total_fours=("is_four", "sum"),
            total_sixes=("is_six", "sum"),
            total_extras=("extras", "sum"),
            total_legal_deliveries=("is_legal_delivery", "sum"),
        )
    )

    # Calculate total overs
    fact_match["total_overs"] = (
        fact_match["total_legal_deliveries"] / 6
    )

    # --------------------------------------------------------
    # Replace Natural Keys with Surrogate Keys
    # --------------------------------------------------------
    fact_match["match_key"] = replace_lookup_values(
        dataframe=fact_match,
        column="match_id",
        lookup=lookup_maps["match_lookup"],
    )

    fact_match["season_key"] = replace_lookup_values(
        dataframe=fact_match,
        column="season",
        lookup=lookup_maps["season_lookup"],
    )

    fact_match = fact_match[
        [
            "match_key",
            "total_runs",
            "total_wickets",
            "total_boundaries",
            "total_fours",
            "total_sixes",
            "total_extras",
            "total_legal_deliveries",
            "total_overs",
        ]
    ]

    logger.info(
        "Built Match fact table with %d matches.",
        len(fact_match),
    )

    return fact_match
