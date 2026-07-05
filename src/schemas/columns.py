"""
Canonical dataframe column names used throughout the project.

This module serves as the single source of truth for all
column names referenced across ETL, analytics, warehouse,
database, and machine learning components.
"""

__all__ = [

    # Match identifiers
    "MATCH_ID_COL",

    # Match metadata
    "SEASON_COL",
    "DATE_COL",
    "MATCH_TYPE_COL",

    # Teams
    "TEAM1_COL",
    "TEAM2_COL",

    # Venue
    "VENUE_COL",
    "CITY_COL",

    # Toss
    "TOSS_WINNER_COL",
    "TOSS_DECISION_COL",

    # Match Result
    "WINNER_COL",
    "WIN_BY_RUNS_COL",
    "WIN_BY_WICKETS_COL",

    # Awards
    "PLAYER_OF_MATCH_COL",
]

# ============================================================================
# Match Identifier
# ============================================================================

MATCH_ID_COL = "match_id"

# ============================================================================
# Match Metadata
# ============================================================================

SEASON_COL = "season"

DATE_COL = "date"

MATCH_TYPE_COL = "match_type"

# ============================================================================
# Teams
# ============================================================================

TEAM1_COL = "team1"

TEAM2_COL = "team2"

# ============================================================================
# Venue
# ============================================================================

VENUE_COL = "venue"

CITY_COL = "city"

# ============================================================================
# Toss
# ============================================================================

TOSS_WINNER_COL = "toss_winner"

TOSS_DECISION_COL = "toss_decision"

# ============================================================================
# Match Result
# ============================================================================

WINNER_COL = "winner"

WIN_BY_RUNS_COL = "winner_runs"

WIN_BY_WICKETS_COL = "winner_wickets"

# ============================================================================
# Awards
# ============================================================================

PLAYER_OF_MATCH_COL = "player_of_match"