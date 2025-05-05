#!/usr/bin/env python3
import os
from pathlib import Path
import sys
import argparse

EXIT_CODE = 0
ALLOWED_EXTENSIONS = {".py", ".xml"}
parser = argparse.ArgumentParser(description="Check max_line_length in Odoo classes")
parser.add_argument('--max_line_length', help='max_line_length')
parser.add_argument('filenames', nargs='*', help='Files passed by pre-commit')
args = parser.parse_args()
max_line_length = args.max_line_length if args.max_line_length else 120
def remove_inline_comment(line: str, ext: str) -> str:
    if ext == ".py":
        return line.split("#")[0]
    elif ext == ".xml":
        # XML comments are usually multiline <!-- ... -->
        return line.split("<!--")[0]
    elif ext in {".txt", ".md"}:
        for comment_start in ("#", "//", ">"):
            if comment_start in line:
                return line.split(comment_start)[0]
    return line

def is_full_comment(line: str, ext: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if ext == ".py":
        return stripped.startswith("#")
    elif ext == ".xml":
        return stripped.startswith("<!--") or stripped.endswith("-->")
    elif ext in {".txt", ".md"}:
        return stripped.startswith("#") or stripped.startswith(">") or stripped.startswith("//")
    return False

def check_file(path: Path):
    global EXIT_CODE
    ext = path.suffix
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                if is_full_comment(line, ext):
                    continue
                line_no_comment = remove_inline_comment(line, ext).strip()
                word_count = len(line_no_comment.split())
                if word_count > max_line_length:
                    print(f"{path}:{lineno}:1 Line has {word_count} words (excluding comments)")
                    print(f"    {line.strip()}")
                    EXIT_CODE = 1
    except Exception as e:
        print(f"⚠️ Error reading file {path}: {e}")

def main():
    cwd = Path(os.getcwd())
    for file_path in cwd.rglob("*"):
        if file_path.is_file() and file_path.suffix in ALLOWED_EXTENSIONS:
            check_file(file_path)
    return EXIT_CODE

if __name__ == "__main__":
    main()
