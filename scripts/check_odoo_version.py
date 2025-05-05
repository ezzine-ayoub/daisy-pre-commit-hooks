#!/usr/bin/env python3
import sys
import re

def find_version():
    try:
        with open('odoo/odoo/tools/config.py', 'r') as f:
            content = f.read()
            match = re.search(r'VERSION_INFO\s*=\s*\((\d+),\s*(\d+),\s*(\d+)', content)
            if match:
                major, minor, patch = match.groups()
                return f"{major}.{minor}.{patch}"
    except FileNotFoundError:
        pass
    return None

def main():
    expected_major = 16  # put the version you expect
    version = find_version()
    if not version:
        print("❌ Could not detect Odoo version.")
        return 1
    major = int(version.split('.')[0])
    if major != expected_major:
        print(f"❌ Wrong Odoo version detected: {version}. Expected: {expected_major}.x.x")
        return 1
    print(f"✅ Odoo version {version} detected.")
    return 0

if __name__ == "__main__":
    SystemExit(main())
