import sqlite3

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static


DATABASE_PATH = "data/pychronicle.db"


def get_latest_run():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT run_id, file_path
        FROM runs
        ORDER BY run_id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    connection.close()

    return result


def get_execution_events(run_id):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT step, line_number
        FROM execution_events
        WHERE run_id = ?
        ORDER BY step
    """, (run_id,))

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_variable_changes(run_id):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT step, variable_name, value
        FROM variable_changes
        WHERE run_id = ?
        ORDER BY step
    """, (run_id,))

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_state_at_step(run_id, step_number):

    changes = get_variable_changes(run_id)

    state = {}

    for step, variable_name, value in changes:

        if step <= step_number:
            state[variable_name] = value

    return state


def read_source_code(file_path):

    with open(file_path, "r") as file:
        return file.readlines()


class PyChronicleApp(App):

    CSS = """
    Screen {
        layout: vertical;
    }

    #main {
        height: 1fr;
    }

    #code {
        width: 60%;
        border: solid green;
        padding: 1;
    }

    #variables {
        width: 40%;
        border: solid cyan;
        padding: 1;
    }

    #timeline {
        height: 12;
        border: solid yellow;
        padding: 1;
    }
    """

    BINDINGS = [
        ("left", "previous_step", "Previous"),
        ("right", "next_step", "Next"),
        ("w", "toggle_watch", "Watch"),
        ("q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:

        run = get_latest_run()

        self.watch_enabled = False
        self.watched_variable = "result"

        if run is None:

            self.run_id = None
            self.file_path = None
            self.current_step = 0

        else:

            self.run_id = run[0]
            self.file_path = run[1]

            events = get_execution_events(
                self.run_id
            )

            if events:
                self.current_step = events[-1][0]
            else:
                self.current_step = 0

        yield Header(show_clock=True)

        with Horizontal(id="main"):

            with Vertical(id="code"):

                yield Static("CODE VIEW")

                yield Static(
                    "",
                    id="code_content"
                )

            with Vertical(id="variables"):

                yield Static("VARIABLES")

                yield Static(
                    "",
                    id="variable_state"
                )

        yield Static(
            "",
            id="timeline"
        )

        yield Footer()

    def on_mount(self):

        if self.run_id is None:
            return

        self.update_display()

    def update_code(self):

        lines = read_source_code(
            self.file_path
        )

        events = get_execution_events(
            self.run_id
        )

        current_line = None

        for step, line_number in events:

            if step == self.current_step:

                current_line = line_number
                break

        code_text = ""

        for number, line in enumerate(
            lines,
            start=1
        ):

            if number == current_line:

                code_text += (
                    f"▶ {number:>2}  {line}"
                )

            else:

                code_text += (
                    f"  {number:>2}  {line}"
                )

        self.query_one(
            "#code_content",
            Static
        ).update(code_text)

    def update_variables(self):

        state = get_state_at_step(
            self.run_id,
            self.current_step
        )

        if self.watch_enabled:

            variables_text = (
                "WATCHED VARIABLE\n\n"
                f"{self.watched_variable} = "
                f"{state.get(self.watched_variable, 'Not defined')}"
            )

        else:

            variables_text = (
                f"Current Step: "
                f"{self.current_step}\n\n"
            )

            if state:

                for variable, value in state.items():

                    variables_text += (
                        f"{variable} = {value}\n"
                    )

            else:

                variables_text += "No variables yet."

        self.query_one(
            "#variable_state",
            Static
        ).update(variables_text)

    def update_timeline(self):

        events = get_execution_events(
            self.run_id
        )

        source_lines = read_source_code(
            self.file_path
        )

        changes = get_variable_changes(
            self.run_id
        )

        changes_by_step = {}

        for step, variable, value in changes:

            if step not in changes_by_step:
                changes_by_step[step] = []

            changes_by_step[step].append(
                (variable, value)
            )

        timeline_text = "TIMELINE\n\n"

        for step, line_number in events:

            if 1 <= line_number <= len(source_lines):

                source_line = (
                    source_lines[
                        line_number - 1
                    ].strip()
                )

            else:

                source_line = "unknown"

            if step in changes_by_step:

                for variable, value in (
                    changes_by_step[step]
                ):

                    event_text = (
                        f"Line {line_number}: "
                        f"{source_line} → "
                        f"{variable} = {value}"
                    )

                    if step == self.current_step:
                        timeline_text += (
                            f"▶ [{step}] "
                            f"{event_text}\n"
                        )
                    else:
                        timeline_text += (
                            f"  {step}  "
                            f"{event_text}\n"
                        )

            else:

                event_text = (
                    f"Line {line_number}: "
                    f"{source_line}"
                )

                if step == self.current_step:
                    timeline_text += (
                        f"▶ [{step}] "
                        f"{event_text}\n"
                    )
                else:
                    timeline_text += (
                        f"  {step}  "
                        f"{event_text}\n"
                    )

        self.query_one(
            "#timeline",
            Static
        ).update(timeline_text)

    def update_display(self):

        events = get_execution_events(
            self.run_id
        )

        if not events:
            return

        self.update_variables()
        self.update_timeline()
        self.update_code()

    def action_previous_step(self):

        if self.current_step > 1:

            self.current_step -= 1
            self.update_display()

    def action_next_step(self):

        events = get_execution_events(
            self.run_id
        )

        if not events:
            return

        last_step = events[-1][0]

        if self.current_step < last_step:

            self.current_step += 1
            self.update_display()

    def action_toggle_watch(self):

        self.watch_enabled = not self.watch_enabled

        self.update_display()

    def action_quit_app(self):

        self.exit()


if __name__ == "__main__":

    PyChronicleApp().run()