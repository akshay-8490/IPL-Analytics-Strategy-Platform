"""
Venue dimension builder.
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _extract_unique_venues(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract the canonical list of IPL venues from the engineered
    match dataset.
    """
    logger.info("Extracting unique IPL venues.")

    required_columns = {"venue"}
    missing_columns = required_columns.difference(matches_df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns for venue extraction: "
            f"{sorted(missing_columns)}"
        )

    venue_dimension = (
        matches_df[["venue"]]
        .dropna()
        .drop_duplicates()
        .sort_values("venue")
        .reset_index(drop=True)
    )

    logger.info(
        "Extracted %d unique venues.",
        len(venue_dimension),
    )

    return venue_dimension


def build_venue_dimension(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Venue dimension.
    """
    logger.info("Building Venue dimension.")

    venues = _extract_unique_venues(
        matches_df=matches_df,
    )

    venue_attributes = (
        matches_df
        .groupby("venue", as_index=False)
        .agg(
            city=("city", "first"),
            first_season=("season", "min"),
            last_season=("season", "max"),
        )
    )

    venue_dimension = (
        venues
        .merge(
            venue_attributes,
            on="venue",
            how="left",
        )
        .sort_values("venue")
        .reset_index(drop=True)
    )

    logger.info(
        "Built Venue dimension with %d venues.",
        len(venue_dimension),
    )

    return venue_dimension
