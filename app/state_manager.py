import sqlite3


DATABASE_PATH = "data/pychronicle.db"


def get_latest_run_id():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT run_id
        FROM runs
        ORDER BY run_id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return None


def get_state_at_step(step_number, run_id=None):

    if run_id is None:
        run_id = get_latest_run_id()

    if run_id is None:
        return {}

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT variable_name, value
        FROM variable_changes
        WHERE run_id = ?
        AND step <= ?
        ORDER BY step
    """, (run_id, step_number))

    rows = cursor.fetchall()

    connection.close()

    state = {}

    for variable_name, value in rows:

        state[variable_name] = value

    return state