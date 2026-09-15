import sqlite3


DATABASE_PATH = "data/pychronicle.db"


connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


# Get the latest run
cursor.execute("""
    SELECT run_id, file_path
    FROM runs
    ORDER BY run_id DESC
    LIMIT 1
""")

run = cursor.fetchone()

if run is None:

    print("No runs found.")

    connection.close()

    exit()


run_id, file_path = run

print("Execution History:")
print()
print(f"Run ID: {run_id}")
print(f"File: {file_path}")
print()


# Get execution events
cursor.execute("""
    SELECT step, line_number
    FROM execution_events
    WHERE run_id = ?
    ORDER BY step
""", (run_id,))

events = cursor.fetchall()


# Get variable changes
cursor.execute("""
    SELECT step, variable_name, value
    FROM variable_changes
    WHERE run_id = ?
    ORDER BY step
""", (run_id,))

changes = cursor.fetchall()


# Convert changes into a dictionary
changes_by_step = {}

for step, variable_name, value in changes:

    if step not in changes_by_step:
        changes_by_step[step] = []

    changes_by_step[step].append(
        (variable_name, value)
    )


# Display combined history
for step, line_number in events:

    print(
        f"Step {step} → Line {line_number}"
    )

    if step in changes_by_step:

        for variable_name, value in changes_by_step[step]:

            print(
                f"    {variable_name} = {value}"
            )

    else:

        print("    No variable changes")


connection.close()