"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: constants.py

Description:
    Centralized constants and configuration values used
    throughout the ETL pipeline.

Purpose:
    - Eliminate hardcoded values.
    - Maintain a single source of truth.
    - Improve consistency and maintainability.

Used By:
    - cleaners.py
    - standardizers.py
    - normalizers.py
    - validators.py
    - feature_builder.py
    - match_info.py

===========================================================
"""

from __future__ import annotations

from src.schemas.columns import (
    DATE_COL,
    MATCH_ID_COL,
    SEASON_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
)

# ===========================================================
# Missing Value Constants
# ===========================================================

DEFAULT_MISSING_VALUES: tuple[str, ...] = (
    "",
    " ",
    "NA",
    "N/A",
    "NULL",
    "null",
    "None",
)


# ===========================================================
# Date & Time Constants
# ===========================================================

DEFAULT_DATE_FORMAT = "%Y-%m-%d"

DATE_COLUMNS: tuple[str, ...] = (
    DATE_COL,
)

DEFAULT_BALLS_PER_OVER = 6

REQUIRED_MATCH_COLUMNS: tuple[str, ...] = (
    MATCH_ID_COL,
    SEASON_COL,
    DATE_COL,
    TEAM1_COL,
    TEAM2_COL,
    VENUE_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
)


# ===========================================================
# Valid Enumerations
# ===========================================================

VALID_TOSS_DECISIONS = {
    "bat",
    "field",
}


# ===========================================================
# Canonical Mappings
# ===========================================================

# -----------------------------------------------------------
# Season Mapping
#
# Cricsheet stores some IPL seasons spanning two calendar
# years (e.g., "2007/08"). These are normalized to the
# ending year for analytical consistency.
# -----------------------------------------------------------

SEASON_MAPPING: dict[str, str] = {
    "2007/08": "2008",
    "2009/10": "2010",
    "2020/21": "2021",
}


# -----------------------------------------------------------
# Team Name Mapping
#
# Canonical franchise names used throughout the project.
# -----------------------------------------------------------

TEAM_NAME_MAPPING: dict[str, str] = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
}


# -----------------------------------------------------------
# City Mapping
#
# Historical city names mapped to their current official
# representation.
# -----------------------------------------------------------

CITY_MAPPING: dict[str, str] = {
    "Bangalore": "Bengaluru",
}


# -----------------------------------------------------------
# Venue Mapping
#
# Different historical representations of the same venue
# are mapped to one canonical venue name.
# -----------------------------------------------------------

VENUE_MAPPING: dict[str, str] = {
    "Arun Jaitley Stadium":
        "Arun Jaitley Stadium, Delhi",

    "Brabourne Stadium":
        "Brabourne Stadium, Mumbai",

    "Dr DY Patil Sports Academy":
        "Dr DY Patil Sports Academy, Mumbai",

    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium":
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",

    "Eden Gardens":
        "Eden Gardens, Kolkata",

    "Himachal Pradesh Cricket Association Stadium":
        "Himachal Pradesh Cricket Association Stadium, Dharamsala",

    "M Chinnaswamy Stadium":
        "M Chinnaswamy Stadium, Bengaluru",

    "M.Chinnaswamy Stadium":
        "M Chinnaswamy Stadium, Bengaluru",

    "MA Chidambaram Stadium":
        "MA Chidambaram Stadium, Chepauk, Chennai",

    "MA Chidambaram Stadium, Chepauk":
        "MA Chidambaram Stadium, Chepauk, Chennai",

    "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur":
        "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh",

    "Maharashtra Cricket Association Stadium":
        "Maharashtra Cricket Association Stadium, Pune",

    "Punjab Cricket Association IS Bindra Stadium":
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",

    "Punjab Cricket Association IS Bindra Stadium, Mohali":
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",

    "Punjab Cricket Association Stadium, Mohali":
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",

    "Rajiv Gandhi International Stadium":
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad",

    "Rajiv Gandhi International Stadium, Uppal":
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad",

    "Sawai Mansingh Stadium":
        "Sawai Mansingh Stadium, Jaipur",

    "Shaheed Veer Narayan Singh International Stadium":
        "Shaheed Veer Narayan Singh International Stadium, Raipur",

    "Wankhede Stadium":
        "Wankhede Stadium, Mumbai",
}

# ===========================================================
# Public Exports
# ===========================================================

__all__ = [
    "DEFAULT_MISSING_VALUES",
    "DEFAULT_DATE_FORMAT",
    "DATE_COLUMNS",
    "DEFAULT_BALLS_PER_OVER",
    "REQUIRED_MATCH_COLUMNS",
    "VALID_TOSS_DECISIONS",
    "SEASON_MAPPING",
    "TEAM_NAME_MAPPING",
    "CITY_MAPPING",
    "VENUE_MAPPING",
]