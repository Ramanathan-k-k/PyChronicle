import sqlite3

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static


def get_execution_history():

    connection = sqlite3.connect("data/pychronicle.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT step, line_number, variable_name, value, event_type
        FROM execution_states
        ORDER BY step
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_state_at_step(step_number):

    rows = get_execution_history()

    state = {}

    for step, line_number, variable_name, value, event_type in rows:

        if step <= step_number and event_type == "change":
            state[variable_name] = value

    return state


def read_source_code():

    with open("examples/loop.py", "r") as file:
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
        height: 8;
        border: solid yellow;
        padding: 1;
    }
    """

    BINDINGS = [
        ("left", "previous_step", "Previous"),
        ("right", "next_step", "Next"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:

        history = get_execution_history()

        self.current_step = history[-1][0]

        yield Header(show_clock=True)

        with Horizontal(id="main"):

            with Vertical(id="code"):
                yield Static("CODE VIEW")
                yield Static("", id="code_content")

            with Vertical(id="variables"):
                yield Static("VARIABLES")
                yield Static("", id="variable_state")

        yield Static("", id="timeline")

        yield Footer()

    def on_mount(self):

        self.update_code()
        self.update_display()

    def update_code(self):

        lines = read_source_code()

        history = get_execution_history()

        current_line = None

        # Find the actual line executed at the current step
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

        self.query_one("#code_content", Static).update(
            code_text
        )

    def update_display(self):

        history = get_execution_history()

        if not history:
            return

        state = get_state_at_step(self.current_step)

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

        timeline = ""

        for step, _, _, _, _ in history:

            if step == self.current_step:

                timeline += f"[{step}]"

            else:

                timeline += str(step)

            if step != history[-1][0]:

                timeline += " ─── "

        self.query_one(
            "#timeline",
            Static
        ).update(
            "TIMELINE\n\n" + timeline
        )

        # Update highlighted code line
        self.update_code()

    def action_previous_step(self):

        if self.current_step > 1:

            self.current_step -= 1

            self.update_display()

    def action_next_step(self):

        history = get_execution_history()

        if self.current_step < history[-1][0]:

            self.current_step += 1

            self.update_display()


if __name__ == "__main__":

    PyChronicleApp().run()