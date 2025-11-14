# MCP → Claude Skills Migration Guide (Authoritative, Standalone)
Note: For a comprehensive test plan, see migration_guide/test_validation_plan.md

Purpose
- Provide a clean, precise process for migrating an MCP server to Claude Skills.
- Make skills discoverable by Claude Code, with autonomous activation and low context usage.
- Keep parameter semantics and JSON contracts identical to any existing CLI or File‑System Script surfaces.

This guide stands alone. If you also ship a CLI or File‑System Scripts, keep overlapping conventions (flags, JSON shape, exit codes) identical across all surfaces for parity.


## 1) When to choose Claude Skills

Choose Claude Skills when you need:
- Autonomous discovery and activation by Claude Code with zero server setup.
- Progressive disclosure (Claude reads only SKILL.md and command help, then runs the script).
- Git-shareable capabilities for a team (committed under project version control).
- Minimal operational burden (no MCP server process to run).

Keep MCP and/or CLI if:
- You have clients requiring MCP transport or streaming.
- You want a canonical place for remote I/O logic and JSON contracts (CLI), with Skills as a discoverable UX layer over scripts.


## 2) Migration strategies

Pick one per project (you can mix as needed per capability).

A) Single‑format migration (Skills only)
- Goal: Expose selected MCP tools as Claude Skills with self‑contained scripts.
- Outcome: A set of skills under `.claude/skills/` that Claude can auto‑detect and invoke.

B) Split / Multi‑format migration (Skills + others)
- Goal: Provide Skills as a discoverable layer over self‑contained scripts and retain a CLI as the canonical JSON contract. MCP may wrap CLI if needed.
- Outcome: Per‑tool matrix mapping which capabilities become Skills (usually most read‑only, self‑contained operations).

Tool mapping guidance:
- Inventory MCP tools with parameters, outputs, and intents.
- For each tool, decide:
  - Should it be discoverable as a Skill? (user-facing, frequent, read‑heavy tasks are great candidates)
  - Which script(s) should the Skill run?
- Maintain identical parameter semantics and JSON fields across CLI/Scripts/Skills to preserve parity.


## 3) Skill design standards

- Directory layout:
  - `.claude/skills/<skill-name>/SKILL.md`
  - `.claude/skills/<skill-name>/scripts/*.py` (self‑contained, one file per capability)
- SKILL.md:
  - Clear name and description (front matter).
  - Instructions emphasizing:
    - Prefer `--json` for processing.
    - Call `<script>.py --help` to learn usage; only read code when strictly needed.
  - “When to use” bullets aligned to user phrasing.
  - Trigger keywords (high-signal terms Claude can detect).
- Scripts:
  - Self‑contained (no repo‑global imports ideally).
  - Flags mirror MCP/CLI semantics (required/optional/defaults/ranges).
  - `--json` prints strict JSON on stdout (no extra text).
  - Exit codes: 0 success; 1 failure; JSON error envelope `{ "error": "<message>" }` in JSON mode.
  - Keep each script ~200–300 lines for easy review and minimal context.

Minimal directory preview:
```/dev/null/tree.txt#L1-14
.claude/
  skills/
    your-skill-name/
      SKILL.md
      scripts/
        status.py
        markets.py
        search.py
        # ... additional one-file scripts (each self-contained)
```


## 4) Implementation steps

1) Plan your skill(s)
- Choose a meaningful `<skill-name>` (e.g., `kalshi-markets`).
- Map one or more scripts to the skill (each script = one capability).
- Define trigger keywords and “When to use” bullets that reflect real user language.

2) Author scripts
- One file per capability, self‑contained, with `--help` and `--json`.
- Flags: identical names/defaults to MCP/CLI. Validate early with helpful errors.
- Output: concise human mode; strict JSON in `--json` mode; exit 0/1 consistently.

3) Write SKILL.md
- Name/description front matter.
- Clear instructions: “use `--json`”, “call `--help` before reading code”.
- “Available Scripts” list with “When to use” one‑liners per script.
- Triggers: keywords Claude can detect to auto‑activate the skill.

4) Validate locally
- Run scripts directly:
  - `uv run .claude/skills/<skill-name>/scripts/<script>.py --help`
  - `uv run .claude/skills/<skill-name>/scripts/<script>.py --json`
- Confirm identical semantics vs CLI/MCP:
  - Same flags, defaults, and pagination behavior.
  - Same JSON fields for the same inputs.

5) Test with Claude Code
- Open Claude Code in the project root.
- Prompt with phrases that should trigger the skill (see triggers).
- Confirm the skill calls scripts with `--json` and avoids reading code unless needed.
- Inspect results and iterate on SKILL.md for clarity and precision.


## 5) Parity and validation

- Compare script JSON outputs to CLI/MCP for representative inputs (golden tests recommended).
- Validate error and exit-code behavior:
  - Missing required flag → exit 1; JSON error envelope in `--json` mode.
  - Invalid enum/range → exit 1; helpful error.
  - Network/API error → exit 1; JSON error envelope.
- Pagination and cursoring:
  - `--limit` and `--cursor` flags present and behave identically to CLI/MCP.
  - Return the same cursor fields in JSON.

