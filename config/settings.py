"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: settings.py

Description:
    Global project settings and constants.

Purpose:
    - Store reusable configuration values.
    - Maintain a single source of truth.
    - Avoid hardcoded constants across the project.

===========================================================
"""

# ===========================================================
# Project Metadata
# ===========================================================

PROJECT_NAME = "IPL Analytics & Strategy Platform"
PROJECT_VERSION = "1.0.0"

AUTHOR = ""


# ===========================================================
# Dataset Configuration
# ===========================================================

DATA_SOURCE = "Cricsheet"

SUPPORTED_FILE_FORMATS = (
    ".csv",
    ".json",
    ".yaml",
)


# ===========================================================
# IPL Configuration
# ===========================================================

IPL_START_YEAR = 2008

# Update this every new IPL season
CURRENT_SEASON = 2026


# ===========================================================
# Machine Learning Configuration
# ===========================================================

RANDOM_STATE = 42

TEST_SIZE = 0.20

CV_FOLDS = 5


# ===========================================================
# Logging Configuration
# ===========================================================

LOG_LEVEL = "INFO"


# ===========================================================
# Visualization Defaults
# ===========================================================

DEFAULT_FIGURE_DPI = 300

DEFAULT_FIGURE_FORMAT = "png"


# ===========================================================
# Export Configuration
# ===========================================================

DEFAULT_EXPORT_FORMAT = "csv"

# ===========================================================
# Database Configuration
# ===========================================================

# MySQL Server
MYSQL_HOST = "127.0.0.1"

MYSQL_PORT = 3306

MYSQL_USER = "root"

MYSQL_PASSWORD = "SQLdatabase05@"

# IPL Warehouse Database
MYSQL_DATABASE = "ipl_analytics"

# Connection Settings
MYSQL_CHARSET = "utf8mb4"

MYSQL_AUTOCOMMIT = False

MYSQL_CONNECT_TIMEOUT = 10