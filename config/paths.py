"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: paths.py

Description:
    Centralized filesystem paths for the entire project.

Purpose:
    - Detect project root automatically.
    - Define reusable directory paths.
    - Avoid hardcoded paths across notebooks and modules.

===========================================================
"""

from pathlib import Path

# ===========================================================
# Project Root
# ===========================================================

# config/ -> Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ===========================================================
# Main Project Directories
# ===========================================================

CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SRC_DIR = PROJECT_ROOT / "src"

RELEASE_DIR = PROJECT_ROOT / "release"
MODELS_DIR = RELEASE_DIR / "models"
POWERBI_DIR = PROJECT_ROOT / "powerbi"


# ===========================================================
# Data Directories
# ===========================================================

# -----------------------------
# Raw Data (Immutable)
# -----------------------------

RAW_DATA_DIR = DATA_DIR / "raw"
CRICSHEET_DIR = RAW_DATA_DIR / "ipl_csv2"


# -----------------------------
# Processed Data (Silver Layer)
# -----------------------------

PROCESSED_DATA_DIR = DATA_DIR / "processed"

STAGING_DIR = PROCESSED_DATA_DIR / "staging"
WAREHOUSE_DIR = PROCESSED_DATA_DIR / "warehouse"
DIMENSIONS_DIR = WAREHOUSE_DIR / "dimensions"
FACTS_DIR = WAREHOUSE_DIR / "facts"


# -----------------------------
# Analytics Data (Gold Layer)
# -----------------------------

ANALYTICS_DATA_DIR = DATA_DIR / "analytics"




# ===========================================================
# Power BI
# ===========================================================

POWERBI_DATASET_DIR = POWERBI_DIR / "datasets"
POWERBI_PBIX_DIR = POWERBI_DIR / "pbix"


# ===========================================================
# Automatically Create Runtime Directories
# ===========================================================

REQUIRED_DIRECTORIES = [

    # Processed Layer
    STAGING_DIR,
    DIMENSIONS_DIR,
    FACTS_DIR,

    # Gold Layer
    ANALYTICS_DATA_DIR,

    # Models
    MODELS_DIR,

    # Power BI
    POWERBI_DATASET_DIR,
    POWERBI_PBIX_DIR,

    # Release
    RELEASE_DIR,
]

for directory in REQUIRED_DIRECTORIES:
    directory.mkdir(parents=True, exist_ok=True)


# ===========================================================
# Public Exports
# ===========================================================

__all__ = [
    # Project
    "PROJECT_ROOT",

    # Main Directories
    "CONFIG_DIR",
    "DATA_DIR",
    "NOTEBOOKS_DIR",
    "SRC_DIR",
    "MODELS_DIR",
    "POWERBI_DIR",
    "RELEASE_DIR",

    # Data
    "RAW_DATA_DIR",
    "CRICSHEET_DIR",
    "PROCESSED_DATA_DIR",
    "STAGING_DIR",
    "WAREHOUSE_DIR",
    "DIMENSIONS_DIR",
    "FACTS_DIR",
    "ANALYTICS_DATA_DIR",

    # Power BI
    "POWERBI_DATASET_DIR",
    "POWERBI_PBIX_DIR",
]