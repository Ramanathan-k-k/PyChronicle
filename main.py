from app.ast_parser import get_assignments
import sqlite3


# 1. Get assignments from AST
assignments = get_assignments("examples/sample.py")

print("AST Data:")
print(assignments)


# 2. Connect to SQLite
connection = sqlite3.connect("data/pychronicle.db")

cursor = connection.cursor()


# 3. Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        step INTEGER,
        line_number INTEGER,
        variable_name TEXT,
        value TEXT
    )
""")


# 4. Remove old test data
cursor.execute("DELETE FROM execution_states")


# 5. Convert AST data into database data
states = []

for step, (line_number, variable, value) in enumerate(assignments, start=1):
    states.append(
        (step, line_number, variable, value)
    )


# 6. Insert into SQLite
cursor.executemany("""
    INSERT INTO execution_states
    (step, line_number, variable_name, value)
    VALUES (?, ?, ?, ?)
""", states)


# 7. Save
connection.commit()


print("AST data inserted into SQLite!")


# 8. Read database
cursor.execute("SELECT * FROM execution_states")

rows = cursor.fetchall()


# 9. Display database contents
print("\nDatabase Data:")

for row in rows:
    print(row)


# 10. Close database
connection.close()