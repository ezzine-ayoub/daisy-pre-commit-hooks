import os
import ast
import sys

class FunctionLengthChecker:
    MAX_FUNCTION_LENGTH = 100

    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []

    def check(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=self.file_path)
        except SyntaxError as e:
            self.errors.append(f"Syntax error in {self.file_path}: {e}")
            return

        attach_parents(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_function(node)

    def _check_function(self, node):
        start_line = node.lineno
        end_line = max(
            (child.lineno for child in ast.walk(node) if hasattr(child, 'lineno')),
            default=start_line
        )
        function_length = end_line - start_line + 1
        if function_length > self.MAX_FUNCTION_LENGTH:
            function_type = "Method" if self._is_method(node) else "Function"
            self.errors.append(
                f"{self.file_path}:{start_line} {function_type} '{node.name}' too long ({function_length} lines)"
            )

    def _is_method(self, node):
        parent = getattr(node, 'parent', None)
        while parent:
            if isinstance(parent, ast.ClassDef):
                return True
            parent = getattr(parent, 'parent', None)
        return False

def attach_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

def find_python_files(base_dir):
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        # Ignore .venv directory
        if '.venv' in dirs:
            dirs.remove('.venv')

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    base_dir = os.getcwd()
    file_paths = find_python_files(base_dir)

    exit_code = 0
    for file_path in file_paths:
        checker = FunctionLengthChecker(file_path)
        checker.check()
        if checker.errors:
            for error in checker.errors:
                print(error)
            exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    SystemExit(main())
