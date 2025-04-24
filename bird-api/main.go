package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

    _ "modernc.org/sqlite"
)
   
// DataItem represents the structure of the data we expect in the POST request.
// The `json:"..."` tags specify how JSON keys map to struct fields.
type DataItem struct {
	ID    int64  `json:"id,omitempty"` // Optional ID, usually set by DB
	Name  string `json:"name"`
	Value int    `json:"value"`
	Notes string `json:"notes,omitempty"` // Optional field
}

// db is our global database connection pool.
var db *sql.DB

const dbFileName = "./data.db" // Name of the SQLite database file

func main() {
	var err error
	// --- Database Setup ---
	log.Println("Setting up database...")
	db, err = setupDatabase(dbFileName)
	if err != nil {
		log.Fatalf("Failed to set up database: %v", err)
	}
	// Ensure the database connection is closed when the application exits
	defer func() {
		if err := db.Close(); err != nil {
			log.Printf("Error closing database: %v", err)
		} else {
			log.Println("Database connection closed.")
		}
	}()

	log.Println("Database setup complete.")

	// --- HTTP Server Setup ---
	// Register the handler function for the /data endpoint
	http.HandleFunc("/data", dataHandler)

	// Define the port the server will listen on
	port := ":8080"
	log.Printf("Starting server on port %s\n", port)

	// Start the HTTP server
	// log.Fatal will log the error and exit if the server fails to start
	log.Fatal(http.ListenAndServe(port, nil))
}

// setupDatabase initializes the SQLite database connection and creates the table if it doesn't exist.
func setupDatabase(dbName string) (*sql.DB, error) {
	// Check if the database file already exists. We only initialize the table if it's new.
	_, err := os.Stat(dbName)
	isNewDB := os.IsNotExist(err)

	// Open the database file. It will be created if it doesn't exist.
	database, err := sql.Open("sqlite", dbName)
	if err != nil {
		return nil, fmt.Errorf("failed to open database %s: %w", dbName, err)
	}

	// Ping the database to verify the connection
	if err = database.Ping(); err != nil {
		database.Close() // Close if ping fails
		return nil, fmt.Errorf("failed to ping database %s: %w", dbName, err)
	}

	log.Printf("Connected to database: %s", dbName)

	// If it's a new database file, create the necessary table
	if isNewDB {
		log.Println("Database file not found, creating table 'items'...")
		createTableSQL := `
		CREATE TABLE items (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			value INTEGER,
			notes TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`

		_, err = database.Exec(createTableSQL)
		if err != nil {
			database.Close() // Close if table creation fails
			return nil, fmt.Errorf("failed to execute table creation statement: %w", err)
		}
		log.Println("Table 'items' created successfully.")
	} else {
		log.Println("Using existing database file.")
	}

	return database, nil
}

// dataHandler handles incoming requests to the /data endpoint.
func dataHandler(w http.ResponseWriter, r *http.Request) {
	// --- Check Request Method ---
	// Only allow POST requests
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		log.Printf("Received non-POST request: %s from %s", r.Method, r.RemoteAddr)
		return
	}

	// --- Decode JSON Body ---
	var newItem DataItem
	decoder := json.NewDecoder(r.Body)
	// Ensure the request body is closed when the function returns
	defer r.Body.Close()

	err := decoder.Decode(&newItem)
	if err != nil {
		http.Error(w, "Bad Request: Invalid JSON format", http.StatusBadRequest)
		log.Printf("Failed to decode JSON from %s: %v", r.RemoteAddr, err)
		return
	}

	// --- (Optional) Basic Validation ---
	if newItem.Name == "" {
		http.Error(w, "Bad Request: 'name' field is required", http.StatusBadRequest)
		log.Printf("Validation failed for request from %s: missing 'name'", r.RemoteAddr)
		return
	}

	// --- Insert Data into Database ---
	log.Printf("Received data to insert: %+v", newItem)

	insertSQL := `INSERT INTO items(name, value, notes) VALUES(?, ?, ?)`
	// Use placeholders (?) to prevent SQL injection vulnerabilities
	result, err := db.Exec(insertSQL, newItem.Name, newItem.Value, newItem.Notes)
	if err != nil {
		// Log the detailed error server-side
		log.Printf("Error inserting data into database: %v", err)
		// Send a generic server error message to the client
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	// Get the ID of the newly inserted row
	id, err := result.LastInsertId()
	if err != nil {
		// This might happen with some drivers/DBs or if the table doesn't have auto-increment
		log.Printf("Warning: Could not get last insert ID: %v", err)
		// Proceed without the ID, as the insertion itself was successful
	} else {
		newItem.ID = id // Add the generated ID to the response object
		log.Printf("Data inserted successfully with ID: %d", id)
	}


	// --- Send Success Response ---
	// Set the Content-Type header to application/json
	w.Header().Set("Content-Type", "application/json")
	// Set the HTTP status code to 201 Created
	w.WriteHeader(http.StatusCreated)

	// Encode the newly created item (including its ID) back to the client as JSON
	responseEncoder := json.NewEncoder(w)
	if err := responseEncoder.Encode(newItem); err != nil {
		// If encoding the response fails, log it but the client likely already got the 201 status
		log.Printf("Error encoding success response: %v", err)
	}
}