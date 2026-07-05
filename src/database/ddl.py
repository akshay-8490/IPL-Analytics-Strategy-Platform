"""
Database schema DDL definitions.

This module contains the physical SQL schema definitions for the IPL Analytics & Strategy Platform.
It contains static SQL queries and does not execute database operations.
"""

from __future__ import annotations


def get_dim_season_ddl() -> str:
    """
    Build the DDL for the Season dimension.
    """
    return """
    CREATE TABLE IF NOT EXISTS dim_season (
        season_key INT NOT NULL,
        season SMALLINT NOT NULL,
        season_start_date DATE NOT NULL,
        season_end_date DATE NOT NULL,
        total_matches INT NOT NULL,
        PRIMARY KEY (season_key),
        UNIQUE KEY uq_dim_season (season)
    ) ENGINE=InnoDB;
    """


def get_dim_team_ddl() -> str:
    """
    Build the DDL for the Team dimension.
    """
    return """
    CREATE TABLE IF NOT EXISTS dim_team (
        team_key INT NOT NULL,
        team_name VARCHAR(100) NOT NULL,
        team_short_name VARCHAR(10) NOT NULL,
        first_season SMALLINT,
        last_season SMALLINT,
        PRIMARY KEY (team_key),
        UNIQUE KEY uq_dim_team_name (team_name)
    ) ENGINE=InnoDB;
    """


def get_dim_player_ddl() -> str:
    """
    Build the DDL for the Player dimension.
    """
    return """
    CREATE TABLE IF NOT EXISTS dim_player (
        player_key INT NOT NULL,
        player_name VARCHAR(120) NOT NULL,
        first_season SMALLINT,
        last_season SMALLINT,
        PRIMARY KEY (player_key),
        INDEX idx_player_name (player_name)
    ) ENGINE=InnoDB;
    """


def get_dim_venue_ddl() -> str:
    """
    Build the DDL for the Venue dimension.
    """
    return """
    CREATE TABLE IF NOT EXISTS dim_venue (
        venue_key INT NOT NULL,
        venue VARCHAR(200) NOT NULL,
        city VARCHAR(100),
        first_season SMALLINT,
        last_season SMALLINT,
        PRIMARY KEY (venue_key),
        UNIQUE KEY uq_dim_venue (venue)
    ) ENGINE=InnoDB;
    """


def get_dim_match_ddl() -> str:
    """
    Build the DDL for the Match dimension.
    """
    return """
    CREATE TABLE IF NOT EXISTS dim_match (
        match_key INT NOT NULL,
        match_id INT NOT NULL,
        season_key INT NOT NULL,
        match_date DATE NOT NULL,
        venue_key INT NOT NULL,
        team1_key INT NOT NULL,
        team2_key INT NOT NULL,
        toss_winner_key INT,
        toss_decision VARCHAR(20),
        winner_key INT,
        win_type VARCHAR(20),
        win_margin INT,
        match_type VARCHAR(30),
        player_of_match VARCHAR(120),
        outcome VARCHAR(30),
        method VARCHAR(50),
        PRIMARY KEY (match_key),
        UNIQUE KEY uq_match_id (match_id),
        CONSTRAINT fk_match_season
            FOREIGN KEY (season_key)
            REFERENCES dim_season(season_key),
        CONSTRAINT fk_match_venue
            FOREIGN KEY (venue_key)
            REFERENCES dim_venue(venue_key),
        CONSTRAINT fk_match_team1
            FOREIGN KEY (team1_key)
            REFERENCES dim_team(team_key),
        CONSTRAINT fk_match_team2
            FOREIGN KEY (team2_key)
            REFERENCES dim_team(team_key),
        CONSTRAINT fk_match_toss
            FOREIGN KEY (toss_winner_key)
            REFERENCES dim_team(team_key),
        CONSTRAINT fk_match_winner
            FOREIGN KEY (winner_key)
            REFERENCES dim_team(team_key)
    ) ENGINE=InnoDB;
    """


def get_fact_match_ddl() -> str:
    """
    Build the DDL for the Match Fact table.
    """
    return """
    CREATE TABLE IF NOT EXISTS fact_match (
        match_key INT NOT NULL,
        total_runs INT NOT NULL,
        total_wickets INT NOT NULL,
        total_boundaries INT NOT NULL,
        total_fours INT NOT NULL,
        total_sixes INT NOT NULL,
        total_extras INT NOT NULL,
        total_legal_deliveries INT NOT NULL,
        total_overs DECIMAL(4,1) NOT NULL,
        PRIMARY KEY (match_key),
        CONSTRAINT fk_fact_match
            FOREIGN KEY (match_key)
            REFERENCES dim_match(match_key)
    ) ENGINE=InnoDB;
    """


