import os
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_IGNORE_DIRS = ['.idea', '__pycache__', '.vscode', '.git','.github']

parser = argparse.ArgumentParser(description="Check Odoo module XML file names")
parser.add_argument('--addons', help='Base path to addons directory')
parser.add_argument('--IGNORE_DIRECTORIES',
                    help='Comma-separated list of directories to ignore (in addition to defaults)')
parser.add_argument('--allowed-prefixes', help='Comma-separated list of allowed XML prefixes')
parser.add_argument('filenames', nargs='*', help='Files passed by pre-commit (ignored)')  # <= IMPORTANT
args = parser.parse_args()


class RecursiveXmlChecker:
    def __init__(self, root_path, allowed_prefixes):
        self.root_path = root_path
        self.allowed_prefixes = tuple(allowed_prefixes)
        self.errors = []

    def check_all_xml_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            # Ignore unwanted directories
            dirnames[:] = [d for d in dirnames if d not in DEFAULT_IGNORE_DIRS and d not in args.IGNORE_DIRECTORIES]

            for filename in filenames:
                if not filename.endswith('.xml'):
                    continue
                # Check if filename starts with one of the allowed prefixes
                if not any(filename.startswith(prefix) for prefix in self.allowed_prefixes):
                    full_path = os.path.join(dirpath, filename)
                    self.errors.append(
                        f"[Invalid XML filename] {filename} (in {full_path}) ➜ must start with one of: {self.allowed_prefixes}"
                    )

        if self.errors:
            for err in self.errors:
                print(err)
            return 1
        return 0


def main():
    # Handle the arguments
    if not args.allowed_prefixes:
        print("[ERROR] You must specify allowed prefixes.")
        sys.exit(1)

    # Convert allowed prefixes into a list
    allowed_prefixes = [p.strip() for p in args.allowed_prefixes.split(',') if p.strip()]

    # Convert the comma-separated directories in `IGNORE_DIRECTORIES` to a list
    ignore_dirs = [i.strip() for i in (args.IGNORE_DIRECTORIES or '').split(',') if i.strip()]

    base_path = os.path.join(os.getcwd(), args.addons if args.addons else "")

    # Check XML filenames with the allowed prefixes
    xml_checker = RecursiveXmlChecker(base_path, allowed_prefixes)
    xml_result = xml_checker.check_all_xml_files()

    sys.exit(xml_result)


if __name__ == "__main__":
    main()
