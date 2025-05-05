import os
import xml.etree.ElementTree as ET
import sys
from collections import defaultdict


class XMLIdDuplicationChecker:
    def __init__(self, directory):
        self.directory = directory
        self.ids_count = defaultdict(list)  # Dictionary to store IDs and the files where they appear
        self.violations = []  # List to store violations of ID duplication

    def _process_file(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Traverse all <record> elements to check IDs
            for idx, elem in enumerate(root.iter('record')):
                if 'id' in elem.attrib:
                    record_id = elem.attrib['id']
                    # Calculate the column position (start position of the id)
                    line_number = idx + 1
                    line = str(ET.tostring(elem, encoding="unicode")).strip()
                    column_number = line.find(f'id="{record_id}"') + 1  # Find the position of the id attribute

                    # Store the occurrences of the ID with file path, line, and column
                    self.ids_count[record_id].append((file_path, line_number, column_number))

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def run(self):
        # Traverse all XML files in the specified directory
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        # Display the found duplications
        found_duplicates = False
        for record_id, occurrences in self.ids_count.items():
            if len(occurrences) > 1:  # If an ID appears in more than one file
                found_duplicates = True
                print(f"[ERROR] Duplicate ID '{record_id}' found in the following files:\n")
                for file_path, line_number, column_number in occurrences:
                    # Convert file path to clickable path for Windows
                    clickable_path = f"file:///{file_path.replace(os.sep, '/')}"
                    print(f"   -> {clickable_path}:{int(line_number)}:{int(column_number)}")

        if found_duplicates:
            sys.exit(1)
        else:
            print("[OK] No duplicate IDs found.")
            sys.exit(0)


def main():
    checker = XMLIdDuplicationChecker(directory=os.getcwd())
    checker.run()
if __name__ == '__main__':
    # Run the duplicate ID check in the current directory
    SystemExit(main())
