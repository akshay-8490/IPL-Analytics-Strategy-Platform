"""
Machine learning inference utilities.

This module performs inference using trained machine learning
models. It provides reusable prediction APIs without handling
preprocessing, training, or evaluation.
"""

from __future__ import annotations

import logging

import pandas as pd

from src.models.ml import (
    TrainingResult,
)

logger = logging.getLogger(__name__)

def _validate_input(
    features: pd.DataFrame,
) -> None:
    """
    Validate inference input.
    """

    if features.empty:

        raise ValueError(
            "Feature dataset cannot be empty."
        )
    
def predict(
    training_result: TrainingResult,
    features: pd.DataFrame,
):
    """
    Generate predictions using a trained model.

    Parameters
    ----------
    training_result : TrainingResult

    features : pd.DataFrame

    Returns
    -------
    pd.Series
    """

    logger.info(
        "Generating predictions."
    )

    predictions = training_result.model.predict(
        features
    )

    return pd.Series(
        predictions,
        name="prediction",
    )

def predict_probability(
    training_result: TrainingResult,
    features: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate prediction probabilities.

    Parameters
    ----------
    training_result : TrainingResult

    features : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    model = training_result.model

    if not hasattr(
        model,
        "predict_proba",
    ):

        raise ValueError(
            "Model does not support probability prediction."
        )

    probabilities = model.predict_proba(
        features
    )

    return pd.DataFrame(
        probabilities,
        columns=model.classes_,
    )

__all__ = [
    "predict",
    "predict_probability",
]