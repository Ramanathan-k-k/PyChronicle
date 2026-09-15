import os
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

    target_file = os.path.abspath(file_path)

    # Reset tracer state for a new run
    previous_variables = {}
    previous_line = None
    step = 0

    # Create a new run
    cursor.execute("""
        INSERT INTO runs (file_path, started_at)
        VALUES (?, ?)
    """, (
        file_path,
        datetime.now().isoformat()
    ))

    run_id = cursor.lastrowid

    connection.commit()


def save_execution_event(line_number):

    global step

    step += 1

    cursor.execute("""
        INSERT INTO execution_events
        (run_id, step, line_number)
        VALUES (?, ?, ?)
    """, (
        run_id,
        step,
        line_number
    ))

    return step


def save_variable_change(step_number, name, value):

    cursor.execute("""
        INSERT INTO variable_changes
        (run_id, step, variable_name, value)
        VALUES (?, ?, ?, ?)
    """, (
        run_id,
        step_number,
        name,
        repr(value)
    ))


def trace_function(frame, event, arg):

    global previous_variables
    global previous_line

    if os.path.abspath(frame.f_code.co_filename) != target_file:
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

        # Changes detected here were caused
        # by the previous line.
        if previous_line is not None:

            current_step = save_execution_event(
                previous_line
            )

            for name, value in changes:

                save_variable_change(
                    current_step,
                    name,
                    value
                )

        previous_variables = current_variables.copy()

        previous_line = current_line

        connection.commit()

    elif event == "return":

        # Capture the final state of variables.
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

        # Save the final executed line.
        if previous_line is not None:

            current_step = save_execution_event(
                previous_line
            )

            for name, value in changes:

                save_variable_change(
                    current_step,
                    name,
                    value
                )

            connection.commit()

            previous_line = None

    return trace_function


def close_database():

    connection.close()