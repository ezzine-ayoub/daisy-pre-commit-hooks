#!/usr/bin/env python3
import os
from pathlib import Path
import sys
import argparse
import tokenize
from io import StringIO

sys.stdout.reconfigure(encoding="utf-8")
EXIT_CODE = 0
ALLOWED_EXTENSIONS = {".py", ".xml"}

parser = argparse.ArgumentParser(description="Check max word count per line in Odoo files (excluding full-line comments)")
parser.add_argument("--max_line_length", type=int, default=20, help="Max words per line (excluding full-line comments)")
args = parser.parse_args()
max_line_length = args.max_line_length

total_files = 0
total_lines = 0
total_violations = 0

def remove_inline_comment(line: str, ext: str) -> str:
    """
    Remove inline comments from the line, but only if they are actual comments.
    This ensures we don't cut off the middle of strings with #.
    """
    if ext == ".py":
        try:
            tokens = list(tokenize.generate_tokens(StringIO(line).readline))
            result = ""
            for tok_type, tok_string, _, _, _ in tokens:
                if tok_type == tokenize.COMMENT:
                    break  # First comment = end of the code part
                result += tok_string
            return result
        except:
            return line
    elif ext == ".xml":
        return line.split("<!--")[0]
    return line

def is_full_comment(line: str, ext: str) -> bool:
    """
    Determine if the line is a full comment (ignores lines starting with #).
    """
    stripped = line.strip()
    if not stripped:
        return True  # Empty lines are considered comments
    if ext == ".py":
        return stripped.startswith("#")  # Full comment starts with #
    elif ext == ".xml":
        return stripped.startswith("<!--") or stripped.endswith("-->")  # Full comment in XML
    return False

def check_file(path: Path):
    global EXIT_CODE, total_files, total_lines, total_violations
    ext = path.suffix
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                total_lines += 1
                if is_full_comment(line, ext):
                    continue  # Skip full-line comments
                line_no_comment = remove_inline_comment(line, ext).strip()
                word_count = len(line_no_comment.split())
                if word_count > max_line_length:
                    print(
                        f"{path.resolve().as_posix()}:{lineno}:1: [too-many-words] {word_count} words (excluding full-line comments)"
                    )
                    print(f"    {line.strip()}")
                    EXIT_CODE = 1
                    total_violations += 1
        total_files += 1
    except Exception as e:
        print(f"⚠️ Error reading file {path}: {e}")

def main():
    cwd = Path(os.getcwd())
    for file_path in cwd.rglob("*"):
        if (
            file_path.is_file()
            and file_path.suffix in ALLOWED_EXTENSIONS
            and not any(ignored in file_path.parts for ignored in {".git", "venv", "__pycache__"})
        ):
            check_file(file_path)

    print("\n✅ Scan complete")
    print(f"  Files scanned     : {total_files}")
    print(f"  Lines scanned     : {total_lines}")
    print(f"  Violations found  : {total_violations}")
    return EXIT_CODE

if __name__ == "__main__":
    sys.exit(main())
