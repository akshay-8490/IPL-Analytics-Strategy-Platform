"""
Delivery fact builder.
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


def build_delivery_fact(
    *,
    deliveries_df: pd.DataFrame,
    lookup_maps: dict[str, dict[Any, int]],
) -> pd.DataFrame:
    """
    Build the Delivery fact table.
    """
    logger.info("Building Delivery fact table.")

    df = deliveries_df.copy()

    # The columns present in processed deliveries are:
    # match_id, season, batting_team, bowling_team, striker, bowler, non_striker, fielder_1, player_dismissed
    required_columns = [
        "match_id",
        "season",
        "batting_team",
        "bowling_team",
        "striker",
        "bowler",
        "non_striker",
        "innings",
        "ball",
        "runs_off_bat",
        "extras",
    ]

    validate_lookup_columns(
        dataframe=df,
        required_columns=required_columns,
    )

    # --------------------------------------------------------
    # Compute Indicator & Schema Columns
    # --------------------------------------------------------
    over_number = df["ball"].astype(int)
    df["over_number"] = over_number

    # Calculate sequential ball number within the (match_id, innings, over_number) group
    # to handle extras (wides/noballs) and prevent primary key duplicate errors.
    df["ball_number"] = (
        df.groupby(["match_id", "innings", "over_number"])
        .cumcount() + 1
    )

    df["total_runs"] = df["runs_off_bat"].fillna(0) + df["extras"].fillna(0)
    df["is_boundary"] = df["runs_off_bat"].isin([4, 6])
    df["is_four"] = df["runs_off_bat"] == 4
    df["is_six"] = df["runs_off_bat"] == 6
    df["is_dot_ball"] = (df["runs_off_bat"] == 0) & (df["extras"] == 0)
    df["is_wicket"] = df["player_dismissed"].notna()
    df["is_legal_delivery"] = df["actual_delivery"].fillna(1) == 1

    # Derive extra_type
    extra_type = pd.Series(None, index=df.index, dtype="string")
    if "wides" in df.columns:
        extra_type = extra_type.mask(df["wides"] > 0, "wide")
    if "noballs" in df.columns:
        extra_type = extra_type.mask(df["noballs"] > 0, "noball")
    if "byes" in df.columns:
        extra_type = extra_type.mask(df["byes"] > 0, "bye")
    if "legbyes" in df.columns:
        extra_type = extra_type.mask(df["legbyes"] > 0, "legbye")
    if "penalty" in df.columns:
        extra_type = extra_type.mask(df["penalty"] > 0, "penalty")
    df["extra_type"] = extra_type

    # --------------------------------------------------------
    # Replace Natural Keys with Surrogate Keys
    # --------------------------------------------------------
    df["match_key"] = replace_lookup_values(
        dataframe=df,
        column="match_id",
        lookup=lookup_maps["match_lookup"],
    )

    df["season_key"] = replace_lookup_values(
        dataframe=df,
        column="season",
        lookup=lookup_maps["season_lookup"],
    )

    df["batting_team_key"] = replace_lookup_values(
        dataframe=df,
        column="batting_team",
        lookup=lookup_maps["team_lookup"],
    )

    df["bowling_team_key"] = replace_lookup_values(
        dataframe=df,
        column="bowling_team",
        lookup=lookup_maps["team_lookup"],
    )

    df["batter_key"] = replace_lookup_values(
        dataframe=df,
        column="striker",
        lookup=lookup_maps["player_lookup"],
    )

    df["bowler_key"] = replace_lookup_values(
        dataframe=df,
        column="bowler",
        lookup=lookup_maps["player_lookup"],
    )

    df["non_striker_key"] = replace_lookup_values(
        dataframe=df,
        column="non_striker",
        lookup=lookup_maps["player_lookup"],
    )

    df["fielder_key"] = replace_lookup_values(
        dataframe=df,
        column="fielder_1" if "fielder_1" in df.columns else "fielder",
        lookup=lookup_maps["player_lookup"],
    )

    df["player_out_key"] = replace_lookup_values(
        dataframe=df,
        column="player_dismissed" if "player_dismissed" in df.columns else "player_out",
        lookup=lookup_maps["player_lookup"],
    )

    # --------------------------------------------------------
    # Select Target Columns to Match MySQL Schema
    # --------------------------------------------------------
    fact_delivery = df[
        [
            "match_key",
            "season_key",
            "batting_team_key",
            "bowling_team_key",
            "batter_key",
            "bowler_key",
            "non_striker_key",
            "fielder_key",
            "player_out_key",
            "innings",
            "over_number",
            "ball_number",
            "runs_off_bat",
            "extras",
            "total_runs",
            "is_boundary",
            "is_four",
            "is_six",
            "is_dot_ball",
            "is_wicket",
            "is_legal_delivery",
            "extra_type",
        ]
    ]

    logger.info(
        "Built Delivery fact table with %d deliveries.",
        len(fact_delivery),
    )

    return fact_delivery
