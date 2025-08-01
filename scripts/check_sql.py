import os
import re
import sys

class SQLChecker:
    def __init__(self, directory):
        self.directory = directory
        self.violations = []

        # Pattern for Odoo cursor usage with raw SQL
        self.odoo_sql_pattern = re.compile(
            r'''(?i)
                (
                    (
                        self\.env\.cr              
                        | self\.pool\.cursor\(\)      
                    )
                    \.execute\s*               
                    \(.*?(["']{1,3})                 
                    \s*(INSERT|DELETE|UPDATE)\b
                )
            ''', re.VERBOSE
        )

        # Pattern for general cursor execute with raw SQL
        self.general_sql_pattern = re.compile(
            r'''(?i)
                (
                    (\w+)                             
                    \.execute\s*               
                    \(.*?(["']{1,3})                 
                    \s*(INSERT|DELETE|UPDATE)\b
                )
            ''', re.VERBOSE
        )

        # Pattern for SQL variables - more specific to avoid false positives
        self.sql_variable_pattern = re.compile(
            r'''(?i)
                (
                    (?!_name|_description|_inherit|_rec_name|_table)  # Exclude Odoo fields
                    (\w+)                                      # Variable name
                    \s*=\s*                                   # Assignment
                    (["']{3}|["'])                            # Quote start
                    [^"']*                                    # Any content
                    (INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+\w+\s+SET)  # SQL keywords
                    [^"']*                                    # Rest of content
                    \3                                        # Matching quote end
                )
            ''', re.VERBOSE
        )

        # Pattern for executing variables that might contain SQL
        self.execute_var_pattern = re.compile(
            r'''(?i)
                (\w+)\.execute\s*\(\s*(\w+)\s*\)
            ''', re.VERBOSE
        )

    def _should_skip_file(self, file_path):
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__', 
            '.git', 
            '.pyc', 
            'test.py',  # Skip this checker file itself
            '__init__.py'  # Often contains only imports
        ]
        return any(skip in file_path for skip in skip_patterns)

    def _should_skip_line(self, line):
        """Check if line should be skipped"""
        stripped = line.strip()
        # Skip empty lines, comments, and docstrings
        if (not stripped or 
            stripped.startswith('#') or 
            stripped.startswith('"""') or 
            stripped.startswith("'''") or
            stripped.startswith('*') or  # JSDoc style comments
            'TODO' in stripped or
            'FIXME' in stripped):
            return True
        return False

    def _process_file(self, file_path):
        """Process a single Python file for SQL violations"""
        if self._should_skip_file(file_path):
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return

        variables_with_sql = set()

        for idx, line in enumerate(lines, start=1):
            if self._should_skip_line(line):
                continue
                
            # Check for direct Odoo SQL usage
            if self.odoo_sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip(), 'Direct Odoo SQL'))
                continue
                
            # Check for general SQL execute patterns
            if self.general_sql_pattern.search(line):
                self.violations.append((file_path, idx, line.strip(), 'General SQL Execute'))
                continue

            # Check for SQL in variables
            match = self.sql_variable_pattern.search(line)
            if match:
                varname = match.group(2)
                variables_with_sql.add(varname)
                self.violations.append((file_path, idx, line.strip(), 'SQL in variable'))

            # Check for execution of variables containing SQL
            match2 = self.execute_var_pattern.search(line)
            if match2:
                varname = match2.group(2)
                if varname in variables_with_sql:
                    self.violations.append((file_path, idx, line.strip(), 'Execute SQL variable'))

    def run(self):
        """Run the SQL checker on all Python files in the directory"""
        print("Starting SQL check...")
        
        file_count = 0
        for root, dirs, files in os.walk(self.directory):
            # Ignore hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)
                    file_count += 1

        print(f"Checked {file_count} Python files.")

        if self.violations:
            print("")
            print("[ERROR] Forbidden raw SQL (INSERT/DELETE/UPDATE) usage detected:")
            print("=" * 60)
            for path, line_num, content, violation_type in self.violations:
                print(f"* [{violation_type}] {path}:{line_num}")
                print(f"  Code: {content}")
                print("")
            print(f"Total violations found: {len(self.violations)}")
            return False
        else:
            print("")
            print("[OK] No forbidden raw SQL INSERT/DELETE/UPDATE usage found.")
            return True

def main():
    """Main function to run the SQL checker"""
    try:
        checker = SQLChecker(directory=os.getcwd())
        success = checker.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("")
        print("Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running SQL checker: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
