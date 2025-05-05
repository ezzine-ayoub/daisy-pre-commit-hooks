#!/usr/bin/env python3

import os
import ast
import sys

# Force UTF-8 encoding in Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

class OdooModelFileChecker:
    # Define rules based on (has_name, has_inherit)
    RULES = {
        (True, False): ('dc_', "[ERROR] {clickable_path} must start with 'dc_' (has _name without _inherit)."),
        (False, True): ('modify_', "[ERROR] {clickable_path} must start with '_modify' (has _inherit without _name)."),
        (True, True): ('_dc_modify_', "[ERROR] {clickable_path} must start with 'dc_modify_' (has both _name and _inherit)."),
    }

    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.success = True

    def find_python_files(self):
        py_files = []
        for root, _, files in os.walk(self.base_directory):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    def check_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read(), filename=filepath)
            except SyntaxError:
                print(f"[SYNTAX ERROR] in file {filepath}")
                self.success = False
                return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self.is_model_class(node):
                    has_name, has_inherit = self.extract_model_attributes(node)
                    self.check_naming_convention(filepath, has_name, has_inherit)

    def is_model_class(self, class_node):
        return any(
            isinstance(base, ast.Attribute) and base.attr == 'Model'
            for base in class_node.bases
        )

    def extract_model_attributes(self, class_node):
        has_name = False
        has_inherit = False

        for stmt in class_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '_name':
                            has_name = True
                        if target.id == '_inherit':
                            has_inherit = True
        return has_name, has_inherit

    def check_naming_convention(self, filepath, has_name, has_inherit):
        rule = self.RULES.get((has_name, has_inherit))
        if rule:
            expected_prefix, error_message = rule
            filename = os.path.basename(filepath)
            clickable_path = f"file:///{filepath.replace(os.sep, '/')}"
            if not filename.startswith(expected_prefix):
                print(error_message.format(clickable_path=clickable_path))
                self.success = False  # Only set this to False if there's an error

    def run(self):
        python_files = self.find_python_files()
        for filepath in python_files:
            self.check_file(filepath)
        if not self.success:
            sys.exit(1)

def main():
    cwd = os.getcwd()
    checker = OdooModelFileChecker(cwd)
    checker.run()

if __name__ == "__main__":
    SystemExit(main())