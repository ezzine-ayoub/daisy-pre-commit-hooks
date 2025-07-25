import ast
import os
import sys
from collections import defaultdict

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def get_all_python_files(root_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                full_path = os.path.join(dirpath, filename)
                py_files.append(full_path)
    return py_files


def get_module_name(file_path, root_dir):
    rel_path = os.path.relpath(file_path, root_dir)
    parts = rel_path.split(os.sep)
    return parts[0] if parts else ""


def extract_class_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=file_path)
    except Exception:
        return []

    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_data = {
                "name": node.name,
                "methods": {},
                "_name": None,
                "_inherit": None,
                "file": file_path
            }

            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "_name" and isinstance(item.value, ast.Str):
                                class_data["_name"] = item.value.s
                            elif target.id == "_inherit" and isinstance(item.value, ast.Str):
                                class_data["_inherit"] = item.value.s

                if isinstance(item, ast.FunctionDef):
                    try:
                        method_code = ast.unparse(item)
                    except Exception:
                        method_code = item.name
                    class_data["methods"][item.name] = method_code.strip()

            if class_data["_name"] or class_data["_inherit"]:
                classes.append(class_data)
    return classes


def group_classes_by_model(classes):
    model_groups = defaultdict(list)

    for cls in classes:
        keys = set()
        if cls["_name"]:
            keys.add(cls["_name"])
        if cls["_inherit"]:
            keys.add(cls["_inherit"])
        for key in keys:
            model_groups[key].append(cls)

    return model_groups


def find_duplicate_methods(model_groups):
    duplicates = []
    for model, class_list in model_groups.items():
        seen_methods = {}
        for cls in class_list:
            for method_name, method_code in cls["methods"].items():
                key = (method_name, method_code)
                if key in seen_methods:
                    duplicates.append({
                        "model": model,
                        "method": method_name,
                        "original": seen_methods[key],
                        "duplicate": f"{cls['name']} ({cls['file']})"
                    })
                else:
                    seen_methods[key] = f"{cls['name']} ({cls['file']})"
    return duplicates


def main():
    root_dir = os.getcwd()
    files = get_all_python_files(root_dir)

    module_classes = defaultdict(list)

    for file_path in files:
        module = get_module_name(file_path, root_dir)
        classes = extract_class_info(file_path)
        module_classes[module].extend(classes)

    duplicates = []

    for module, classes in module_classes.items():
        grouped_by_model = group_classes_by_model(classes)
        module_duplicates = find_duplicate_methods(grouped_by_model)
        if module_duplicates:
            duplicates.extend(module_duplicates)

    if duplicates:
        print("\n🚫 Duplicate method(s) detected in related model classes within the same module:\n")
        for d in duplicates:
            print(f" - Method '{d['method']}' is duplicated in model '{d['model']}'")
            print(f"   -> First defined in: {d['original']}")
            print(f"   -> Duplicated in   : {d['duplicate']}\n")
        sys.exit(1)
    else:
        print("✅ No duplicated methods found.")
        sys.exit(0)


if __name__ == '__main__':
    SystemExit(main())
