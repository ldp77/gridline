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

type FPIRating struct {
	TeamName string  `json:"team_name"`
	FPI      float32 `json:"fpi"`
}

func GetFpisHandler(w http.ResponseWriter, r *http.Request) {
	query := `SELECT team_name, fpi FROM fpi_ratings`

	// Execute SQL query to retrieve all lines in the database
	rows, err := db.Query(context.Background(), query)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	fpis := []FPIRating{}
	for rows.Next() {
		var fpi FPIRating
		if err := rows.Scan(&fpi.TeamName, &fpi.FPI); err != nil {
			http.Error(w, "Failed to scan row", http.StatusInternalServerError)
			return
		}
		fpis = append(fpis, fpi)
	}

	if err := json.NewEncoder(w).Encode(fpis); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
	}
}

func PostFpisHandler(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	fpis := []FPIRating{}
	if err := json.Unmarshal(body, &fpis); err != nil {
		http.Error(w, "Invalid JSON format", http.StatusBadRequest)
		return
	}

	// Prepare batch insert query using pgx
	query := `
		INSERT INTO fpi_ratings (team_name, fpi)
		VALUES ($1, $2)
		ON CONFLICT (team_name) DO UPDATE
		SET team_name = EXCLUDED.team_name, fpi = EXCLUDED.fpi;
	`

	batch := &pgx.Batch{}

	for _, fpi := range fpis {
		batch.Queue(query, fpi.TeamName, fpi.FPI)
	}

	br := db.SendBatch(context.Background(), batch)
	defer br.Close()

	for range fpis {
		_, err := br.Exec()
		if err != nil {
			http.Error(w, "Failed to insert data", http.StatusInternalServerError)
			log.Printf("Database error: %v", err)
			return
		}
	}

	// Respond with success message
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(fmt.Sprintf(`{"message": "%d fpi ratings inserted successfully"}`, len(fpis))))
}
