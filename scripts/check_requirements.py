import ast
import os
import sys
import glob
import argparse

sys.stdout.reconfigure(encoding='utf-8')

parser = argparse.ArgumentParser(description="Check Odoo __manifest__.py files")
parser.add_argument('--required_keys', help='Champs requis séparés par des virgules')
parser.add_argument('--debug', action='store_true', help='Affiche les messages de debug')
parser.add_argument('filenames', nargs='*', help='Fichiers passés par pre-commit')
args = parser.parse_args()


class ManifestChecker:
    def __init__(self, base_directory=None):
        self.base_directory = base_directory or os.getcwd()
        self.required_fields = args.required_keys.split(',') if args.required_keys else []
        self.debug = args.debug

    def _log(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")

    def _parse_manifest_file(self, file_path):
        """Analyse un fichier __manifest__.py et retourne son contenu sous forme de dictionnaire."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return ast.literal_eval(content)
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse du fichier {file_path}: {e}")
            sys.exit(1)

    def _check_required_fields(self, manifest_content, file_path):
        """Vérifie que tous les champs obligatoires sont présents et valides."""
        missing_fields = []
        for field in self.required_fields:
            if field not in manifest_content or not manifest_content[field]:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ Les champs suivants sont manquants ou vides dans le fichier {file_path}:")
            for field in missing_fields:
                print(f"- {field}")
            sys.exit(1)
        else:
            self._log(f"✔ Tous les champs obligatoires sont présents dans {file_path}.")

    def _check_data_files(self, file_path, manifest_content):
        """Vérifie que tous les fichiers listés dans 'data' existent."""
        data_files = manifest_content.get('data', [])
        missing_files = []

        for data_file in data_files:
            full_file_path = os.path.normpath(os.path.join(os.path.dirname(file_path), data_file))
            print(full_file_path)
            sys.exit(1)
            if not os.path.isfile(full_file_path):
                missing_files.append((data_file, full_file_path))

        if missing_files:
            print(f"\n❌ Fichiers listés dans 'data' manquants dans {file_path}:")
            for data_file, full_path in missing_files:
                print(f"- '{data_file}' n'existe pas. (Chemin attendu : {full_path})")
                print("  ➤ Vérifie le nom, le chemin, ou une virgule oubliée.")
            sys.exit(1)

    def _check_assets_files(self, file_path, manifest_content):
        """Vérifie que tous les fichiers listés dans 'assets' existent (y compris les 'remove')."""
        assets = manifest_content.get('assets', {})
        missing_files = []

        for bundle_name, file_list in assets.items():
            for entry in file_list:
                if isinstance(entry, tuple) and len(entry) == 2:
                    _, asset_path = entry
                else:
                    asset_path = entry

                full_glob_path = os.path.dirname(os.path.dirname(file_path))+"/"+asset_path
                full_glob_path = full_glob_path.replace('/','\\')
                matches = glob.glob(full_glob_path, recursive=True)
                if not matches:
                    missing_files.append((asset_path, full_glob_path, bundle_name))

        if missing_files:
            print(f"\n❌ Fichiers d'assets manquants dans {file_path}:")
            for asset_path, full_path, bundle in missing_files:
                print(f"- '{asset_path}' (bundle : {bundle}) n'existe pas.")
                print(f"  → Chemin attendu : {full_path}")
                print("  ⚠️ Vérifie le nom, le chemin relatif, les jokers glob (**), ou une virgule oubliée.")
            sys.exit(1)

    def check_manifest_file(self, file_path):
        """Vérifie un fichier __manifest__.py spécifique."""
        manifest_content = self._parse_manifest_file(file_path)
        self._check_required_fields(manifest_content, file_path)
        self._check_data_files(file_path, manifest_content)
        self._check_assets_files(file_path, manifest_content)

    def check_all_manifest_files(self):
        """Parcourt tout le répertoire pour vérifier tous les fichiers '__manifest__.py'."""
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                if file == '__manifest__.py':
                    file_path = os.path.join(root, file)
                    self._log(f"Analyse du fichier manifeste : {file_path}")
                    self.check_manifest_file(file_path)


def main():
    checker = ManifestChecker()
    checker.check_all_manifest_files()


if __name__ == "__main__":
    SystemExit(main())