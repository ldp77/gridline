package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)

func helloWorld(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "{'message': 'Hello world'}")
}

func linesHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		PostLinesHandler(w, r)
	case http.MethodGet:
		GetLinesHandler(w, r)
	}
}

var db *pgxpool.Pool

func main() {

	// Load database connection
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		log.Fatal("DATABASE_URL environment variable not set")
	}
	log.Printf("Fetched DATABASE_URL: %s", databaseURL)

	var err error
	db, err = pgxpool.New(context.Background(), databaseURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
	}
	defer db.Close()

	http.HandleFunc("/", helloWorld)
	log.Print("Starting server on :8080")

	http.HandleFunc("/lines", linesHandler)

	http.ListenAndServe(":8080", nil)
}
