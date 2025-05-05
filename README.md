# daisy-pre-commit-hooks
This project provides a set of pre-commit hooks to enforce best practices during development. It includes hooks for linting, formatting, security checks, and validation. By integrating these hooks, the project ensures consistent code quality, detects issues early, and prevents common mistakes.
# My Odoo Project with pre-commit Hooks

This project uses **pre-commit hooks** to automate various code quality checks before each commit. The hooks are configured to ensure the quality and consistency of the codebase.

## Prerequisites

- **Git** must be installed on your system.
- **Python 3.11+** should be installed.
- **pre-commit** must be installed globally.

You can install **pre-commit** by running:

in your director project run in terminal:

```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate
pip install pre-commit
pre-commit install
pre-commit run
pre-commit run --all-files
pre-commit clean
```
```bash
exclude: 'daisy-pre-commit-hooks/scripts/.*|odoo18/(check_manifest|wait-for-psql)\.py|check_duplicate_ids\.py|.idea/.*'
repos:
  # Standard code quality hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
        files: '.*|[^.].*'

      - id: check-yaml
        files: '.*|[^.].*\.ya?ml$'

      - id: check-added-large-files
        files: '.*|[^.].*'
        exclude: 'odoo18/.*'

  - repo: https://github.com/pre-commit/mirrors-pylint
    rev: v3.0.0a5
    hooks:
      - id: pylint
        name: pylint
        entry: pylint --max-line-length=120
        language: system
        types: [ python ]
        args:
          - "--max-line-length=120"
          - "--disable=all"
          - "--enable=unused-variable,invalid-name"
          - "--enable=missing-function-docstring"

  - repo: https://github.com/Daisy-Consulting/daisy-pre-commit-hooks
    rev: main
    hooks:
      ##########################################################################################
      ######################################just for new new ####################################
      ##########################################################################################
      - id: check-xml-header
      - id: check-print-usage
      - id: check-sudo-comment
      - id: check-long-functions
      - id: check-xml-filenames
        args:
          - "--addons="
          - "--allowed-prefixes="
          - "--IGNORE_DIRECTORIES="
      - id: check-lines-max
      - id: check-manifest-fields
        args:
          - "--required_keys=name,version,category,description,author"

      - id: check-odoo-models-naming
        args:
          - "--addons="
          - "--allowed-prefixes="
          - "--IGNORE_DIRECTORIES="
      - id: detect-raw-sql-delete-insert
      ################################################################################################################################
      ######################################for old and new if this project old comment this part ####################################
      ################################################################################################################################
      - id: check_duplicate_method_names
      - id: class-property-checker
      - id: check-xml-closing-tags
      - id: check-report-template
        args:
          - "--addons="
      - id: check-compute-function
      - id: check-duplicate-ids





#      - id: check-module-prefix
#        args:
#          - "--addons="
#          - "--IGNORE_DIRECTORIES="
#          - "--PREFIXES="
```
