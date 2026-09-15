import sqlite3

# 1. Create / open the database
connection = sqlite3.connect("data/pychronicle.db")

# 2. Create a cursor
cursor = connection.cursor()

# 3. Create the execution_states table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        step INTEGER,
        line_number INTEGER,
        variable_name TEXT,
        value TEXT
    )
""")

# 4. Delete our previous test data
cursor.execute("DELETE FROM execution_states")

# 5. Sample execution states
states = [
    (1, 1, "x", "10"),
    (2, 2, "y", "20"),
    (3, 3, "z", "30"),
    (4, 5, "x", "50")
]

# 6. Insert all states into the database
cursor.executemany("""
    INSERT INTO execution_states
    (step, line_number, variable_name, value)
    VALUES (?, ?, ?, ?)
""", states)

# 7. Save the changes
connection.commit()

print("Data inserted successfully!")

# 8. Read the data from the database
cursor.execute("SELECT * FROM execution_states")

rows = cursor.fetchall()

# 9. Display the data
for row in rows:
    print(row)

# 10. Close the database connection
connection.close()