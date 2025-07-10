import os
import re
import sys

class SQLChecker:
    def __init__(self, directory):
        self.directory = directory

        self.odoo_sql_pattern = re.compile(
            r'''(?i)
                (
                    (
                        self\.env(\.cr)?              
                        | self\.pool\.cursor\(\)      
                    )
                    \.(execute|sql)\s*               
                    \(.*?(["']{1,3})                 
                    \s*(INSERT|DELETE)\b
                )
            ''', re.VERBOSE
        )

        self.general_sql_pattern = re.compile(
            r'''(?i)
                (
                    (\w+)                             
                    \.(execute|sql)\s*               
                    \(.*?(["']{1,3})                 
                    \s*(INSERT|DELETE)\b
                )
            ''', re.VERBOSE
        )

        self.sql_variable_pattern = re.compile(
            r'''(?i)
                (
                    (\w+)                            
                    \s*=\s*                         
                    (["']{1,3})                     
                    .*?\b(INSERT|DELETE)\b         
                )
            ''', re.VERBOSE
        )

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
            if self.odoo_sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip(), 'Odoo SQL'))
            elif self.general_sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip(), 'General SQL'))

            m = self.sql_variable_pattern.search(line)
            if m:
                varname = m.group(2)
                variables_with_sql.add(varname)
                self.violations.append((file_path, idx, line.strip(), 'SQL in variable'))

            m2 = self.execute_var_pattern.search(line)
            if m2:
                varname = m2.group(3)
                if varname in variables_with_sql:
                    self.violations.append((file_path, idx, line.strip(), 'Execute SQL variable'))

    def run(self):
        self.violations = []

        for root, dirs, files in os.walk(self.directory):
            # 🚨 ignore folders starting with `.`
            dirs[:] = [d for d in dirs if not d.startswith('.')]
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
