"""
Machine Learning constants for the IPL Analytics & Strategy Platform.

This module centralizes reusable configuration values shared across the
machine learning pipeline, including feature definitions, model settings,
training defaults, and evaluation metrics.
"""

from __future__ import annotations

# =============================================================================
# Feature Configuration
# =============================================================================

FEATURE_COLUMNS = [
    "season",
    "venue",
    "city",
    "team1",
    "team2",
    "toss_winner",
    "toss_decision",
    "match_type",
]

TARGET_COLUMNS = [
    "winner",
    "player_of_match",
]

# =============================================================================
# Data Splitting
# =============================================================================

DEFAULT_TEST_SIZE = 0.20

DEFAULT_RANDOM_STATE = 42

DEFAULT_SHUFFLE = True

# =============================================================================
# Cross Validation
# =============================================================================

DEFAULT_CV_FOLDS = 5

DEFAULT_SCORING = "accuracy"

# =============================================================================
# Model Configuration
# =============================================================================

SUPPORTED_MODELS = {
    "logistic_regression": "Logistic Regression",
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
}

DEFAULT_MODEL = "random_forest"

# =============================================================================
# Random Forest Defaults
# =============================================================================

RF_N_ESTIMATORS = 200

RF_MAX_DEPTH = None

RF_MIN_SAMPLES_SPLIT = 2

RF_MIN_SAMPLES_LEAF = 1

# =============================================================================
# Logistic Regression Defaults
# =============================================================================

LR_MAX_ITER = 1000

LR_SOLVER = "lbfgs"

# =============================================================================
# Evaluation Metrics
# =============================================================================

CLASSIFICATION_METRICS = [
    "accuracy",
    "precision",
    "recall",
    "f1_score",
]

# =============================================================================
# Exported Symbols
# =============================================================================

__all__ = [
    "FEATURE_COLUMNS",
    "TARGET_COLUMNS",
    "DEFAULT_TEST_SIZE",
    "DEFAULT_RANDOM_STATE",
    "DEFAULT_SHUFFLE",
    "DEFAULT_CV_FOLDS",
    "DEFAULT_SCORING",
    "SUPPORTED_MODELS",
    "DEFAULT_MODEL",
    "RF_N_ESTIMATORS",
    "RF_MAX_DEPTH",
    "RF_MIN_SAMPLES_SPLIT",
    "RF_MIN_SAMPLES_LEAF",
    "LR_MAX_ITER",
    "LR_SOLVER",
    "CLASSIFICATION_METRICS",
]