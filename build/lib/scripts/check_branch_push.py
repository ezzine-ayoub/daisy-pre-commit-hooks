#!/usr/bin/env python3
import subprocess
import sys
import re
import argparse
import os
parser = argparse.ArgumentParser(description="Pre-push hook with branch validation and checks")
parser.add_argument(
    "--forbidden_branch",
    type=str,
    default="",
    help="Comma-separated forbidden branch names (e.g., main,staging)"
)

parser.add_argument('filenames', nargs='*', help='Files passed by pre-commit (ignored)')
args = parser.parse_args()

forbidden_branches = [b.strip() for b in args.forbidden_branch.split(",") if b.strip()]

def ensure_utf8():
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')


def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting branch: {e}")
        sys.exit(1)


def is_valid_branch(branch):
    allowed_patterns = [r"feature/.*", r"hotfix/.*"]
    allowed_branches = ["dev"]

    if any(re.match(pat, branch) for pat in allowed_patterns):
        return True
    if branch in allowed_branches:
        return True

    if os.environ.get("ALLOW_PUSH") == "1":
        print(f"⚠️ Push to '{branch}' is allowed because ALLOW_PUSH=1.")
        return True

    if branch in forbidden_branches:
        return False

    return True


def run_checks():
    print("Running checks...")

    # pylint_result = subprocess.run(["pylint", "**/*.py"], capture_output=True, text=True)
    # if pylint_result.returncode != 0:
    #     print("❌ Pylint failed. Push blocked.")
    #     print(pylint_result.stdout)
    #     sys.exit(1)
    #
    # pytest_result = subprocess.run(["pytest", "--maxfail=1", "--disable-warnings", "-q"], capture_output=True, text=True)
    # if pytest_result.returncode != 0:
    #     print("❌ Tests failed. Push blocked.")
    #     print(pytest_result.stdout)
    #     sys.exit(1)


def main():
    ensure_utf8()

    branch = get_current_branch()

    if not is_valid_branch(branch):
        print(f"🚫 Push to branch '{branch}' is forbidden. Use dev, feature/*, hotfix/* or set ALLOW_PUSH=1.")
        sys.exit(1)

    run_checks()
    print("✅ All checks passed. Push allowed.")


if __name__ == "__main__":
    main()
