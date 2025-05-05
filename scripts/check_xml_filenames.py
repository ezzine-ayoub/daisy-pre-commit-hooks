import os
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_IGNORE_DIRS = ['.idea', '__pycache__', '.vscode', '.git']

parser = argparse.ArgumentParser(description="Check module directory names in Odoo addons")
parser.add_argument('--addons', help='Base path to addons directory')
parser.add_argument('--IGNORE_DIRECTORIES',
                    help='Comma-separated list of directories to ignore (in addition to defaults)')
parser.add_argument('--allowed-prefixes', help='Comma-separated list of allowed module prefixes')
parser.add_argument('filenames', nargs='*', help='Files passed by pre-commit')
args = parser.parse_args()


class ModuleDirectoryChecker:
    def __init__(self, base_path, allowed_prefixes, ignored_modules):
        self.base_path = base_path
        self.allowed_prefixes = tuple(allowed_prefixes)
        self.ignored_modules = set(ignored_modules)
        self.errors = []

    def _list_directories(self):
        return [
            item for item in os.listdir(self.base_path)
            if os.path.isdir(os.path.join(self.base_path, item))
        ]

    def check_directories(self):
        if not os.path.exists(self.base_path):
            print(f"[ERROR] Path not found: {self.base_path}")
            return 1

        for directory in self._list_directories():
            if directory in self.ignored_modules:
                continue
            if not directory.startswith(self.allowed_prefixes) and self.allowed_prefixes:
                self.errors.append(
                    f"[Invalid module name] {directory} ➜ name must start with one of: {self.allowed_prefixes}"
                )

        if self.errors:
            for err in self.errors:
                print(err)
            return 1
        return 0


def main():
    if not args.allowed_prefixes:
        args.allowed_prefixes = ""

    allowed_prefixes = [p.strip() for p in args.allowed_prefixes.split(',') if p.strip()]

    # Combine default ignores with user-provided ones (if any)
    custom_ignores = [i.strip() for i in (args.IGNORE_DIRECTORIES or '').split(',') if i.strip()]
    all_ignores = DEFAULT_IGNORE_DIRS + custom_ignores

    base_path = os.path.join(os.getcwd(), args.addons if args.addons else "")
    checker = ModuleDirectoryChecker(base_path, allowed_prefixes, all_ignores)
    sys.exit(checker.check_directories())


if __name__ == "__main__":
    main()
