"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: models.py

Description:
    Domain models used during dataset discovery.

Purpose:
    - Represent Cricsheet match metadata.
    - Provide strongly-typed objects for ETL.
    - Avoid passing raw dictionaries throughout the pipeline.

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(slots=True)
class MatchMetadata:
    """
    Represents metadata extracted from a Cricsheet *_info.csv file.
    """

    match_id: int | None = None

    season: Optional[str] = None

    date: Optional[str] = None

    team1: Optional[str] = None

    team2: Optional[str] = None

    venue: Optional[str] = None

    city: Optional[str] = None

    winner: Optional[str] = None

    toss_winner: Optional[str] = None

    toss_decision: Optional[str] = None

    player_of_match: Optional[str] = None

    gender: Optional[str] = None

    match_type: Optional[str] = None

    winner_runs: Optional[int] = None

    winner_wickets: Optional[int] = None

    balls_per_over: Optional[int] = None

    match_number: Optional[str] = None

    target_runs: Optional[int] = None

    target_overs: Optional[int] = None

    event_name: Optional[str] = None

    stage: Optional[str] = None

    overs: Optional[int] = None

    method: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert MatchMetadata to a dictionary.

        Returns
        -------
        dict
        """

        return asdict(self)