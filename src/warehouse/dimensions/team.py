"""
Team dimension builder.
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _extract_unique_teams(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extract the canonical list of IPL teams from the engineered
    match dataset.
    """
    logger.info("Extracting unique IPL teams.")

    required_columns = {"team1", "team2"}
    missing_columns = required_columns.difference(matches_df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns for team extraction: "
            f"{sorted(missing_columns)}"
        )

    teams = pd.concat(
        [
            matches_df["team1"],
            matches_df["team2"],
        ],
        ignore_index=True,
    )

    team_dimension = (
        teams
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
        .to_frame(name="team_name")
    )

    logger.info(
        "Extracted %d unique teams.",
        len(team_dimension),
    )

    return team_dimension


def _generate_team_short_name(team_name: str) -> str:
    """
    Generate the official IPL short name for a team.
    """
    team_short_names = {
        "Chennai Super Kings": "CSK",
        "Delhi Capitals": "DC",
        "Delhi Daredevils": "DD",
        "Deccan Chargers": "DCG",
        "Gujarat Titans": "GT",
        "Gujarat Lions": "GL",
        "Kings XI Punjab": "KXIP",
        "Kings Xi Punjab": "KXIP",
        "Punjab Kings": "PBKS",
        "Kochi Tuskers Kerala": "KTK",
        "Kolkata Knight Riders": "KKR",
        "Lucknow Super Giants": "LSG",
        "Mumbai Indians": "MI",
        "Pune Warriors": "PWI",
        "Pune Warriors India": "PWI",
        "Rajasthan Royals": "RR",
        "Rising Pune Supergiant": "RPS",
        "Rising Pune Supergiants": "RPS",
        "Royal Challengers Bangalore": "RCB",
        "Royal Challengers Bengaluru": "RCB",
        "Sunrisers Hyderabad": "SRH",
    }

    return team_short_names.get(team_name, team_name)


def build_team_dimension(
    *,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Team dimension.
    """
    logger.info("Building Team dimension.")

    teams = _extract_unique_teams(
        matches_df=matches_df,
    )

    teams["team_short_name"] = teams["team_name"].apply(
        _generate_team_short_name
    )

    team_seasons = pd.concat(
        [
            matches_df[["team1", "season"]].rename(
                columns={"team1": "team_name"}
            ),
            matches_df[["team2", "season"]].rename(
                columns={"team2": "team_name"}
            ),
        ],
        ignore_index=True,
    )

    season_summary = (
        team_seasons
        .groupby("team_name", as_index=False)
        .agg(
            first_season=("season", "min"),
            last_season=("season", "max"),
        )
    )

    team_dimension = (
        teams
        .merge(
            season_summary,
            on="team_name",
            how="left",
        )
        .sort_values("team_name")
        .reset_index(drop=True)
    )

    logger.info(
        "Built Team dimension with %d teams.",
        len(team_dimension),
    )

    return team_dimension
