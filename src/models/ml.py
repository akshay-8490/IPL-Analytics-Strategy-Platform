from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

@dataclass(frozen=True)
class PreprocessedDataset:
    """
    Container for preprocessed machine learning datasets.
    """

    X_train: pd.DataFrame

    X_test: pd.DataFrame

    y_train: pd.Series

    y_test: pd.Series

    feature_names: list[str]

@dataclass(frozen=True)
class FeatureEngineeringResult:
    """
    Container for engineered feature datasets.
    """

    dataset: PreprocessedDataset

    selected_features: list[str]

    feature_importance: pd.DataFrame | None = None

@dataclass(frozen=True)
class TrainingResult:
    """
    Container for trained machine learning model.
    """

    model: Any

    model_name: str

    training_time: float

@dataclass(frozen=True)
class EvaluationResult:
    """
    Container for evaluation metrics.
    """

    accuracy: float

    precision: float

    recall: float

    f1_score: float

    confusion_matrix: pd.DataFrame

    classification_report: pd.DataFrame

    cv_mean_accuracy: float

    cv_std_accuracy: float

    feature_importance: pd.DataFrame | None = None

@dataclass(frozen=True)
class MLPipelineResult:
    """
    Final result returned by the ML workflow.
    """

    target_column: str

    training_result: TrainingResult

    evaluation_result: EvaluationResult

    preprocessed_dataset: PreprocessedDataset

    execution_time: float

    status: str

__all__ = [
    "PreprocessedDataset",
    "FeatureEngineeringResult",
    "TrainingResult",
    "EvaluationResult",
    "MLPipelineResult",
]