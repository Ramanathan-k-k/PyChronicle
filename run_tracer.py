import sys

from app.tracer import trace_function, close_database, set_target_file


file_path = "examples/sample.py"

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