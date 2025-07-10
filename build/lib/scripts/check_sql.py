import os
import re
import sys

class SQLChecker:
    def __init__(self, directory):
        self.directory = directory
        self.sql_pattern = re.compile(
            r'''(?i)
                        (
                            (
                                self\.env(\.cr)?              # capture self.env or self.env.cr
                                | self\.pool\.cursor\(\)       # capture self.pool.cursor()
                            )
                            \.(execute|sql)\s*                      # method execute with optional spaces
                            \(.*?(["']{1,3})                        # any argument within the parentheses
                            \s*(INSERT|DELETE)\b        # match SQL commands INSERT, DELETE, UPDATE
                        )
                    ''', re.VERBOSE
        )

    def _process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for idx, line in enumerate(lines, start=1):
            if self.sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip()))

    def run(self):
        self.violations = []

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        if self.violations:
            print("[ERROR] Forbidden raw SQL (INSERT/DELETE/UPDATE) usage detected:\n")
            for path, line, content in self.violations:
                print(f" - {path}:{line} -> {content}")
            sys.exit(1)
        else:
            print("[OK] No raw SQL INSERT/DELETE/UPDATE usage found.")
            sys.exit(0)

def main():
    checker = SQLChecker(directory=os.getcwd())
    checker.run()

if __name__ == '__main__':
    SystemExit(main())
