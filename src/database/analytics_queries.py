"""
Database analytics queries.

This module contains reusable SQL queries for the IPL Analytics & Strategy
Platform.

The module is divided into two logical sections:

1. Summary Queries
   Reusable SQL summary queries for reporting, validation, and dashboarding.

2. Dataset Queries
   Canonical analytical datasets reconstructed from the warehouse.
   These datasets are consumed by the NB6 Analytics Framework.
"""

from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def get_match_summary_query() -> str:
    """
    Build the warehouse match summary query.
    """
    return """
        SELECT
            m.match_key,
            m.match_id,
            s.season,
            t1.team_name AS team1,
            t2.team_name AS team2,
            v.venue,
            m.match_date,
            fm.total_runs,
            fm.total_wickets,
            fm.total_boundaries,
            fm.total_fours,
            fm.total_sixes,
            fm.total_extras,
            fm.total_overs
        FROM dim_match m
        INNER JOIN fact_match fm
            ON m.match_key = fm.match_key
        INNER JOIN dim_team t1
            ON m.team1_key = t1.team_key
        INNER JOIN dim_team t2
            ON m.team2_key = t2.team_key
        INNER JOIN dim_season s
            ON m.season_key = s.season_key
        INNER JOIN dim_venue v
            ON m.venue_key = v.venue_key
        ORDER BY
            m.match_date;
    """


def get_team_summary_query() -> str:
    """
    Build team performance summary.
    """
    return """
        SELECT
            t.team_name,
            COUNT(DISTINCT fm.match_key) AS matches_played,
            SUM(fm.total_runs) AS total_runs,
            SUM(fm.total_wickets) AS total_wickets,
            AVG(fm.total_runs) AS avg_runs,
            AVG(fm.total_wickets) AS avg_wickets
        FROM fact_match fm
        INNER JOIN dim_team t
            ON fm.team1_key = t.team_key
        GROUP BY
            t.team_name
        ORDER BY
            matches_played DESC;
    """


def get_player_summary_query() -> str:
    """
    Build player batting summary.
    """
    return """
        SELECT
            p.player_name,
            COUNT(*) AS matches,
            SUM(fpm.batting_runs) AS runs,
            SUM(fpm.balls_faced) AS balls,
            SUM(fpm.fours) AS fours,
            SUM(fpm.sixes) AS sixes,
            SUM(fpm.dismissals) AS dismissals,
            ROUND(
                SUM(fpm.batting_runs) /
                NULLIF(
                    SUM(fpm.dismissals),
                    0
                ),
                2
            ) AS batting_average,
            ROUND(
                100 *
                SUM(fpm.batting_runs) /
                NULLIF(
                    SUM(fpm.balls_faced),
                    0
                ),
                2
            ) AS strike_rate
        FROM fact_player_match fpm
        INNER JOIN dim_player p
            ON fpm.player_key = p.player_key
        GROUP BY
            p.player_name
        ORDER BY
            runs DESC;
    """


def get_season_summary_query() -> str:
    """
    Build season summary.
    """
    return """
        SELECT
            s.season,
            COUNT(DISTINCT m.match_key) AS matches,
            SUM(fm.total_runs) AS runs,
            SUM(fm.total_wickets) AS wickets,
            AVG(fm.total_runs) AS avg_runs,
            AVG(fm.total_wickets) AS avg_wickets
        FROM dim_season s
        INNER JOIN dim_match m
            ON s.season_key = m.season_key
        INNER JOIN fact_match fm
            ON m.match_key = fm.match_key
        GROUP BY
            s.season
        ORDER BY
            s.season;
    """


def get_analytics_queries() -> Dict[str, str]:
    """
    Return reusable analytical SQL queries.
    """
    logger.debug("Building analytics query registry.")
    return {
        "match_summary": get_match_summary_query(),
        "team_summary": get_team_summary_query(),
        "player_summary": get_player_summary_query(),
        "season_summary": get_season_summary_query(),
    }

# ============================================================================
# Dataset Queries (NB6 Analytics Framework)
# ============================================================================

