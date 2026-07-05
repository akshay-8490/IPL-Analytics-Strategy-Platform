from __future__ import annotations

import logging

import pandas as pd

from src.database.analytics_queries import (
    get_dataset_queries,
)
from src.database.connection import (
    create_connection,
    close_connection,
)
from src.analytics.transformations import (
    build_team_dataset,
    build_team_pair_dataset,
)
from src.models import AnalyticsDatasetBundle

logger = logging.getLogger(__name__)

def _load_dataframe(
    *,
    connection,
    query: str,
) -> pd.DataFrame:
    """
    Execute an analytical SQL query and return a DataFrame.

    Parameters
    ----------
    connection
        Active database connection.

    query : str
        SQL query.

    Returns
    -------
    pd.DataFrame
    """

    return pd.read_sql(
        sql=query,
        con=connection,
    )

queries = get_dataset_queries()

def load_match_dataset(
    connection,
) -> pd.DataFrame:
    """
    Load the canonical match analytical dataset.

    Parameters
    ----------
    connection
        Active database connection.

    Returns
    -------
    pd.DataFrame
        Match-level analytical dataset.
    """

    logger.info("Loading match analytical dataset.")

    match_query = queries["match"]

    return _load_dataframe(
        connection=connection,
        query=match_query,
    )

def load_player_dataset(
    connection,
) -> pd.DataFrame:
    """
    Load the canonical player analytical dataset.

    Parameters
    ----------
    connection
        Active database connection.

    Returns
    -------
    pd.DataFrame
        Player-match analytical dataset.
    """

    logger.info("Loading player analytical dataset.")

    player_query = queries["player"]

    return _load_dataframe(
        connection=connection,
        query=player_query,
    )

def load_delivery_dataset(
    connection,
) -> pd.DataFrame:
    """
    Load the canonical delivery analytical dataset.

    Parameters
    ----------
    connection
        Active database connection.

    Returns
    -------
    pd.DataFrame
        Delivery-level analytical dataset.
    """

    logger.info("Loading delivery analytical dataset.")

    delivery_query = queries["delivery"]

    return _load_dataframe(
        connection=connection,
        query=delivery_query,
    )

def load_analytics_datasets() -> AnalyticsDatasetBundle:
    """
    Load all analytical datasets from the warehouse.

    Returns
    -------
    AnalyticsDatasetBundle
        Collection of analytics-ready DataFrames.
    """

    logger.info("Loading analytics datasets from warehouse.")

    connection = create_connection()

    try:
        match_df = load_match_dataset(connection)
        player_df = load_player_dataset(connection)
        delivery_df = load_delivery_dataset(connection)

        logger.info("Building derived analytical datasets.")

        team_df = build_team_dataset(match_df)

        head_to_head_df = build_team_pair_dataset(match_df)

        logger.info("Analytics datasets successfully loaded.")

        return AnalyticsDatasetBundle(
            match_df=match_df,
            player_df=player_df,
            delivery_df=delivery_df,
            team_df=team_df,
            head_to_head_df=head_to_head_df,
        )

    finally:
        close_connection(connection)

__all__ = [
    "AnalyticsDatasetBundle",
    "load_match_dataset",
    "load_player_dataset",
    "load_delivery_dataset",
    "load_analytics_datasets",
]