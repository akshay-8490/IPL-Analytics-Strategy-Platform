"""
Machine Learning workflow pipeline.

This module orchestrates the complete machine learning workflow,
including feature loading, preprocessing, training, evaluation,
and packaging of results.
"""

from __future__ import annotations

import logging
import time

from src.ml.constants import (
    DEFAULT_MODEL,
)

from src.ml.feature_loader import (
    load_feature_dataset,
)

from src.ml.preprocessing import (
    preprocess_features,
)

from src.ml.training import (
    train_model,
)

from src.ml.evaluation import (
    evaluate_model,
)

from src.models.ml import (
    MLPipelineResult,
)

logger = logging.getLogger(__name__)

def _run_training_pipeline(
    target_column: str,
    model_name: str,
) -> tuple:
    """
    Execute the complete training pipeline.
    """

    dataset = load_feature_dataset()

    processed = preprocess_features(
        dataset=dataset,
        target_column=target_column,
    )

    training_result = train_model(
        dataset=processed,
        model_name=model_name,
    )

    evaluation_result = evaluate_model(
        training_result=training_result,
        dataset=processed,
    )

    return (
        training_result,
        evaluation_result,
        processed,
    )

def run_ml_pipeline(
    target_column: str,
    model_name: str = DEFAULT_MODEL,
) -> MLPipelineResult:
    """
    Execute the complete machine learning pipeline.

    Parameters
    ----------
    target_column : str
        Prediction target.

    model_name : str
        Machine learning model.

    Returns
    -------
    MLPipelineResult
    """

    logger.info(
        "Starting ML pipeline."
    )

    start = time.perf_counter()

    status = "SUCCESS"

    try:

        (
            training_result,
            evaluation_result,
            preprocessed_dataset,
        ) = _run_training_pipeline(
            target_column=target_column,
            model_name=model_name,
        )

    except Exception:

        logger.exception(
            "ML pipeline failed."
        )

        status = "FAILED"

        raise

    finally:

        execution_time = (
            time.perf_counter() - start
        )

    logger.info(
        "ML pipeline completed."
    )

    return MLPipelineResult(

        target_column=target_column,

        training_result=training_result,

        evaluation_result=evaluation_result,

        preprocessed_dataset=preprocessed_dataset,

        execution_time=execution_time,

        status=status,
    )

__all__ = [
    "run_ml_pipeline",
]