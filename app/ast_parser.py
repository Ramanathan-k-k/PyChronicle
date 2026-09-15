import ast


def get_assignments(file_path):
    # Read the Python file
    with open(file_path, "r") as file:
        source_code = file.read()

    # Convert Python code into AST
    tree = ast.parse(source_code)

    assignments = []

    # Find assignment statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            variable = node.targets[0].id
            value = ast.unparse(node.value)

            assignments.append(
                (node.lineno, variable, value)
            )

    return assignments