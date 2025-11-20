import sqlite3
import os

DB_PATH = 'obd2py.db'

class DatabaseHandler:
    def __init__(self):
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row # Access columns by name
            print(f"✅ Connesso al database SQLite: {DB_PATH}")
        except sqlite3.Error as e:
            print(f"❌ Errore di connessione al database: {e}")
            self.conn = None

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("🔌 Connessione al database chiusa.")

    def create_tables(self):
        """Creates necessary tables if they don't exist."""
        if not self.conn:
            print("⚠️ Impossibile creare tabelle: nessuna connessione al database.")
            return

        try:
            cursor = self.conn.cursor()
            
            # Table for storing categories of data (e.g., 'motore', 'gyroscope')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Categories (
                    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL UNIQUE
                )
            """)
            
            # Table for storing time-series data from any category
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS OBDData (
                    DataID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CategoryID INTEGER NOT NULL,
                    Value TEXT NOT NULL,
                    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (CategoryID) REFERENCES Categories (CategoryID)
                )
            """)

            # Table for storing Diagnostic Trouble Codes (DTCs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dtc_codes (
                    DTCID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Code TEXT NOT NULL,
                    Description TEXT,
                    Status TEXT
                )
            """)

            self.conn.commit()
            print("✅ Tabelle del database verificate/create con successo.")
        except sqlite3.Error as e:
            print(f"❌ Errore durante la creazione delle tabelle: {e}")

    def get_or_create_category(self, category_name):
        """Gets the ID of a category, creating it if it doesn't exist."""
        if not self.conn: return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT CategoryID FROM Categories WHERE Name = ?", (category_name,))
            result = cursor.fetchone()
            if result:
                return result['CategoryID']
            else:
                cursor.execute("INSERT INTO Categories (Name) VALUES (?)", (category_name,))
                self.conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Errore in get_or_create_category: {e}")
            return None

    def insert_data(self, category_name, value):
        """Inserts a data point for a specific category."""
        if not self.conn: return
        category_id = self.get_or_create_category(category_name)
        if category_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO OBDData (CategoryID, Value) VALUES (?, ?)", (category_id, str(value)))
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"❌ Errore durante l'inserimento dei dati: {e}")

    def insert_dtc(self, code, description, status):
        """Inserts a Diagnostic Trouble Code (DTC) into the database."""
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO dtc_codes (Code, Description, Status) VALUES (?, ?, ?)", (code, description, status))
            self.conn.commit()
            print(f"✅ DTC Inserito: {code}")
        except sqlite3.Error as e:
            print(f"❌ Errore durante l'inserimento del DTC: {e}")

# Example usage:
if __name__ == '__main__':
    import json
    db = DatabaseHandler()
    
    # Example of inserting engine data (as a JSON string)
    engine_data = {"rpm": 2500, "speed": 100, "throttle_pos": 45.5}
    db.insert_data('motore_prestazioni', json.dumps(engine_data))

    # Example of inserting gyroscope data
    gyro_data = {"pitch": 1.2, "roll": -0.5}
    db.insert_data('gyroscope', json.dumps(gyro_data))

    # Example of inserting a DTC
    db.insert_dtc('P0420', 'Catalyst System Efficiency Below Threshold (Bank 1)', 'pending')

    db.close()