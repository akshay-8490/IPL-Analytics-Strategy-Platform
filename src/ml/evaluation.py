"""
Machine learning evaluation utilities.

This module evaluates trained machine learning models and
generates reusable evaluation metrics.
"""

from __future__ import annotations

import logging

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

from sklearn.model_selection import cross_val_score

from src.ml.constants import (
    DEFAULT_CV_FOLDS,
    DEFAULT_SCORING,
)

from src.models.ml import (
    EvaluationResult,
    PreprocessedDataset,
    TrainingResult,
)

logger = logging.getLogger(__name__)

def _predict(
    training_result: TrainingResult,
    dataset: PreprocessedDataset,
):
    """
    Generate predictions on the test dataset.
    """

    return training_result.model.predict(
        dataset.X_test
    )

def _compute_metrics(
    y_true,
    y_pred,
) -> dict[str, float]:
    """
    Compute classification metrics.
    """

    return {

        "accuracy": accuracy_score(
            y_true,
            y_pred,
        ),

        "precision": precision_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),

        "recall": recall_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),

        "f1_score": f1_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
    }

def _build_confusion_matrix(
    y_true,
    y_pred,
) -> pd.DataFrame:
    """
    Build confusion matrix.
    """

    matrix = confusion_matrix(
        y_true,
        y_pred,
    )

    return pd.DataFrame(matrix)

def _build_classification_report(
    y_true,
    y_pred,
) -> pd.DataFrame:
    """
    Build classification report.
    """

    report = classification_report(

        y_true,

        y_pred,

        output_dict=True,

        zero_division=0,

    )

    return pd.DataFrame(report).transpose()

def _extract_feature_importance(
    training_result: TrainingResult,
    dataset: PreprocessedDataset,
) -> pd.DataFrame | None:
    """
    Extract feature importance when supported.
    """

    model = training_result.model

    if not hasattr(
        model,
        "feature_importances_",
    ):

        return None

    importance = pd.DataFrame({

        "feature": dataset.feature_names,

        "importance": model.feature_importances_,

    })

    return importance.sort_values(

        by="importance",

        ascending=False,

        ignore_index=True,

    )

def evaluate_model(
    training_result: TrainingResult,
    dataset: PreprocessedDataset,
) -> EvaluationResult:
    """
    Evaluate a trained machine learning model.
    """

    logger.info(
        "Evaluating model."
    )

    predictions = _predict(
        training_result,
        dataset,
    )

    metrics = _compute_metrics(

        dataset.y_test,

        predictions,

    )

    confusion = _build_confusion_matrix(

        dataset.y_test,

        predictions,

    )

    report = _build_classification_report(

        dataset.y_test,

        predictions,

    )

    importance = _extract_feature_importance(
        training_result,
        dataset,
    )

    logger.info(
        "Running cross validation."
    )

    cv_scores = cross_val_score(
        estimator=training_result.model,
        X=dataset.X_train,
        y=dataset.y_train,
        cv=DEFAULT_CV_FOLDS,
        scoring=DEFAULT_SCORING,
    )

    cv_mean = float(cv_scores.mean())
    cv_std = float(cv_scores.std())

    logger.info(
        "Evaluation completed."
    )

    return EvaluationResult(
        accuracy=metrics["accuracy"],
        precision=metrics["precision"],
        recall=metrics["recall"],
        f1_score=metrics["f1_score"],
        confusion_matrix=confusion,
        classification_report=report,
        cv_mean_accuracy=cv_mean,
        cv_std_accuracy=cv_std,
        feature_importance=importance,
    )

__all__ = [
    "evaluate_model",
]