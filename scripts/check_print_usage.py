# # scripts/check_print_usage.py
#
# import os
# import sys
# import io
#
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# class PrintChecker:
#     def __init__(self, directory):
#         self.directory = directory
#         self.errors = []
#
#     def _process_file(self, file_path):
#         with open(file_path, 'r', encoding='utf-8') as file:
#             lines = file.readlines()
#             for idx, line in enumerate(lines, start=1):
#                 if 'print(' in line:
#                     self.errors.append((file_path, idx, line.strip()))
#
#     def run(self):
#         for root, dirs, files in os.walk(self.directory):
#             for file in files:
#                 if file.endswith(".py"):
#                     file_path = os.path.join(root, file)
#                     self._process_file(file_path)
#
#         if self.errors:
#             print("\n[ERROR] Usage of print() detected in the following files:\n")
#             for path, line, content in self.errors:
#                 print(f" - {path}:{line} -> {content}")
#             sys.exit(1)
#         else:
#             print("[OK] No usage of print() found.")
#             sys.exit(0)
#
# if __name__ == '__main__':
#     checker = PrintChecker(directory=os.getcwd())
#     checker.run()

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class PrintChecker:
    def __init__(self, directory):
        self.directory = directory
        self.errors = []

    def _process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for idx, line in enumerate(lines, start=1):
                if line.strip().startswith("#"):
                    continue
                if 'print(' in line:
                    self.errors.append((file_path, idx, line.strip()))

    def run(self):

        ignored_dirs = {'.idea', '.venv', 'node_modules', '__pycache__','scripts','odoo18'}

        for root, dirs, files in os.walk(self.directory):

            dirs[:] = [d for d in dirs if d not in ignored_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        if self.errors:
            print("\n[ERROR] Usage of print() detected in the following files:\n")
            for path, line, content in self.errors:
                print(f" - {path}:{line} -> {content}")
            sys.exit(1)
        else:
            print("[OK] No usage of print() found.")
            sys.exit(0)

def main():
    checker = PrintChecker(directory=os.getcwd())
    checker.run()
if __name__ == '__main__':
    SystemExit(main())
