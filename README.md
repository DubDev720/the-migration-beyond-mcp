# The Migration Beyond MCP

A companion repo for practical migration resources and templates that help you evolve an MCP server into lighter, more portable forms (CLI, file‑system scripts, and Claude skills) without replacing your existing MCP setup.

This work builds on and complements the beyond-mcp examples by IndyDevDan which can be found at https://github.com/disler/beyond-mcp

## Pick your path

- MCP → File‑System Scripts (focused, minimal-context scripts)
  - migration/guides/guide_file_system_scripts_migration.md

- MCP → CLI + File‑System Scripts + Claude Skills (end‑to‑end playbook)
  - migration/migration_plan.md

## What you’ll find here

- A concise guide for turning MCP tools into self‑contained scripts with `--help` and `--json`.
- An expanded, additive migration playbook for building a canonical CLI, extracting fine‑grained scripts, and packaging them as Claude skills.
- Patterns for progressive disclosure, consistent parameters/flags, clean JSON output, and stable exit codes.
- A CLI/Script generator at scripts/generate_cli_script.py (usage in the script header, or run: python scripts/generate_cli_script.py --help).


## Attribution

This repository expands upon the excellent beyond-mcp project by IndyDevDan, serving as an addition—not a replacement—to improve the migration experience for teams wanting multiple capability surfaces.