def get_match_dataset_query() -> str:
    """
    Build the canonical match-level analytical dataset.

    The returned dataset reconstructs a business-friendly match DataFrame
    from the warehouse star schema.

    Returns
    -------
    str
        SQL query returning one row per match.
    """

    return """
        SELECT

            -- Match Identity
            m.match_key,
            m.match_id,

            -- Season
            s.season,

            -- Match Metadata
            m.match_date AS date,
            m.match_type,

            -- Teams
            t1.team_name AS team1,
            t2.team_name AS team2,

            -- Venue
            v.venue,
            v.city,

            -- Toss
            toss.team_name AS toss_winner,
            m.toss_decision,

            -- Match Result
            winner.team_name AS winner,
            m.win_type,
            m.win_margin,
            CASE WHEN m.win_type = 'runs' THEN m.win_margin ELSE NULL END AS winner_runs,
            CASE WHEN m.win_type = 'wickets' THEN m.win_margin ELSE NULL END AS winner_wickets,
            m.outcome,
            m.method,

            -- Awards
            m.player_of_match,

            -- Match Measures
            fm.total_runs,
            fm.total_wickets,
            fm.total_boundaries,
            fm.total_fours,
            fm.total_sixes,
            fm.total_extras,
            fm.total_legal_deliveries,
            fm.total_overs

        FROM fact_match fm

        INNER JOIN dim_match m
            ON fm.match_key = m.match_key

        INNER JOIN dim_season s
            ON m.season_key = s.season_key

        INNER JOIN dim_venue v
            ON m.venue_key = v.venue_key

        INNER JOIN dim_team t1
            ON m.team1_key = t1.team_key

        INNER JOIN dim_team t2
            ON m.team2_key = t2.team_key

        LEFT JOIN dim_team toss
            ON m.toss_winner_key = toss.team_key

        LEFT JOIN dim_team winner
            ON m.winner_key = winner.team_key

        ORDER BY
            s.season,
            m.match_date,
            m.match_id;
    """

def get_player_dataset_query() -> str:
    """
    Build the canonical player-match analytical dataset.

    The returned dataset reconstructs player-match records from the
    warehouse star schema.

    Returns
    -------
    str
        SQL query returning one row per player per match.
    """

    return """
        SELECT

            -- Player Identity
            p.player_key,
            p.player_name,

            -- Match Identity
            m.match_key,
            m.match_id,

            -- Season
            s.season,

            -- Match Metadata
            m.match_date,
            m.match_type,

            -- Batting Statistics
            fpm.batting_runs,
            fpm.balls_faced,
            fpm.fours,
            fpm.sixes,
            fpm.dismissals

        FROM fact_player_match fpm

        INNER JOIN dim_player p
            ON fpm.player_key = p.player_key

        INNER JOIN dim_match m
            ON fpm.match_key = m.match_key

        INNER JOIN dim_season s
            ON m.season_key = s.season_key

        ORDER BY
            p.player_name,
            s.season,
            m.match_date,
            m.match_id;
    """

def get_delivery_dataset_query() -> str:
    """
    Build the canonical delivery-level analytical dataset.

    The returned dataset reconstructs ball-by-ball records from the
    warehouse star schema.

    Returns
    -------
    str
        SQL query returning one row per delivery.
    """

    return """
        SELECT

            -- Match Identity
            m.match_key,
            m.match_id,

            -- Season
            s.season,

            -- Match Metadata
            m.match_date,

            -- Teams
            batting.team_name AS batting_team,
            bowling.team_name AS bowling_team,

            -- Players
            batter.player_name AS batter,
            bowler.player_name AS bowler,
            non_striker.player_name AS non_striker,
            fielder.player_name AS fielder,
            player_out.player_name AS player_out,

            -- Delivery Information
            fd.innings,
            fd.over_number,
            fd.ball_number,

            -- Runs
            fd.runs_off_bat,
            fd.extras,
            fd.total_runs,

            -- Delivery Flags
            fd.is_boundary,
            fd.is_four,
            fd.is_six,
            fd.is_dot_ball,
            fd.is_wicket,
            fd.is_legal_delivery,

            -- Extra Information
            fd.extra_type

        FROM fact_delivery fd

        INNER JOIN dim_match m
            ON fd.match_key = m.match_key

        INNER JOIN dim_season s
            ON fd.season_key = s.season_key

        INNER JOIN dim_team batting
            ON fd.batting_team_key = batting.team_key

        INNER JOIN dim_team bowling
            ON fd.bowling_team_key = bowling.team_key

        INNER JOIN dim_player batter
            ON fd.batter_key = batter.player_key

        INNER JOIN dim_player bowler
            ON fd.bowler_key = bowler.player_key

        INNER JOIN dim_player non_striker
            ON fd.non_striker_key = non_striker.player_key

        LEFT JOIN dim_player fielder
            ON fd.fielder_key = fielder.player_key

        LEFT JOIN dim_player player_out
            ON fd.player_out_key = player_out.player_key

        ORDER BY
            s.season,
            m.match_date,
            m.match_id,
            fd.innings,
            fd.over_number,
            fd.ball_number;
    """

def get_dataset_queries() -> Dict[str, str]:
    """
    Return canonical analytical dataset queries.

    These datasets are consumed by the NB6 Analytics Framework.
    """

    logger.debug("Building analytics dataset query registry.")

    return {
        "match": get_match_dataset_query(),
        "player": get_player_dataset_query(),
        "delivery": get_delivery_dataset_query(),
    }

__all__ = [
    "get_match_summary_query",
    "get_team_summary_query",
    "get_player_summary_query",
    "get_season_summary_query",
    "get_analytics_queries",
    "get_match_dataset_query",
    "get_player_dataset_query",
    "get_delivery_dataset_query",
    "get_dataset_queries",
]