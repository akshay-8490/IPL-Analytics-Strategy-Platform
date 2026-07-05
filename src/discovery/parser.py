"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: parser.py

Description:
    Parser for Cricsheet *_info.csv files.

Purpose:
    - Parse match metadata.
    - Convert raw CSV records into MatchMetadata objects.

===========================================================
"""

from __future__ import annotations

import csv
from pathlib import Path


from src.models import MatchMetadata
from src.utils.file_utils import extract_match_id
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class MatchInfoParser:
    """
    Parser for Cricsheet match information files.
    """

    FIELD_MAPPING = {
        "season": "season",
        "date": "date",
        "venue": "venue",
        "city": "city",
        "gender": "gender",
        "match_type": "match_type",
        "winner": "winner",
        "winner_runs": "winner_runs",
        "winner_wickets": "winner_wickets",
        "toss_winner": "toss_winner",
        "toss_decision": "toss_decision",
        "player_of_match": "player_of_match",
        "overs": "overs",
        "balls_per_over": "balls_per_over",
    }

    def parse(self, file_path: Path) -> MatchMetadata:
        """
        Parse a Cricsheet *_info.csv file.

        Parameters
        ----------
        file_path : Path

        Returns
        -------
        MatchMetadata
        """

        logger.info("Parsing %s", file_path.name)

        metadata = MatchMetadata()

        metadata.match_id = extract_match_id(file_path)

        teams = []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or row[0] != "info":
                    continue
                if len(row) < 3:
                    continue

                self._process_record(
                    metadata,
                    row,
                    teams,
                )

        if len(teams) >= 2:

            metadata.team1 = teams[0]
            metadata.team2 = teams[1]

        return metadata

    def _process_record(
        self,
        metadata: MatchMetadata,
        row: list[str],
        teams: list[str],
        ) -> None:
        """
        Process a single metadata record from a Cricsheet
        *_info.csv file.
        """

        key = row[1].strip()

        # -------------------------------------------------------
        # Team
        # -------------------------------------------------------
        if key == "team":

            if len(row) >= 3:
                teams.append(row[2])

            return

        # -------------------------------------------------------
        # Event
        # -------------------------------------------------------
        if key == "event":

            if len(row) >= 3:
                metadata.event_name = row[2]

            return

        # -------------------------------------------------------
        # Stage
        # -------------------------------------------------------
        if key == "stage":

            if len(row) >= 3:
                metadata.stage = row[2]

            return
        
        # -------------------------------------------------------
        # Match Number
        # -------------------------------------------------------
        if key == "match_number":

            metadata.match_number = row[2]
            return





        # -------------------------------------------------------
        # Method (D/L etc.)
        # -------------------------------------------------------
        if key == "method":

            metadata.method = row[2]
            return


        # -------------------------------------------------------
        # Target Runs
        # info,target_runs,2,208
        # -------------------------------------------------------
        if key == "target_runs":

            if len(row) >= 4:
                metadata.target_runs = row[3]

            return


        # -------------------------------------------------------
        # Target Overs
        # info,target_overs,2,20
        # -------------------------------------------------------
        if key == "target_overs":

            if len(row) >= 4:
                metadata.target_overs = row[3]

            return

        # -------------------------------------------------------
        # Standard Fields
        # -------------------------------------------------------
        if key in self.FIELD_MAPPING:

            attribute = self.FIELD_MAPPING[key]

            if len(row) >= 3:
                setattr(
                    metadata,
                    attribute,
                    row[2],
                )