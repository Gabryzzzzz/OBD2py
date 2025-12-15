import sqlite3
import os

DB_PATH = 'obd2py.db'

class DatabaseHandler:
    def __init__(self):
        self.conn = None
        self.connect()
        self.create_tables()
        self.delete_simulated_data()

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

            # Table for storing performance engine data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS MotorePrestazioniData (
                    DataID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    rpm INTEGER,
                    velocita INTEGER,
                    acceleratore INTEGER,
                    pressione_map INTEGER,
                    flusso_maf INTEGER,
                    simulated BOOLEAN NOT NULL
                )
            """)

            # Table for storing other data like km traveled
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS AltriDatiData (
                    DataID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    km_percorsi REAL,
                    simulated BOOLEAN NOT NULL
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
                # Use datetime('now', '+1 hour') to adjust for the user's timezone (e.g., UTC+1)
                cursor.execute("INSERT INTO OBDData (CategoryID, Value, Timestamp) VALUES (?, ?, datetime('now', '+1 hour'))", (category_id, str(value)))
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"❌ Errore durante l'inserimento dei dati: {e}")

    def insert_motore_prestazioni_data(self, data):
        """Inserts a performance engine data point into the specific table."""
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO MotorePrestazioniData 
                (rpm, velocita, acceleratore, pressione_map, flusso_maf, simulated, Timestamp)
                VALUES (:rpm, :velocita, :acceleratore, :pressione_map, :flusso_maf, :simulated, datetime('now', '+1 hour'))
            """
            # Ensure all keys are present, providing a default if not
            data_to_insert = {
                'rpm': data.get('rpm'),
                'velocita': data.get('velocita'),
                'acceleratore': data.get('acceleratore'),
                'pressione_map': data.get('pressione_map'),
                'flusso_maf': data.get('flusso_maf'),
                'simulated': data.get('simulated', False)
            }
            cursor.execute(query, data_to_insert)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Errore durante l'inserimento dei dati motore: {e}")

    def insert_altri_dati_data(self, data):
        """Inserts other data (like km_percorsi) into the specific table."""
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO AltriDatiData 
                (km_percorsi, simulated, Timestamp)
                VALUES (:km_percorsi, :simulated, datetime('now', '+1 hour'))
            """
            data_to_insert = {
                'km_percorsi': data.get('km_percorsi'),
                'simulated': data.get('simulated', False)
            }
            cursor.execute(query, data_to_insert)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Errore durante l'inserimento degli 'altri dati': {e}")

    def insert_dtc(self, code, description, status):
        """Inserts a Diagnostic Trouble Code (DTC) into the database."""
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            # Use datetime('now', '+1 hour') to adjust for the user's timezone
            cursor.execute("INSERT INTO dtc_codes (Code, Description, Status, Timestamp) VALUES (?, ?, ?, datetime('now', '+1 hour'))", (code, description, status))
            self.conn.commit()
            print(f"✅ DTC Inserito: {code}")
        except sqlite3.Error as e:
            print(f"❌ Errore durante l'inserimento del DTC: {e}")

    def delete_simulated_data(self):
        """Deletes all records from OBDData that were marked as simulated."""
        if not self.conn:
            print("⚠️ Impossibile eliminare dati simulati: nessuna connessione al database.")
            return

        try:
            cursor = self.conn.cursor()
            # The LIKE operator is used for broad compatibility, as it doesn't depend on the SQLite JSON1 extension.
            # It finds any entry where the 'Value' text contains the substring '"simulated": true'.
            cursor.execute("""
                DELETE FROM OBDData 
                WHERE Value LIKE '%"simulated": true%'
            """)
            # Also delete from the new specific table
            cursor.execute("""
                DELETE FROM MotorePrestazioniData
                WHERE simulated = 1
            """)

            # Also delete from the 'altri dati' table
            cursor.execute("""
                DELETE FROM AltriDatiData
                WHERE simulated = 1
            """)
            self.conn.commit()
            print(f"🧹 Dati simulati precedenti eliminati ({cursor.rowcount} record).")
        except sqlite3.Error as e:
            print(f"❌ Errore durante l'eliminazione dei dati simulati: {e}")

    def get_data_by_category_and_range(self, category_name, start_date, end_date):
        """
        Retrieves data for a specific category within a given date range.
        Dates should be in 'YYYY-MM-DD HH:MM:SS' format.
        """
        if not self.conn:
            print("⚠️ Impossibile recuperare dati: nessuna connessione al database.")
            return []
        
        try:
            cursor = self.conn.cursor()
            query = ""

            if category_name == 'motore_prestazioni':
                query = """
                    SELECT Timestamp, rpm, velocita, acceleratore, pressione_map, flusso_maf, simulated
                    FROM MotorePrestazioniData
                    WHERE Timestamp BETWEEN ? AND ?
                    ORDER BY Timestamp ASC
                """
            elif category_name == 'altri_dati':
                query = """
                    SELECT Timestamp, km_percorsi, simulated
                    FROM AltriDatiData
                    WHERE Timestamp BETWEEN ? AND ?
                    ORDER BY Timestamp ASC
                """
            else:
                # Fallback to the generic OBDData table for other categories
                query = """
                    SELECT d.Timestamp, d.Value
                    FROM OBDData d
                    JOIN Categories c ON d.CategoryID = c.CategoryID
                    WHERE c.Name = ? AND d.Timestamp BETWEEN ? AND ?
                    ORDER BY d.Timestamp ASC
                """

            if category_name in ['motore_prestazioni', 'altri_dati']:
                cursor.execute(query, (start_date, end_date))
            else:
                cursor.execute(query, (category_name, start_date, end_date))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"❌ Errore durante il recupero dei dati per intervallo: {e}")
            return []

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