def get_fact_player_match_ddl() -> str:
    """
    Build the DDL for the Player Match fact table.
    """
    return """
    CREATE TABLE IF NOT EXISTS fact_player_match (
        match_key INT NOT NULL,
        player_key INT NOT NULL,
        batting_runs INT NOT NULL,
        balls_faced INT NOT NULL,
        fours INT NOT NULL,
        sixes INT NOT NULL,
        dismissals INT NOT NULL,
        PRIMARY KEY (
            match_key,
            player_key
        ),
        CONSTRAINT fk_fpm_match
            FOREIGN KEY (match_key)
            REFERENCES dim_match(match_key),
        CONSTRAINT fk_fpm_player
            FOREIGN KEY (player_key)
            REFERENCES dim_player(player_key)
    ) ENGINE=InnoDB;
    """


def get_fact_delivery_ddl() -> str:
    """
    Build the DDL for the Delivery Fact table.
    """
    return """
    CREATE TABLE IF NOT EXISTS fact_delivery (
        match_key INT NOT NULL,
        season_key INT NOT NULL,
        batting_team_key INT NOT NULL,
        bowling_team_key INT NOT NULL,
        batter_key INT NOT NULL,
        bowler_key INT NOT NULL,
        non_striker_key INT NOT NULL,
        fielder_key INT NULL,
        player_out_key INT NULL,
        innings TINYINT NOT NULL,
        over_number TINYINT NOT NULL,
        ball_number TINYINT NOT NULL,
        runs_off_bat TINYINT NOT NULL,
        extras TINYINT NOT NULL,
        total_runs TINYINT NOT NULL,
        is_boundary BOOLEAN NOT NULL,
        is_four BOOLEAN NOT NULL,
        is_six BOOLEAN NOT NULL,
        is_dot_ball BOOLEAN NOT NULL,
        is_wicket BOOLEAN NOT NULL,
        is_legal_delivery BOOLEAN NOT NULL,
        extra_type VARCHAR(30),
        PRIMARY KEY (
            match_key,
            innings,
            over_number,
            ball_number
        ),
        CONSTRAINT fk_fd_match
            FOREIGN KEY (match_key)
            REFERENCES dim_match(match_key),
        CONSTRAINT fk_fd_season
            FOREIGN KEY (season_key)
            REFERENCES dim_season(season_key),
        CONSTRAINT fk_fd_batting_team
            FOREIGN KEY (batting_team_key)
            REFERENCES dim_team(team_key),
        CONSTRAINT fk_fd_bowling_team
            FOREIGN KEY (bowling_team_key)
            REFERENCES dim_team(team_key),
        CONSTRAINT fk_fd_batter
            FOREIGN KEY (batter_key)
            REFERENCES dim_player(player_key),
        CONSTRAINT fk_fd_bowler
            FOREIGN KEY (bowler_key)
            REFERENCES dim_player(player_key),
        CONSTRAINT fk_fd_non_striker
            FOREIGN KEY (non_striker_key)
            REFERENCES dim_player(player_key),
        CONSTRAINT fk_fd_fielder
            FOREIGN KEY (fielder_key)
            REFERENCES dim_player(player_key),
        CONSTRAINT fk_fd_player_out
            FOREIGN KEY (player_out_key)
            REFERENCES dim_player(player_key)
    ) ENGINE=InnoDB;
    """


def get_indexes_ddl() -> list[str]:
    """
    Build CREATE INDEX statements for the warehouse.
    """
    return [
        """
        CREATE INDEX idx_dim_match_season
        ON dim_match (season_key);
        """,
        """
        CREATE INDEX idx_dim_match_team1
        ON dim_match (team1_key);
        """,
        """
        CREATE INDEX idx_dim_match_team2
        ON dim_match (team2_key);
        """,
        """
        CREATE INDEX idx_fact_delivery_match
        ON fact_delivery (match_key);
        """,
        """
        CREATE INDEX idx_fact_delivery_batter
        ON fact_delivery (batter_key);
        """,
        """
        CREATE INDEX idx_fact_delivery_bowler
        ON fact_delivery (bowler_key);
        """,
        """
        CREATE INDEX idx_fact_delivery_batting_team
        ON fact_delivery (batting_team_key);
        """,
        """
        CREATE INDEX idx_fact_delivery_bowling_team
        ON fact_delivery (bowling_team_key);
        """,
        """
        CREATE INDEX idx_fact_player_match_player
        ON fact_player_match (player_key);
        """,
    ]
