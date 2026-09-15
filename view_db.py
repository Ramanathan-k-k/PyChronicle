import sqlite3


connection = sqlite3.connect("data/pychronicle.db")
cursor = connection.cursor()


cursor.execute("""
SELECT step, line_number, variable_name, value
FROM execution_states
ORDER BY step
""")


rows = cursor.fetchall()


print("Execution History:\n")

for row in rows:
    print(row)


connection.close()