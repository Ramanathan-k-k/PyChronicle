import sys

from app.state_manager import get_state_at_step


step_number = int(sys.argv[1])

state = get_state_at_step(step_number)


print(f"State at Step {step_number}:\n")

for variable, value in state.items():
    print(f"{variable} = {value}")
    