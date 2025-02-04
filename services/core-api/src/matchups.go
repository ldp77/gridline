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

type Matchup struct {
	HomeTeam string `json:"home_team"`
	AwayTeam string `json:"away_team"`
	Neutral  bool   `json:"neutral"`
}

func GetMatchupsHandler(w http.ResponseWriter, r *http.Request) {
	query := `SELECT home_team, away_team, neutral FROM matchups`

	// Execute SQL query to retrieve all lines in the database
	rows, err := db.Query(context.Background(), query)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	matchups := []Matchup{}
	for rows.Next() {
		var matchup Matchup
		if err := rows.Scan(&matchup.HomeTeam, &matchup.AwayTeam, &matchup.Neutral); err != nil {
			http.Error(w, "Failed to scan row", http.StatusInternalServerError)
			return
		}
		matchups = append(matchups, matchup)
	}

	if err := json.NewEncoder(w).Encode(matchups); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
	}
}

func PostMatchupsHandler(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	matchups := []Matchup{}
	if err := json.Unmarshal(body, &matchups); err != nil {
		http.Error(w, "Invalid JSON format", http.StatusBadRequest)
		return
	}

	// Prepare batch insert query using pgx
	query := `
		INSERT INTO matchups (home_team, away_team, neutral)
		VALUES ($1, $2, $3);
	`

	batch := &pgx.Batch{}

	for _, matchup := range matchups {
		batch.Queue(query, matchup.HomeTeam, matchup.AwayTeam, matchup.Neutral)
	}

	br := db.SendBatch(context.Background(), batch)
	defer br.Close()

	for range matchups {
		_, err := br.Exec()
		if err != nil {
			http.Error(w, "Failed to insert data", http.StatusInternalServerError)
			log.Printf("Database error: %v", err)
			return
		}
	}

	// Respond with success message
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf(`{"message": "%d matchups inserted successfully"}`, len(matchups))))
}
