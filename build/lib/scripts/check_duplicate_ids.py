import os
import xml.etree.ElementTree as ET
import sys
import ast
from collections import defaultdict


class XMLIdDuplicationChecker:
    def __init__(self, directory):
        self.directory = directory
        self.module_ids = defaultdict(lambda: defaultdict(list))
        self.module_declared_files = defaultdict(set)

    def _get_module_name(self, file_path):
        rel_path = os.path.relpath(file_path, self.directory)
        parts = rel_path.split(os.sep)
        return parts[0] if parts else "unknown"

    def _load_manifest_files(self):
        """Load XML files declared in each module's __manifest__.py."""
        for module in os.listdir(self.directory):
            module_path = os.path.join(self.directory, module)
            manifest_path = os.path.join(module_path, "__manifest__.py")
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        data = ast.literal_eval(f.read())
                        data_files = data.get("data", []) + data.get("demo", []) + data.get("init_xml", [])
                        for xml_file in data_files:
                            full_path = os.path.normpath(os.path.join(module_path, xml_file))
                            if os.path.isfile(full_path):
                                self.module_declared_files[module].add(os.path.abspath(full_path))
                except Exception:
                    pass  # manifest file parsing error ignored silently

    def _process_file(self, file_path):
        try:
            # skip empty files
            if os.path.getsize(file_path) == 0:
                return

            tree = ET.parse(file_path)
            root = tree.getroot()
            module_name = self._get_module_name(file_path)

            for idx, elem in enumerate(root.iter('record')):
                if 'id' in elem.attrib:
                    record_id = elem.attrib['id']
                    line_number = idx + 1
                    line = str(ET.tostring(elem, encoding="unicode")).strip()
                    column_number = line.find(f'id="{record_id}"') + 1
                    self.module_ids[module_name][record_id].append(
                        (os.path.abspath(file_path), line_number, column_number)
                    )

        except ET.ParseError:
            # silently skip malformed XML files
            return
        except Exception:
            return

    def run(self):
        self._load_manifest_files()

        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        found_duplicates = False

        for module, ids_dict in self.module_ids.items():
            declared_files = self.module_declared_files.get(module, set())

            for record_id, occurrences in ids_dict.items():
                if len(occurrences) > 1:
                    # check if both/all files are declared in manifest
                    declared_occurrences = [
                        occ for occ in occurrences if occ[0] in declared_files
                    ]
                    if len(declared_occurrences) > 1:
                        found_duplicates = True
                        print(f"[ERROR] Duplicate ID '{record_id}' found in module '{module}' in declared files:\n")
                        for file_path, line_number, column_number in declared_occurrences:
                            clickable_path = f"file:///{file_path.replace(os.sep, '/')}"
                            print(f"   -> {clickable_path}:{int(line_number)}:{int(column_number)}")
                        print("")

        if found_duplicates:
            sys.exit(1)
        else:
            print("[OK] No duplicate IDs found among declared files.")
            sys.exit(0)


def main():
    checker = XMLIdDuplicationChecker(directory=os.getcwd())
    checker.run()


if __name__ == '__main__':
    SystemExit(main())
