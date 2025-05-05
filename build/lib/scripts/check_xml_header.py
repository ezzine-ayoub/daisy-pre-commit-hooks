import os
import sys

class XMLHeaderChecker:
    def __init__(self, directory, required_prefix='<?xml', excluded_dirs=None):
        self.directory = directory
        self.required_prefix = required_prefix.strip().lower()
        self.excluded_dirs = excluded_dirs or ['.idea', '.venv', '__pycache__','scripts']
        self.violations = []

    def _process_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip().lower()
                if not first_line.startswith(self.required_prefix):
                    self.violations.append((file_path, first_line))
        except Exception as e:
            print(f"[ERROR] Failed to read {file_path}: {e}")

    def run(self):
        for root, dirs, files in os.walk(self.directory):
            # حذف المجلدات لي بغينا نتجاهلو
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        if self.violations:
            print("[ERROR] The following XML files do not start with expected prefix:")
            for path, first_line in self.violations:
                print(f" - {path} -> starts with: <?xml version='1.0' encoding='utf-8'?>")
            sys.exit(1)
        else:
            print("[OK] All XML files start with the expected prefix.")
            sys.exit(0)

def main():
    checker = XMLHeaderChecker(directory=os.getcwd())
    checker.run()
if __name__ == '__main__':
    SystemExit(main())
