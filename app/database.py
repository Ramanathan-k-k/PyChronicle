import sqlite3


DATABASE_PATH = "data/pychronicle.db"


def get_connection():

    return sqlite3.connect(DATABASE_PATH)


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            started_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            step INTEGER,
            line_number INTEGER,
            variable_name TEXT,
            value TEXT,
            event_type TEXT
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")