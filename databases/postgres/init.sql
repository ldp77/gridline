CREATE TABLE IF NOT EXISTS lines (
    game_id   VARCHAR(100) PRIMARY KEY,
    home_team VARCHAR(100),
	away_team VARCHAR(100),
	line_value      DECIMAL(3,1),
	favorite  VARCHAR(100),
	neutral   BOOLEAN NOT NULL DEFAULT FALSE
);