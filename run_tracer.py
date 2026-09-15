import sys

from app.tracer import trace_function, close_database, set_target_file


# Get Python file from terminal
file_path = sys.argv[1]

set_target_file(file_path)


sys.settrace(trace_function)

with open(file_path, "r") as file:
    source_code = file.read()

code = compile(
    source_code,
    file_path,
    "exec"
)

exec(code, {})

sys.settrace(None)

close_database()