Caching (optional)
- If scripts include caching for expensive operations:
  - Document TTL and refresh behavior (e.g., a `--refresh` flag).
  - Validate first-run (cold) vs subsequent runs (warm) latency.


## 6) Distribution and usage

- Commit the `.claude/skills/<skill-name>/` folder to your repository for team-wide usage.
- Claude Code will auto-detect and offer to use the skill based on triggers and context.
- You can also run scripts directly via `uv run` for manual workflows or debugging.

Examples (run directly):
```/dev/null/bash.txt#L1-6
# Learn usage
uv run .claude/skills/your-skill-name/scripts/status.py --help

# Machine-friendly output
uv run .claude/skills/your-skill-name/scripts/status.py --json | jq .
```


## 7) User-facing documentation and agent permissions

Author a concise Skill README (separate from this migration guide):
- Purpose and “When to use” summary.
- Trigger keywords and example prompts.
- Script list with one-line intent each.
- Quick start (how Claude auto-detects and uses the skill).
- JSON mode recommendation and examples.
- Notes on pagination (`--limit`, `--cursor`), caching (if any), and error/exit codes.

Agent permissions and policy
- Provide an allowlist and safe defaults (for ops/security):
```/dev/null/permissions.yaml#L1-20
allowed_scripts:
  - status.py
  - markets.py
  - search.py

defaults:
  limit: 25

disallowed_flags:
  - --full  # use only when explicitly approved

notes:
  - Prefer --json for processing
  - Call --help to discover options; avoid reading code unless necessary
```
- Clarify data volumes, rate limits, and any environment prerequisites (e.g., network access, proxies).
- Keep the allowlist and defaults version-controlled alongside SKILL.md.


## 8) Security and compliance

- No secrets in stdout for `--json` mode; stderr only for human diagnostics.
- Prefer environment variables or secure stores for any credentials (if later introduced).
- Validate and whitelist endpoints; do not accept arbitrary URLs unless explicitly intended and documented.
- Keep scripts read‑only unless explicitly adding safe write functionality (document and require explicit flags).
- Enforce timeouts; consider retries/backoff for transient failures.


## 9) Versioning and change management

- Skills and scripts are versioned via your repository.
- Keep parameter semantics stable; document breaking changes in a CHANGELOG and in SKILL.md notes.
- Maintain per‑tool mapping sheets to prevent drift across CLI/Scripts/Skills.
- When scripts or JSON fields change, update SKILL.md and any user-facing docs accordingly.


## 10) Minimal SKILL.md template

A concise template you can copy and adjust.

```/dev/null/SKILL.md#L1-120
---
name: your-skill-name
description: Short, actionable description. Include nouns/verbs likely to appear in user prompts.
---

# Your Skill Name

Self-contained scripts for <your domain>. Each script is independently executable with zero shared dependencies.

## Instructions
- Default to `--json` for all commands when processing data.
- Prefer `<script>.py --help` to discover options; only read code when necessary.
- Use the smallest sufficient command and limit results to reduce context.

## Triggers
- "keyword 1"
- "keyword 2"
- "domain term"

## Available Scripts

### scripts/foo.py
When to use: <single-line intent>

### scripts/bar.py
When to use: <single-line intent>
```

Directory scaffolding (example):
```/dev/null/tree.txt#L1-12
.claude/
  skills/
    your-skill-name/
      SKILL.md
      scripts/
        foo.py
        bar.py
```


## 11) Checklist (copy/paste)

Planning
- [ ] Inventory MCP tools and decide which become Skills.
- [ ] Create per‑tool mapping sheets (inputs, outputs, errors, pagination).
- [ ] Choose triggers and “When to use” phrasing aligned to real prompts.

Design
- [ ] One skill per domain/topic with clear scripts per capability.
- [ ] Scripts self‑contained; flags mirror MCP/CLI; identical defaults/validations.
- [ ] `--json` strict output; human output concise.
- [ ] Exit codes: 0 success; 1 failure; JSON error envelope for errors in JSON mode.
- [ ] Pagination/cursor behavior matches CLI/MCP.

Implementation
- [ ] Write SKILL.md with name, description, triggers, instructions, and script list.
- [ ] Implement scripts with `click` + `httpx` (or equivalents).
- [ ] No stdout noise in `--json` mode; errors → stderr in human mode.

Validation
- [ ] Parity vs CLI/MCP JSON outputs for representative inputs.
- [ ] Error/exit code tests (missing flags, invalid ranges, network errors).
- [ ] Pagination flow verified.
- [ ] Test skill triggers in Claude Code; confirm it defaults to `--json` and avoids reading code unless needed.

Docs and Ops
- [ ] User-facing Skill README: triggers, when-to-use, examples, JSON usage.
- [ ] Agent allowlist/defaults documented (permissions file).
- [ ] CHANGELOG updated; mapping sheets committed.

Release
- [ ] Commit `.claude/skills/<skill-name>/` folder.
- [ ] Communicate new/updated Skills and any breaking changes.


## 12) References

- beyond‑mcp (owner/creator: IndyDevDan): a practical repository that demonstrates complementary surfaces (MCP, CLI, File‑System Scripts, Claude Skills). Use it as a reference for parity and progressive disclosure patterns. This guide is additive and focuses on the Claude Skills format specifically.