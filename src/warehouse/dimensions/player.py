"""
Player dimension builder.
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _extract_unique_players(
    *,
    deliveries_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract the canonical list of IPL players.
    """
    logger.info("Extracting unique IPL players.")

    # In the processed deliveries, player columns are:
    # striker (batter), bowler, non_striker, player_dismissed, and fielder_1/2/3.
    target_columns = [
        "striker",
        "bowler",
        "non_striker",
        "player_dismissed",
        "fielder_1",
        "fielder_2",
        "fielder_3",
    ]

    required_columns = ["striker", "bowler", "non_striker"]
    missing = [col for col in required_columns if col not in deliveries_df.columns]

    if missing:
        raise ValueError(
            f"Missing required player columns in deliveries: {missing}"
        )

    players_series = []
    for column in target_columns:
        if column in deliveries_df.columns:
            players_series.append(deliveries_df[column])

    players = pd.concat(players_series, ignore_index=True)

    player_dimension = (
        players
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
        .to_frame(name="player_name")
    )

    logger.info(
        "Extracted %d unique players.",
        len(player_dimension),
    )

    return player_dimension


def build_player_dimension(
    *,
    deliveries_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Player dimension.
    """
    logger.info("Building Player dimension.")

    players = _extract_unique_players(
        deliveries_df=deliveries_df,
    )

    player_seasons = []
    player_columns = [
        "striker",
        "bowler",
        "non_striker",
        "player_dismissed",
        "fielder_1",
        "fielder_2",
        "fielder_3",
    ]

    for column in player_columns:
        if column in deliveries_df.columns:
            temp = (
                deliveries_df[[column, "season"]]
                .rename(columns={column: "player_name"})
                .dropna()
            )
            player_seasons.append(temp)

    player_seasons = pd.concat(
        player_seasons,
        ignore_index=True,
    )

    season_summary = (
        player_seasons
        .groupby("player_name", as_index=False)
        .agg(
            first_season=("season", "min"),
            last_season=("season", "max"),
        )
    )

    player_dimension = (
        players
        .merge(
            season_summary,
            on="player_name",
            how="left",
        )
        .sort_values("player_name")
        .reset_index(drop=True)
    )

    logger.info(
        "Built Player dimension with %d players.",
        len(player_dimension),
    )

    return player_dimension
