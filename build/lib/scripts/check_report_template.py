import os
import re
import sys
import argparse
import json
sys.stdout.reconfigure(encoding='utf-8')

parser = argparse.ArgumentParser(description="Check duplicate method names in Odoo classes")
parser.add_argument('--addons', help='addons')
parser.add_argument('--MANDATORY_FIELDS', help='MANDATORY_FIELDS')
parser.add_argument('filenames', nargs='*', help='Files passed by pre-commit')
args = parser.parse_args()

class ReportFieldChecker:
    def __init__(self):
        self.directory = os.getcwd()  # خذ المسار الحالي تلقائيا
        self.pattern_record = re.compile(
            r'<record[^>]+model=["\']ir.actions.report["\'][^>]*>.*?</record>', re.DOTALL | re.IGNORECASE
        )
        self.pattern_field_report_name = re.compile(
            r'<field name=["\']report_name["\'][^>]*>(.*?)</field>', re.IGNORECASE
        )
        self.template_pattern = re.compile(
            r'<template[^>]*(?:id|name)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE
        )

    def check_reports(self):
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

    def _process_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            records = self.pattern_record.findall(content)
            if not records:
                return

            lines = content.splitlines()

            for record in records:
                match = self.pattern_field_report_name.search(record)
                if match:
                    report_name = match.group(1)
                    self._check_dossier_exists(report_name, lines, file_path)

        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")

    def _check_dossier_exists(self, report_name, lines, file_path):
        dossier_name = report_name.split('.')[0] if report_name else ""
        if not dossier_name:
            return
        if args.addons:
            dossier_path = os.path.join(self.directory, args.addons, dossier_name)
        else:
            dossier_path = os.path.join(self.directory, dossier_name)
        clickable_path = f"file:///{file_path.replace(os.sep, '/')}"
        line_number = self._find_line_number(lines, report_name)
        if not os.path.exists(dossier_path):
            print(
                f"⚠️ : Dossier '{dossier_name}' from report_name '{report_name}' not found in {args.addons} at:\n⚠️ {clickable_path}:{line_number}"
            )
            sys.exit(1)
        self.find_templates_with_id_or_name(dossier_path, report_name.split('.')[1],f"{clickable_path}:{line_number}")

    def _find_line_number(self, lines, search_text):
        for i, line in enumerate(lines):
            if search_text in line:
                return i + 1
        return 0

    def find_templates_with_id_or_name(self, directory, search,path_line):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.xml'):  # كل ملفات XML في المشروع
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            matches = self.template_pattern.findall(content)
                            if search in matches:
                                sys.exit(0)
                    except Exception as e:
                        print(f"⚠️ Could not read {file_path}: {e}")
        print(f"⚠️ Could not read {directory} \n⚠️ check : {path_line}")
        print("⚠️ maybe name or id is incorrect or template in other module or not exist.")
        sys.exit(1)

# MANDATORY_FIELDS = {
#     "ir.ui.view": ["name", "model"],
#     "ir.actions.act_window": ["name", "res_model", "view_mode"],
#     "ir.actions.report": ["name", "model", "report_name"],
#
# }
MANDATORY_FIELDS = dict(json.loads(args.MANDATORY_FIELDS))
class XMLFieldValidator:
    def __init__(self, directory):
        self.directory = directory
        self.pattern_record = r'<record[^>]+model=["\'](.*?)["\'][^>]*>.*?</record>'
        self.pattern_field = r'<field name=["\'](.*?)["\'](?:[^>]*)>(.*?)</field>'

    def run(self):
        has_errors = False
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    if self._process_file(file_path):
                        has_errors = True
        if has_errors:
            sys.exit(1)

    def _remove_comments(self, content):
        return re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    def _process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            clean_content = self._remove_comments(original_content)
            records = re.findall(self.pattern_record, clean_content, re.DOTALL)

            has_error = False
            for record_model in records:
                record_block = self._extract_record_block(clean_content, record_model)
                record_block_original = self._extract_record_block(original_content, record_model)

                if record_model in MANDATORY_FIELDS:
                    missing = self._validate_fields(record_block, record_model)
                    if missing:
                        line = self._find_line_number(original_content, record_block_original)
                        clickable_path = f"file:///{file_path.replace(os.sep, '/')}:{line}"
                        print(f"❌ Missing fields for model='{record_model}': {missing}\n {clickable_path}")
                        has_error = True


            return has_error

    def _extract_record_block(self, content, model):
        pattern = rf'<record[^>]+model=["\']{re.escape(model)}["\'][^>]*>.*?</record>'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0) if match else ""

    def _validate_fields(self, record, model):
        found_fields = dict(re.findall(self.pattern_field, record))
        return [field for field in MANDATORY_FIELDS[model] if field not in found_fields]

    def _get_field_value(self, record):
        found_fields = dict(re.findall(self.pattern_field, record))
        return found_fields.get('name')

    def _find_line_number(self, content, block):
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if block.strip() in line:
                return idx + 1

        position = content.find(block.strip())
        if position != -1:
            return content[:position].count('\n') + 1
        return 0

def main():
    directory = os.getcwd()
    validator = XMLFieldValidator(directory)
    validator.run()
    checker = ReportFieldChecker()
    checker.check_reports()

if __name__ == "__main__":
    SystemExit(main())

