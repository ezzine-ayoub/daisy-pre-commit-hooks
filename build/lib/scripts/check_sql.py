import os
import re
import sys

class SQLChecker:
    def __init__(self, directory):
        self.directory = directory

        # self.env.cr / self.pool.cursor with SQL
        self.odoo_sql_pattern = re.compile(
            r'''(?i)
                (
                    (
                        self\.env(\.cr)?              # self.env or self.env.cr
                        | self\.pool\.cursor\(\)      # self.pool.cursor()
                    )
                    \.(execute|sql)\s*               # method execute/sql
                    \(.*?(["']{1,3})                 # open quote
                    \s*(INSERT|DELETE)\b
                )
            ''', re.VERBOSE
        )

        # any var.execute(...) with inline SQL
        self.general_sql_pattern = re.compile(
            r'''(?i)
                (
                    (\w+)                             # any variable
                    \.(execute|sql)\s*               # method execute/sql
                    \(.*?(["']{1,3})                 # open quote
                    \s*(INSERT|DELETE)\b
                )
            ''', re.VERBOSE
        )

        # variable assignment with SQL
        self.sql_variable_pattern = re.compile(
            r'''(?i)
                (
                    (\w+)                            # variable name
                    \s*=\s*                         # equals
                    (["']{1,3})                     # quote
                    .*?\b(INSERT|DELETE)\b         # SQL keywords
                )
            ''', re.VERBOSE
        )

        # usage of variable in execute(sql)
        self.execute_var_pattern = re.compile(
            r'''(?i)
                (\w+)\.(execute|sql)\s*\(\s*(\w+)\s*\)
            ''', re.VERBOSE
        )

    def _process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        variables_with_sql = set()

        for idx, line in enumerate(lines, start=1):
            # direct odoo sql
            if self.odoo_sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip(), 'Odoo SQL'))
            # general direct sql
            elif self.general_sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip(), 'General SQL'))

            # variable assignment with sql
            m = self.sql_variable_pattern.search(line)
            if m:
                varname = m.group(2)
                variables_with_sql.add(varname)
                self.violations.append((file_path, idx, line.strip(), 'SQL in variable'))

            # execute(variable)
            m2 = self.execute_var_pattern.search(line)
            if m2:
                varname = m2.group(3)
                if varname in variables_with_sql:
                    self.violations.append((file_path, idx, line.strip(), 'Execute SQL variable'))

    def run(self):
        self.violations = []

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        if self.violations:
            print("[ERROR] Forbidden raw SQL (INSERT/DELETE) usage detected:\n")
            for path, line, content, typ in self.violations:
                print(f" - [{typ}] {path}:{line} -> {content}")
            sys.exit(1)
        else:
            print("[OK] No raw SQL INSERT/DELETE usage found.")
            sys.exit(0)

def main():
    checker = SQLChecker(directory=os.getcwd())
    checker.run()

if __name__ == '__main__':
    SystemExit(main())
