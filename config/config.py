"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: config.py

Description:
    Unified configuration interface for the project.

Purpose:
    - Re-export commonly used paths and settings.
    - Provide a single import point across notebooks and modules.

===========================================================
"""

# ===========================================================
# Import Project Paths
# ===========================================================

from .paths import (
    PROJECT_ROOT,
    CONFIG_DIR,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    STAGING_DIR,
    WAREHOUSE_DIR,
    DIMENSIONS_DIR,
    FACTS_DIR,
    ANALYTICS_DATA_DIR,
    CRICSHEET_DIR,
    NOTEBOOKS_DIR,
    SRC_DIR,
    MODELS_DIR,
    POWERBI_DIR,
    RELEASE_DIR,
    POWERBI_DATASET_DIR,
    POWERBI_PBIX_DIR,
)

# ===========================================================
# Import Project Settings
# ===========================================================

from .settings import (
    PROJECT_NAME,
    PROJECT_VERSION,
    AUTHOR,
    DATA_SOURCE,
    SUPPORTED_FILE_FORMATS,
    IPL_START_YEAR,
    CURRENT_SEASON,
    RANDOM_STATE,
    TEST_SIZE,
    CV_FOLDS,
    LOG_LEVEL,
    DEFAULT_FIGURE_DPI,
    DEFAULT_FIGURE_FORMAT,
    DEFAULT_EXPORT_FORMAT,

    # Database
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_CHARSET,
    MYSQL_AUTOCOMMIT,
    MYSQL_CONNECT_TIMEOUT,
)

# ===========================================================
# Public API
# ===========================================================

__all__ = [
    # Paths
    "PROJECT_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "STAGING_DIR",
    "WAREHOUSE_DIR",
    "DIMENSIONS_DIR",
    "FACTS_DIR",
    "ANALYTICS_DATA_DIR",
    "CRICSHEET_DIR",
    "NOTEBOOKS_DIR",
    "SRC_DIR",
    "MODELS_DIR",
    "POWERBI_DIR",
    "RELEASE_DIR",
    "POWERBI_DATASET_DIR",
    "POWERBI_PBIX_DIR",

    # Settings
    "PROJECT_NAME",
    "PROJECT_VERSION",
    "AUTHOR",
    "DATA_SOURCE",
    "SUPPORTED_FILE_FORMATS",
    "IPL_START_YEAR",
    "CURRENT_SEASON",
    "RANDOM_STATE",
    "TEST_SIZE",
    "CV_FOLDS",
    "LOG_LEVEL",
    "DEFAULT_FIGURE_DPI",
    "DEFAULT_FIGURE_FORMAT",
    "DEFAULT_EXPORT_FORMAT",

    # Database
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
    "MYSQL_CHARSET",
    "MYSQL_AUTOCOMMIT",
    "MYSQL_CONNECT_TIMEOUT",
]