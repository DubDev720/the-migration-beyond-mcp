# How to Use This Repository (User Guide)

This repository helps you evolve an MCP server into lighter, more portable formats:
- A canonical CLI (for automation and subprocess integration)
- File‑system scripts (self‑contained, minimal, easy to review and run)
- Claude Skills (discoverable, autonomous invocation in Claude Code)

It’s designed for humans (you and your team), not for agents. You’ll find practical guides, templates, and generators to help you plan, implement, validate, and operate these capabilities confidently.

Note: Earlier iterations of this repo referenced a legacy `refactor/` folder. The current structure no longer uses it; treat any similar folders in your own projects as deprecated in favor of the patterns described below.

--------------------------------------------------------------------------------

## Repository layout (current)

- `README.md` — Repo overview
- `how_to_use/` — This umbrella user guide (you’re here)
- `migration/`
  - `guides/`
    - `guide_cli_migration.md` — Authoritative, standalone MCP → CLI migration guide
    - `guide_file_system_scripts_migration.md` — Authoritative, standalone MCP → File‑System Scripts guide
    - `guide_claude_skills_migration.md` — Authoritative, standalone MCP → Claude Skills guide
  - `migration_plan.md` — “Pick your path” planning doc (single‑format vs split/multi‑format migration)
  - `templates/`
    - `file_skeletons/`
      - `cli_subcommand_skeleton.py` — Copy/paste skeleton for a CLI subcommand
      - `script_skeleton.py` — Copy/paste skeleton for a self‑contained script
    - `template_per_tool_mapping.md` — Fill‑in template to keep per‑tool parity across formats
    - `template.agent/` — Agent and command templates (e.g., docs scraper and load‑docs command)
    - `template_ai_docs/` — Template README for an `ai_docs/` folder in your project
    - `template_file_system_scripts/` — Example file‑system scripts and README patterns
- `scripts/`
  - `generate_cli_script.py` — Generator that emits real code files from arguments (CLI and/or script)
  - `scripts_index.py` — Utility to index a scripts folder for quick review and progressive disclosure
- `tests/`
  - `test_validation_plan.md` — Comprehensive, end‑to‑end validation plan (parity, error handling, pagination, CI)
- `.agent/`
  - `agents/` — Example local agents (e.g., `docs-scraper`) used for documentation workflows
  - `commands/` — Example commands (e.g., `load_ai_docs`, `prime`) that demonstrate how to orchestrate agents and scripts
  - `settings.json` — Declares this repo as a Beyond‑MCP extension/quickstart and points to local agents/commands

Example paths shown elsewhere in this guide (such as `apps/2_cli/`, `.golden/`, `.cache/`, `.claude/`) are illustrative for your own projects and are not required to exist in this repository.

--------------------------------------------------------------------------------

## How to choose your path

- CLI (Command‑Line Interface)
  - Best for: automation, CI/CD, subprocess integration, and canonical JSON contracts for your tools.
  - Start here if you want a single source of truth for HTTP interaction, pagination, retries, and `--json` output.
  - Guide: `migration/guides/guide_cli_migration.md`

- File‑System Scripts
  - Best for: minimal context usage, simple audit/review, and “drop‑in” capability reuse.
  - Each script is one file, self‑contained, and easy to run with flags and `--json`.
  - Guide: `migration/guides/guide_file_system_scripts_migration.md`

- Claude Skills
  - Best for: discoverable, autonomous usage by Claude Code with zero server setup.
  - Wrap self‑contained scripts, define SKILL.md triggers, and let the model activate when appropriate.
  - Guide: `migration/guides/guide_claude_skills_migration.md`

- Planning “single‑format” vs “split/multi‑format” migration
  - Use `migration/migration_plan.md` to decide:
    - Whether to migrate everything to one format (e.g., all to CLI)
    - Or map different tools to different formats (e.g., CLI + Scripts + Skills)

--------------------------------------------------------------------------------

## Quick starts

### 1) Generate a CLI subcommand and script (fastest path)
Use the generator to scaffold both a CLI subcommand and a script with correct conventions baked in (strict `--json`, clean exit codes, minimal stdout noise, consistent flags).

- Requirements:
  - Python 3.10+
  - `click` and `httpx` are required by the generated code (install in your project)
- Example:
```bash
python scripts/generate_cli_script.py markets \
  --target both \
  --binary yourcmd \
  --endpoint /v1/markets \
  --api-base-url https://api.example.com \
  --param limit:int:10 \
  --param query:str \
  --out-cli ./your_project/cli/markets.py \
  --out-script ./your_project/scripts/markets.py \
  --emit-test-plan ./your_project/tests/test_validation_plan.md \
  --force
```
Then:
- Add `click` and `httpx` to your project (via `uv add` or `pip install`).
- Run the outputs:
  - CLI: `python ./your_project/cli/markets.py --help` (or wire it to your CLI entrypoint)
  - Script: `python ./your_project/scripts/markets.py --help`

Tip: If your project uses `uv`, you can run with `uv run` instead of `python`.

### 2) Use skeletons directly (copy/paste)
Prefer hands‑on? Copy a skeleton and customize:

- CLI: `migration/templates/file_skeletons/cli_subcommand_skeleton.py`
- Script: `migration/templates/file_skeletons/script_skeleton.py`

Make sure you:
- Keep `--json` strictly JSON (no extra text on stdout)
- Print human‑readable output by default (concise)
- Exit 0 on success; exit 1 on failure
- Mirror parameter names/defaults across formats for parity (CLI, Scripts, Skills)

### 3) Index your scripts for quick review
If you maintain a scripts folder, index it so teammates can skim function/purpose without opening everything:

