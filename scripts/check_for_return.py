import os
import ast
import sys  # Import de sys pour gérer l'arrêt du programme avec des codes de sortie

class ClassPropertyChecker:
    def __init__(self, directory):
        self.directory = directory

    def _process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        try:
            tree = ast.parse(content)  # Analyser le contenu du fichier pour obtenir l'arbre syntaxique
        except SyntaxError as e:
            print(f"SyntaxError in file {file_path}: {e}")
            return

        # Rechercher les classes avec les propriétés _name ou _inherit
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):  # Vérifier les définitions de classes
                class_name = node.name
                has_property = False
                functions = []

                # Vérifier si la classe a les propriétés _name ou _inherit
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Attribute):
                                has_property = True
                    # Vérifier si la classe a les fonctions write() ou copy()
                    if isinstance(item, ast.FunctionDef):
                        if item.name in ['write', 'copy','create','unlink']:
                            functions.append(item.name)
                            # Vérifier la présence d'une instruction return dans la fonction
                            has_return = False
                            for sub_item in item.body:
                                if isinstance(sub_item, ast.Return):
                                    has_return = True
                            if not has_return:
                                # Ajouter le numéro de ligne où la fonction commence
                                self.violations.append((file_path, class_name, item.name, "No return statement found", item.lineno))

                # Si la classe a une propriété et une fonction, on l'affiche
                if has_property and functions:
                    for func in functions:
                        # Si une fonction write ou copy n'a pas de return, on la signale
                        if (file_path, class_name, func, "No return statement found") not in self.violations:
                            self.violations.append((file_path, class_name, func, "Missing return", node.lineno))

    def run(self):
        self.violations = []  # Reset violations list

        for root, dirs, files in os.walk(self.directory):
            # Ignore .venv directory
            if '.venv' in dirs:
                dirs.remove('.venv')

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

        # Si des violations sont trouvées, les afficher avec les numéros de ligne
        if self.violations:
            print("[ERROR] Issues detected with classes and functions:\n")
            for path, class_name, function, message, lineno in self.violations:
                clickable_path = f"file:///{path.replace(os.sep, '/')}"
                print(f" - {clickable_path}:{lineno}: Class '{class_name}', function '{function}' -> {message} at line {lineno}")
            sys.exit(1)  # Erreur détectée, quitter avec code 1 pour indiquer un échec
        else:
            print("[OK] No issues found.")
            sys.exit(0)  # Aucun problème trouvé, quitter avec code 0 pour indiquer un succès

def main():
    checker = ClassPropertyChecker(directory=os.getcwd())
    checker.run()
if __name__ == '__main__':
    SystemExit(main())
