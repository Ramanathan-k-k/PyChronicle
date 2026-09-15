import sqlite3
from datetime import datetime


DATABASE_PATH = "data/pychronicle.db"

target_file = None
run_id = None

previous_variables = {}
previous_line = None
step = 0

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


def set_target_file(file_path):

    global target_file
    global run_id
    global previous_variables
    global previous_line
    global step

    target_file = file_path
    previous_variables = {}
    previous_line = None
    step = 0

    cursor.execute("""
        INSERT INTO runs (file_path, started_at)
        VALUES (?, ?)
    """, (
        file_path,
        datetime.now().isoformat()
    ))

    run_id = cursor.lastrowid

    connection.commit()


def save_event(line_number, changes):

    global step

    step += 1

    if changes:

        for name, value in changes:

            print(
                f"CHANGE → Step {step} → "
                f"Line {line_number} → "
                f"{name} = {value}"
            )

            cursor.execute("""
                INSERT INTO execution_states
                (run_id, step, line_number,
                 variable_name, value, event_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                step,
                line_number,
                name,
                str(value),
                "change"
            ))

    else:

        print(
            f"EXECUTE → Step {step} → "
            f"Line {line_number}"
        )

        cursor.execute("""
            INSERT INTO execution_states
            (run_id, step, line_number,
             variable_name, value, event_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            step,
            line_number,
            None,
            None,
            "execute"
        ))

    connection.commit()


def trace_function(frame, event, arg):

    global previous_variables
    global previous_line

    if frame.f_code.co_filename != target_file:
        return trace_function

    if event == "line":

        current_line = frame.f_lineno

        current_variables = {
            name: value
            for name, value in frame.f_locals.items()
            if name != "__builtins__"
        }

        changes = []

        for name, value in current_variables.items():

            if (
                name not in previous_variables
                or previous_variables[name] != value
            ):
                changes.append((name, value))

        # The changes seen now were caused by the previous line.
        if previous_line is not None:
            save_event(previous_line, changes)

        previous_variables = current_variables.copy()
        previous_line = current_line

    elif event == "return":

        # Flush the final executed line.
        if previous_line is not None:
            save_event(previous_line, [])

        previous_line = None

    return trace_function


def close_database():
    connection.close()