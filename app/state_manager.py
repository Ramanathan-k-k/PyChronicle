import sqlite3


def get_state_at_step(step_number):

    connection = sqlite3.connect("data/pychronicle.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT variable_name, value
        FROM execution_states
        WHERE step <= ?
        ORDER BY step
    """, (step_number,))

    rows = cursor.fetchall()

    connection.close()

    state = {}

    for variable_name, value in rows:
        state[variable_name] = value

    return state