```bash
python scripts/scripts_index.py --json
python scripts/scripts_index.py --prime-prompt
python scripts/scripts_index.py --filter status
```

--------------------------------------------------------------------------------

## Planning a migration

- Single‑format migration: Migrate everything (or selected tools) to one format.
  - Example: “All read‑only tools → CLI” or “Top 5 tools → Scripts only”
  - Use and fill `migration/templates/template_per_tool_mapping.md` for each tool.

- Split/multi‑format migration: Map each tool to the best‑suited format(s).
  - Example: “All tools → CLI; subset → Scripts; smaller subset → Skills”
  - Keep parameter semantics and JSON fields identical across all included surfaces.
  - `migration/migration_plan.md` provides a decision framework and directory expectations.

--------------------------------------------------------------------------------

## User‑facing documentation checklist

Create or update the documentation your users will read (separate from dev‑only guides):

- CLI README:
  - Overview and when to use
  - Quick start (install, run examples)
  - Commands summary with flags and defaults
  - JSON mode (`--json`) examples and piping to `jq`
  - Pagination (`--limit`, `--cursor`) and any caching notes
  - Exit code semantics
  - Common workflows: monitoring, exports, watch loops
- Script index or per‑script entries:
  - One‑line “when to use”
  - Flags and defaults
  - Example commands (human and `--json`)
  - Output fields users care about most
  - Pagination and limits (if applicable)
  - Exit code semantics
- Claude Skills README:
  - Skill purpose and “when to use”
  - Trigger keywords and example prompts
  - Script list with one‑line intents
  - JSON mode recommendation and pagination notes
- Parity and testing:
  - Link to your team’s test docs or to `tests/test_validation_plan.md`
  - Explain how users can validate correct outputs or report issues

--------------------------------------------------------------------------------

## Parity, testing, and CI

Use `tests/test_validation_plan.md` to validate:

- Parity across formats (CLI vs Scripts vs MCP if still present)
- Error and exit code behavior
- Pagination (`--limit`, `--cursor`) and cursor propagation
- Caching behavior (if implemented)
- Documentation coverage and accuracy
- Optional golden snapshots for representative `--json` outputs

Suggested next steps:
- Add a small `.golden/` folder in your project for curated `--json` outputs
- Add CI to:
  - Run smoke tests for CLI and scripts
  - Validate JSON outputs and exit codes
  - Fail on regressions

--------------------------------------------------------------------------------

## Permissions and governance (for teams)

Define simple allowlists and safe defaults for agents and automation (kept in your project):

Example (YAML or JSON):
```yaml
allowed_commands:
  - status
  - markets
  - search

defaults:
  limit: 25

disallowed_flags:
  - --full  # Use only under explicit approval; can increase data volume

notes:
  - Prefer --json for automation
  - Validate pagination limits and rate limits
```

For scripts, maintain an analogous allowlist:
```yaml
allowed_scripts:
  - status.py
  - markets.py
  - search.py
defaults:
  limit: 25
```

Keep these files version‑controlled and visible for ops/security review.

--------------------------------------------------------------------------------

## Frequently asked questions

- Do I need to keep MCP after migrating?
  - Only if you still deliver MCP to clients. Many teams adopt the CLI as canonical and optionally retain MCP as a wrapper that calls the CLI via subprocess.

- Why both CLI and Scripts?
  - CLI is a great canonical JSON contract, ideal for automation and MCP wrapping. Scripts are minimal and easy to review, great for progressive disclosure and quick reuse.

- When should I add Claude Skills?
  - When you’re using Claude Code and want discoverable, autonomous activation. Skills wrap your scripts with SKILL.md to guide the model’s behavior.

- What’s the difference between skeletons and templates?
  - Skeletons are runnable code scaffolds. Templates are planning/documentation patterns you fill in to keep parity and clarity across formats.

- Where can I see a fully worked example?
  - The beyond‑mcp repository by “IndyDevDan” is a great reference showing MCP, CLI, File‑System Scripts, and Claude Skills aligned together.

--------------------------------------------------------------------------------

## References

- Migration guides (authoritative, standalone):
  - CLI: `migration/guides/guide_cli_migration.md`
  - File‑System Scripts: `migration/guides/guide_file_system_scripts_migration.md`
  - Claude Skills: `migration/guides/guide_claude_skills_migration.md`
- Migration planning:
  - `migration/migration_plan.md`
- Templates and skeletons:
  - `migration/templates/template_per_tool_mapping.md`
  - `migration/templates/file_skeletons/cli_subcommand_skeleton.py`
  - `migration/templates/file_skeletons/script_skeleton.py`
  - `migration/templates/template.agent/` (agent and command templates)
  - `migration/templates/template_ai_docs/` (ai_docs README template)
  - `migration/templates/template_file_system_scripts/` (example scripts and patterns)
- Generator:
  - `scripts/generate_cli_script.py`
- Validation plan:
  - `tests/test_validation_plan.md`

## Conventions used by .agent files

- `allowed-tools` entries like `Bash(ls*)` indicate constrained shell access (for example, only safe `ls`‑style listings), not arbitrary shell execution.
- Agent names are referenced in prompts with `@<agent-name>` (for example, `@docs-scraper` corresponds to `.agent/agents/docs-scraper.md`).
- The concrete `.agent/commands/load_ai_docs.md` command is a simplified specialization of `migration/templates/template.agent/template_commands/template_load_ai_docs.md`, assuming an `ai_docs/` folder in your project rather than this template repo.

To apply these patterns in your own project, adapt the example paths (CLI, scripts, skills, `.agent/`, and `ai_docs/`) to your existing layout and keep a per‑tool mapping and validation plan close to your code.
