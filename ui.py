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


def get_execution_history(run_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT step, line_number, variable_name, value, event_type
        FROM execution_states
        WHERE run_id = ?
        ORDER BY step
    """, (run_id,))

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_state_at_step(run_id, step_number):

    rows = get_execution_history(run_id)

    state = {}

    for step, line_number, variable_name, value, event_type in rows:

        if step <= step_number and event_type == "change":
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
        height: 10;
        border: solid yellow;
        padding: 1;
    }
    """

    BINDINGS = [
        ("left", "previous_step", "Previous"),
        ("right", "next_step", "Next"),
        ("q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:

        run = get_latest_run()

        if run is None:

            self.run_id = None
            self.file_path = None
            self.current_step = 0

        else:

            self.run_id = run[0]
            self.file_path = run[1]

            history = get_execution_history(self.run_id)

            if history:
                self.current_step = history[-1][0]
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

        self.update_code()

        self.update_display()

    def update_code(self):

        lines = read_source_code(self.file_path)

        history = get_execution_history(self.run_id)

        current_line = None

        for step, line_number, variable_name, value, event_type in history:

            if step == self.current_step:

                current_line = line_number

                break

        code_text = ""

        for number, line in enumerate(lines, start=1):

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

    def update_display(self):

        history = get_execution_history(
            self.run_id
        )

        if not history:
            return

        state = get_state_at_step(
            self.run_id,
            self.current_step
        )

        variables_text = (
            f"Current Step: {self.current_step}\n\n"
        )

        for variable, value in state.items():

            variables_text += (
                f"{variable} = {value}\n"
            )

        self.query_one(
            "#variable_state",
            Static
        ).update(variables_text)

        timeline = "TIMELINE\n\n"

        for (
            step,
            line_number,
            variable_name,
            value,
            event_type
        ) in history:

            if event_type == "change":

                event_text = (
                    f"{variable_name} = {value}"
                )

            else:

                event_text = "execution"

            if step == self.current_step:

                timeline += (
                    f"▶ [{step}: {event_text}]"
                )

            else:

                timeline += (
                    f"{step}: {event_text}"
                )

            if step != history[-1][0]:

                timeline += " ─── "

        self.query_one(
            "#timeline",
            Static
        ).update(timeline)

        self.update_code()

    def action_previous_step(self):

        if self.current_step > 1:

            self.current_step -= 1

            self.update_display()

    def action_next_step(self):

        history = get_execution_history(
            self.run_id
        )

        if not history:
            return

        if self.current_step < history[-1][0]:

            self.current_step += 1

            self.update_display()

    def action_quit_app(self):

        self.exit()


if __name__ == "__main__":

    PyChronicleApp().run()