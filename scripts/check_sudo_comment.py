# scripts/check_sudo_comment.py
import os
import re
import sys

class SudoChecker:
    def __init__(self, directory):
        self.directory = directory
        self.sudo_pattern = re.compile(
            r"self\.env\[\s*['\"][\w\.]+['\"]\s*\]\.sudo\(\)", re.IGNORECASE
        )
        self.violations = []

    def _process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            match = self.sudo_pattern.search(line)
            if line.strip().startswith("#"):
                continue
            if match:
                comment_pos = line.find('#')
                sudo_pos = match.start()

                if comment_pos == -1 or comment_pos < sudo_pos:
                    self.violations.append((file_path, idx+1, line.strip()))

    def run(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        if self.violations:
            print("[ERROR] Missing inline comment for `.sudo()` usage:\n")
            for path, line, content in self.violations:
                print(f" - {path}:{line} -> {content}")
            sys.exit(1)
        else:
            print("[OK] All `.sudo()` usages have an inline comment.")
            sys.exit(0)

def main():
    checker = SudoChecker(directory=os.getcwd())
    checker.run()
if __name__ == '__main__':
    SystemExit(main())
