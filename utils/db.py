import sqlite3

DB_FILE = "candidates.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            match_score REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_candidate(name, email, score, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO candidates (name, email, match_score, status) VALUES (?, ?, ?, ?)",
              (name, email, score, status))
    conn.commit()
    conn.close()
