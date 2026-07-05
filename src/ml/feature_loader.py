"""
Machine Learning feature loader.

This module loads the canonical machine learning dataset from the
MySQL warehouse. It does not perform preprocessing, feature engineering,
or model training.
"""

from __future__ import annotations

import logging

import pandas as pd

from src.database.analytics_queries import (
    get_match_dataset_query,
)

from src.database.connection import (
    close_connection,
    create_connection,
)

from src.ml.constants import (
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
)

from src.analytics.validators import (
    validate_dataframe,
)

logger = logging.getLogger(__name__)

def _execute_query(
    query: str,
) -> pd.DataFrame:
    """
    Execute a SQL query and return the result as a DataFrame.

    Parameters
    ----------
    query : str
        SQL query to execute.

    Returns
    -------
    pd.DataFrame
        Query result.
    """

    logger.info("Loading machine learning dataset from warehouse.")

    connection = create_connection()

    try:
        dataset = pd.read_sql(
            sql=query,
            con=connection,
        )

    finally:
        close_connection(connection)

    logger.info(
        "Loaded %d records from warehouse.",
        len(dataset),
    )

    return dataset

def _validate_dataset(
    dataset: pd.DataFrame,
) -> None:
    """
    Validate the machine learning dataset.

    Parameters
    ----------
    dataset : pd.DataFrame
        Dataset returned from the warehouse.
    """

    validate_dataframe(dataset)

    required_columns = FEATURE_COLUMNS + TARGET_COLUMNS

    missing_columns = [
        column
        for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            f"{missing_columns}"
        )

    logger.info(
        "Machine learning dataset validation completed."
    )

def _select_feature_columns(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    """
    Select machine learning features and targets.

    Parameters
    ----------
    dataset : pd.DataFrame
        Canonical warehouse dataset.

    Returns
    -------
    pd.DataFrame
        Machine learning dataset.
    """

    selected_columns = (
        FEATURE_COLUMNS
        + TARGET_COLUMNS
    )

    ml_dataset = (
        dataset[selected_columns]
        .copy()
    )

    logger.info(
        "Selected %d columns for ML.",
        len(selected_columns),
    )

    return ml_dataset

def load_feature_dataset(
) -> pd.DataFrame:
    """
    Load the canonical machine learning dataset.

    Returns
    -------
    pd.DataFrame
        Machine learning dataset containing
        features and supported target columns.
    """

    logger.info(
        "Starting machine learning dataset loading."
    )

    dataset = _execute_query(
        get_match_dataset_query()
    )

    _validate_dataset(dataset)

    ml_dataset = _select_feature_columns(
        dataset
    )

    logger.info(
        "Machine learning dataset ready."
    )

    return ml_dataset

__all__ = [
    "load_feature_dataset",
]