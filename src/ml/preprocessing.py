"""
Machine learning preprocessing.

This module prepares datasets for model training by validating
targets, encoding categorical variables, and performing
train-test splitting.
"""

from __future__ import annotations

import logging

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from src.ml.constants import (
    DEFAULT_RANDOM_STATE,
    DEFAULT_SHUFFLE,
    DEFAULT_TEST_SIZE,
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
)

from src.models.ml import (
    PreprocessedDataset,
)

logger = logging.getLogger(__name__)

def _validate_target(
    target_column: str,
) -> None:
    """
    Validate the requested target column.
    """

    if target_column not in TARGET_COLUMNS:

        raise ValueError(
            f"Unsupported target column: {target_column}"
        )
    
def _split_features_target(
    dataset: pd.DataFrame,
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Separate feature columns from the target.
    """

    X = dataset[FEATURE_COLUMNS].copy()

    y = dataset[target_column].copy()

    return X, y

def _encode_features(
    features: pd.DataFrame,
) -> pd.DataFrame:
    """
    Label encode all categorical features.
    """

    encoded = features.copy()

    for column in encoded.columns:

        encoder = LabelEncoder()

        encoded[column] = encoder.fit_transform(
            encoded[column].astype(str)
        )

    return encoded

def _create_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
) -> PreprocessedDataset:
    """
    Split data into train and test sets.
    """

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=DEFAULT_TEST_SIZE,

        random_state=DEFAULT_RANDOM_STATE,

        shuffle=DEFAULT_SHUFFLE,

        stratify=y,

    )

    return PreprocessedDataset(

        X_train=X_train,

        X_test=X_test,

        y_train=y_train,

        y_test=y_test,

        feature_names=list(X.columns),

    )

def preprocess_features(
    dataset: pd.DataFrame,
    target_column: str,
) -> PreprocessedDataset:
    """
    Prepare the machine learning dataset.

    Parameters
    ----------
    dataset : pd.DataFrame
        Machine learning dataset.

    target_column : str
        Prediction target.

    Returns
    -------
    PreprocessedDataset
    """

    logger.info(
        "Starting preprocessing."
    )

    _validate_target(target_column)

    # Filter out rows with null target values
    dataset = dataset.dropna(subset=[target_column])

    X, y = _split_features_target(
        dataset,
        target_column,
    )

    X = _encode_features(X)

    processed = _create_train_test_split(
        X,
        y,
    )

    logger.info(
        "Preprocessing completed."
    )

    return processed

__all__ = [
    "preprocess_features",
]