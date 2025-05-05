import os
import xml.etree.ElementTree as ET
import sys

class XMLChecker:
    def __init__(self, directory):
        self.directory = directory

    def _process_file(self, file_path):
        try:
            tree = ET.parse(file_path)  # Try parsing the XML file
            root = tree.getroot()

        except ET.ParseError as e:
            # If there's an XML parsing error (such as mismatched tags), capture the line and column
            error_message = str(e)
            line_number = error_message.split("line ")[1].split(",")[0]
            column_number = error_message.split("column ")[1].split()[0]
            self.violations.append((file_path, line_number, column_number, error_message))

    def run(self):
        self.violations = []  # Reset violations list

        # Walk through the directory and its subdirectories
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        # If any malformed XML files were found, print them
        if self.violations:
            print("[ERROR] Malformed XML files detected:\n")
            for path, line, column, error in self.violations:
                clickable_path = f"file:///{path.replace(os.sep, '/')}"
                print(f"   -> {clickable_path}[{line}:{column}]")
            sys.exit(1)
        else:
            print("[OK] All XML files are well-formed.")
            sys.exit(0)

def main():
    checker = XMLChecker(directory=os.getcwd())
    checker.run()
if __name__ == '__main__':
    # Run the checker on the current directory
    SystemExit(main())
