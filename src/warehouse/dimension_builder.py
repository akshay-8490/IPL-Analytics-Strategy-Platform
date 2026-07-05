"""
Warehouse Dimension Builder
===========================

This module constructs the warehouse dimension tables from the
engineered datasets produced by the ETL pipeline.

Responsibilities
----------------
- Coordinate building of team, player, match, venue, and season dimensions

Notes
-----
- Consumes specific dimension builder submodules
- Contains no SQL or database logic.
"""

from __future__ import annotations

from typing import Dict
import pandas as pd

from src.utils.logging_utils import get_logger
from src.warehouse.dimensions import (
    build_match_dimension,
    build_player_dimension,
    build_season_dimension,
    build_team_dimension,
    build_venue_dimension,
)

logger = get_logger(__name__)

# ============================================================================
# Module Constants
# ============================================================================

TEAM_DIMENSION_NAME = "dim_team"
PLAYER_DIMENSION_NAME = "dim_player"
MATCH_DIMENSION_NAME = "dim_match"
VENUE_DIMENSION_NAME = "dim_venue"
SEASON_DIMENSION_NAME = "dim_season"


# ============================================================================
# Public Coordinator
# ============================================================================

def build_dimensions(
    *,
    matches_df: pd.DataFrame,
    deliveries_df: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """
    Build all warehouse dimensions.

    Parameters
    ----------
    matches_df : pd.DataFrame
        Engineered match dataset.

    deliveries_df : pd.DataFrame
        Engineered delivery dataset.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing all warehouse dimensions.
    """
    logger.info("Building warehouse dimensions.")

    dimensions = {
        TEAM_DIMENSION_NAME: build_team_dimension(
            matches_df=matches_df,
        ),
        PLAYER_DIMENSION_NAME: build_player_dimension(
            deliveries_df=deliveries_df,
        ),
        MATCH_DIMENSION_NAME: build_match_dimension(
            matches_df=matches_df,
        ),
        VENUE_DIMENSION_NAME: build_venue_dimension(
            matches_df=matches_df,
        ),
        SEASON_DIMENSION_NAME: build_season_dimension(
            matches_df=matches_df,
        ),
    }

    logger.info(
        "Successfully built %d warehouse dimensions.",
        len(dimensions),
    )

    return dimensions


__all__ = [
    "TEAM_DIMENSION_NAME",
    "PLAYER_DIMENSION_NAME",
    "MATCH_DIMENSION_NAME",
    "VENUE_DIMENSION_NAME",
    "SEASON_DIMENSION_NAME",
    "build_dimensions",
]