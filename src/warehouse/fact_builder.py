"""
Warehouse Fact Builder
======================

Construct warehouse fact tables using the engineered datasets and
surrogate-key lookup maps.

Responsibilities
----------------
- Coordinate building of Delivery, Match, and Player Match fact tables

Notes
-----
- Consumes specific fact builder submodules
- Contains no SQL logic.
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger
from src.warehouse.facts import (
    build_delivery_fact,
    build_match_fact,
    build_player_match_fact,
)

logger = get_logger(__name__)


def build_fact_tables(
    *,
    deliveries_df: pd.DataFrame,
    lookup_maps: dict[str, dict[str, int]],
) -> dict[str, pd.DataFrame]:
    """
    Build all warehouse fact tables.

    Parameters
    ----------
    deliveries_df : pd.DataFrame
        Engineered delivery dataset.

    lookup_maps : dict
        Surrogate-key lookup maps.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing all warehouse fact tables.
    """
    logger.info("Building warehouse fact tables.")

    facts = {
        "fact_delivery": build_delivery_fact(
            deliveries_df=deliveries_df,
            lookup_maps=lookup_maps,
        ),
        "fact_match": build_match_fact(
            deliveries_df=deliveries_df,
            lookup_maps=lookup_maps,
        ),
        "fact_player_match": build_player_match_fact(
            deliveries_df=deliveries_df,
            lookup_maps=lookup_maps,
        ),
    }

    logger.info(
        "Successfully built %d fact tables.",
        len(facts),
    )

    return facts


__all__ = [
    "build_fact_tables",
]