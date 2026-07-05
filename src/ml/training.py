"""
Machine learning model training.
"""

from __future__ import annotations

import logging
import time

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

from src.ml.constants import (
    DEFAULT_MODEL,
    LR_MAX_ITER,
    LR_SOLVER,
    RF_MAX_DEPTH,
    RF_MIN_SAMPLES_LEAF,
    RF_MIN_SAMPLES_SPLIT,
    RF_N_ESTIMATORS,
)

from src.models.ml import (
    PreprocessedDataset,
    TrainingResult,
)

logger = logging.getLogger(__name__)


class TargetEncodingClassifier(BaseEstimator, ClassifierMixin):
    """
    Wrapper classifier that encodes string targets to integers during fit
    and decodes them back to strings during predict.
    """

    def __init__(self, estimator):
        self.estimator = estimator
        self.label_encoder = LabelEncoder()

    def fit(self, X, y):
        y_encoded = self.label_encoder.fit_transform(y)
        self.estimator.fit(X, y_encoded)
        self.classes_ = self.label_encoder.classes_
        return self

    def predict(self, X):
        y_pred_encoded = self.estimator.predict(X)
        return self.label_encoder.inverse_transform(y_pred_encoded)

    def predict_proba(self, X):
        return self.estimator.predict_proba(X)

    @property
    def feature_importances_(self):
        return getattr(self.estimator, "feature_importances_", None)


def _build_model(
    model_name: str,
):
    """
    Construct the requested classifier.
    """

    if model_name == "logistic_regression":

        return LogisticRegression(
            max_iter=LR_MAX_ITER,
            solver=LR_SOLVER,
            random_state=42,
        )

    if model_name == "decision_tree":

        return DecisionTreeClassifier(
            random_state=42,
        )

    if model_name == "random_forest":

        return RandomForestClassifier(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            min_samples_split=RF_MIN_SAMPLES_SPLIT,
            min_samples_leaf=RF_MIN_SAMPLES_LEAF,
            random_state=42,
        )

    if model_name == "xgboost":

        return TargetEncodingClassifier(
            XGBClassifier(
                random_state=42,
                eval_metric="mlogloss",
            )
        )

    if model_name == "lightgbm":

        return TargetEncodingClassifier(
            LGBMClassifier(
                random_state=42,
                verbose=-1,
            )
        )

    if model_name == "catboost":

        return CatBoostClassifier(
            random_state=42,
            verbose=0,
        )

    raise ValueError(
        f"Unsupported model: {model_name}"
    )

def _train(
    model,
    dataset: PreprocessedDataset,
):
    """
    Fit the model.
    """

    model.fit(

        dataset.X_train,

        dataset.y_train,

    )

    return model

def train_model(
    dataset: PreprocessedDataset,
    model_name: str = DEFAULT_MODEL,
) -> TrainingResult:
    """
    Train a machine learning model.
    """

    logger.info(
        "Training %s.",
        model_name,
    )

    start = time.perf_counter()

    model = _build_model(model_name)

    trained_model = _train(
        model,
        dataset,
    )

    elapsed = time.perf_counter() - start

    logger.info(
        "Training completed."
    )

    return TrainingResult(

        model=trained_model,

        model_name=model_name,

        training_time=elapsed,

    )

__all__ = [
    "train_model",
]