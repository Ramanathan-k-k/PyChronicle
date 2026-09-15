import sqlite3


target_file = None

previous_variables = {}
step = 0

def set_target_file(file_path):
    global target_file
    target_file = file_path


connection = sqlite3.connect("data/pychronicle.db")
cursor = connection.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        step INTEGER,
        line_number INTEGER,
        variable_name TEXT,
        value TEXT
    )
""")

# Remove old data
cursor.execute("DELETE FROM execution_states")
connection.commit()


def trace_function(frame, event, arg):

    global previous_variables
    global step

    if frame.f_code.co_filename == target_file:

        if event == "line":

            line_number = frame.f_lineno

            current_variables = {
                name: value
                for name, value in frame.f_locals.items()
                if name != "__builtins__"
            }

            for name, value in current_variables.items():

                if (
                    name not in previous_variables
                    or previous_variables[name] != value
                ):

                    step += 1

                    print(
                        f"CHANGE → Step {step} → "
                        f"Line {line_number} → "
                        f"{name} = {value}"
                    )

                    cursor.execute("""
                        INSERT INTO execution_states
                        (step, line_number, variable_name, value)
                        VALUES (?, ?, ?, ?)
                    """, (
                        step,
                        line_number,
                        name,
                        str(value)
                    ))

                    connection.commit()

            previous_variables = current_variables.copy()

    return trace_function


def close_database():
    connection.close()