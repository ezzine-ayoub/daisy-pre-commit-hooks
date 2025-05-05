import ast
import os
import sys


class ComputeFieldChecker:
    def __init__(self, root_path):
        self.root_path = root_path
        self.errors = []

    def get_all_python_files(self):
        python_files = []
        for dirpath, _, filenames in os.walk(self.root_path):
            for filename in filenames:
                if filename.endswith(".py"):
                    python_files.append(os.path.join(dirpath, filename))
        return python_files

    def check_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read(), filename=file_path)
        except SyntaxError as e:
            self.errors.append(f"[SyntaxError] {file_path}: {e}")
            return

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_methods = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for elt in stmt.targets:
                            if isinstance(elt, ast.Name):
                                if isinstance(stmt.value, ast.Call) and hasattr(stmt.value.func, 'attr'):
                                    kwargs = {kw.arg: kw.value for kw in stmt.value.keywords}
                                    if 'compute' in kwargs:
                                        compute_node = kwargs['compute']
                                        compute_func = None
                                        if isinstance(compute_node, ast.Str):
                                            compute_func = compute_node.s
                                        elif isinstance(compute_node, ast.Constant):
                                            compute_func = compute_node.value

                                        if compute_func and compute_func not in class_methods:
                                            clickable_path = f"file:///{file_path.replace(os.sep, '/')}"
                                            self.errors.append(
                                                f"[Missing compute] {clickable_path}: méthode '{compute_func}' non définie dans la classe '{node.name}'"
                                            )

    def run(self):
        python_files = self.get_all_python_files()
        for file_path in python_files:
            self.check_file(file_path)

        if self.errors:
            for error in self.errors:
                print(error)
            return 1
        return 0

def main():
    checker = ComputeFieldChecker(os.getcwd())
    sys.exit(checker.run())

if __name__ == "__main__":
    SystemExit(main())
