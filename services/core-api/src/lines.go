package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	"github.com/jackc/pgx/v5"
)

type Line struct {
	HomeTeam string  `json:"home_team"`
	AwayTeam string  `json:"away_team"`
	Line     float32 `json:"line"`
	Favorite string  `json:"favorite"`
	Neutral  bool    `json:"neutral"`
	GameID   string  `json:"game_id"`
}

func GetLinesHandler(w http.ResponseWriter, r *http.Request) {

	query := `SELECT game_id, home_team, away_team, line_value, favorite, neutral FROM lines;`

	// Execute SQL query to retrieve all lines in the database
	rows, err := db.Query(context.Background(), query)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	lines := []Line{}
	for rows.Next() {
		var line Line
		if err := rows.Scan(&line.GameID, &line.HomeTeam, &line.AwayTeam, &line.Line, &line.Favorite, &line.Neutral); err != nil {
			http.Error(w, "Failed to scan row", http.StatusInternalServerError)
			return
		}
		lines = append(lines, line)
	}

	if err := json.NewEncoder(w).Encode(lines); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
	}

}

func PostLinesHandler(w http.ResponseWriter, r *http.Request) {

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	lines := []Line{}
	if err := json.Unmarshal(body, &lines); err != nil {
		http.Error(w, "Invalid JSON format", http.StatusBadRequest)
		return
	}

	// Prepare batch insert query using pgx
	query := `
		INSERT INTO lines (game_id, home_team, away_team, line_value, favorite, neutral)
		VALUES ($1, $2, $3, $4, $5, $6)
		ON CONFLICT (game_id) DO UPDATE
		SET game_id = EXCLUDED.game_id, home_team = EXCLUDED.home_team, away_team = EXCLUDED.away_team, line_value = EXCLUDED.line_value, favorite = EXCLUDED.favorite, neutral = EXCLUDED.neutral;
	`

	batch := &pgx.Batch{}

	for _, line := range lines {
		batch.Queue(query, line.GameID, line.HomeTeam, line.AwayTeam, line.Line, line.Favorite, line.Neutral)
	}

	br := db.SendBatch(context.Background(), batch)
	defer br.Close()

	for range lines {
		_, err := br.Exec()
		if err != nil {
			http.Error(w, "Failed to insert data", http.StatusInternalServerError)
			log.Printf("Database error: %v", err)
			return
		}
	}

	// Respond with success message
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf(`{"message": "%d lines inserted successfully"}`, len(lines))))
}
