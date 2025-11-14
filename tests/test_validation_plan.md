# End-to-End Test and Validation Plan

This document defines a comprehensive, repeatable plan to validate the additive migration from an MCP server to a CLI, fine‑grained file‑system scripts, and Claude Skills. It ensures parity, reliability, context efficiency, and developer ergonomics across all capability surfaces.

Attribution: This plan builds upon patterns and examples inspired by the beyond-mcp repository by IndyDevDan. It is intended as an addition, not a replacement.


## 1) Scope and Objectives

- Surfaces under test:
  - MCP Server (optionally wrapping the CLI via subprocess)
  - CLI (canonical API logic and JSON contracts)
  - File‑system scripts (self‑contained, minimal, progressive disclosure)
  - Claude Skills (autonomous discovery in Claude Code; wraps scripts)

- Objectives:
  - Guarantee behavioral parity across surfaces for each capability/tool
  - Validate strict JSON output for automation and concise human output for devs
  - Ensure stable exit codes, consistent error envelopes, and pagination semantics
  - Confirm Claude Skills are discoverable and default to JSON processing
  - Establish CI-based regression safety nets (golden outputs, schema checks)


## 2) Environments and Prerequisites

- Operating System: macOS (primary); optionally include Linux in CI
- Python: 3.10–3.12 (matrix if feasible)
- Package manager: uv or pip/venv (consistent across all runs)
- Shell: sh/bash/zsh
- Tools installed:
  - Python + uv
  - jq (for JSON introspection in examples)
  - Claude Desktop/Code (for manual skill tests, if applicable)

- Network:
  - Internet access to target APIs (or mocked endpoints for offline CI)

- Repositories:
  - Current project (this repo)
  - Reference examples (beyond-mcp by IndyDevDan) for comparison and learning


## 3) Test Data and Fixtures

- Real API (public, read-only) where possible to reduce mocking complexity
- Known stable endpoints for deterministic assertions (e.g., “status” calls)
- Param catalogs for each capability:
  - “Happy path” params (valid, typical values)
  - Edge params (min/max limits, unusual enum values)
  - Invalid params (for error validation)
- Optional: Local JSON fixtures to simulate responses when offline or rate-limited
- Caching scenarios:
  - First-run cold cache vs warm cache behavior (if caching is implemented)


## 4) Test Matrix

- Python versions: 3.10, 3.11, 3.12
- Modes: human output vs `--json` output
- CLI vs Script vs MCP (subprocess) vs Claude Skills
- Network: online (primary), optional offline/mocked for CI fallbacks
- Cache: cold vs warm (if applicable)


## 5) Parity Tests (Golden Outputs)

Goal: Confirm that MCP (if present), CLI, and Scripts produce equivalent JSON for the same capability and parameters.

- For each capability/tool:
  1. CLI: run with representative params and `--json`; save output as golden JSON
  2. Scripts: run same params with `--json`; compare JSON to CLI golden
  3. MCP: call tool; compare JSON to CLI golden

- Comparison rules:
  - Key presence and type equality are mandatory
  - Value equivalence within expected tolerances (e.g., timestamps)
  - Allow additional optional fields if documented (flag `--full` vs default)

- Example workflow (CLI vs Script):
  - uv run yourcmd status --json | jq -S . > .golden/status.cli.json
  - uv run scripts/status.py --json | jq -S . > .golden/status.script.json
  - diff .golden/status.cli.json .golden/status.script.json

- Suggested capabilities to cover initially:
  - Exchange status (deterministic)
  - A list endpoint with `--limit` and `--cursor`
  - A detail endpoint with a specific identifier
  - A search endpoint (if supported; account for caching on first run)


## 6) Error and Exit Code Tests

- Required behavior:
  - Success: exit 0
  - Failure: exit 1 (validation errors, API errors, network errors)
  - JSON error envelope when `--json` is present:
    - { "error": "<message>" }

- Test cases:
  - Missing required flag → exit 1, readable error (CLI/Scripts)
  - Invalid enum or range → exit 1, readable error
  - Network error (simulate via bad base URL) → exit 1, readable error
  - MCP: ensure subprocess non-zero maps to structured MCP error

- JSON mode discipline:
  - No stdout noise when `--json` is used (stderr for human diagnostics only)
  - Validate with: uv run yourcmd foo --json | jq . (must parse cleanly)


## 7) Pagination and Cursor Tests

- Validate:
  - Default `--limit` is applied
  - Returned `cursor` (or equivalent) is present for follow-up queries
  - Follow-up request with cursor yields next page (if available)
  - CLI and scripts produce identical pagination behavior and JSON shapes
  - MCP mirrors CLI output via its subprocess integration

- Procedure:
  - CLI: list with low limit; capture cursor; fetch next page
  - Script: repeat same two calls; compare results against CLI
  - Assert identical field presence and shape


## 8) Caching and Performance Tests (if implemented)

- Behavior to validate:
  - First run (cold cache) may be slower; subsequent runs are faster
  - TTL is respected; `--refresh` or equivalent forces refresh
  - No stale data after TTL expiration
  - Cache storage location documented (size, TTL, eviction)

- Procedure:
  - Measure wall-clock times for first and second run
  - Delete cache; confirm cold behavior again
  - If available, test `--refresh` flag


## 9) Security and Configuration Tests

- No secrets printed to stdout in `--json` mode
- If authentication is introduced later:
  - Validate env var-based configuration
  - Validate minimal required scopes
  - Failure with missing/invalid creds yields exit 1 with JSON error in `--json` mode
- Input validation:
  - Reject unexpected file paths or external URLs (if applicable)
  - Do not write to disk unless documented and intended


## 10) Claude Skills Tests

- Trigger tests:
  - Confirm that SKILL.md name/description/keywords lead to autonomous discovery
  - Prompt Claude Code with domain-relevant phrases and verify skill invocation
  - The skill should prefer running scripts with `--json`
  - Ensure instructions emphasize “call --help, not code open” for progressive disclosure

- Behavior tests:
  - Verify script outputs are compact and agent-friendly
  - Confirm that reading code is not required to learn usage (help is sufficient)
  - Evaluate that returned data is minimal and structured for follow-on reasoning


## 11) Documentation Consistency

- CLI:
  - `--help` shows complete flags, defaults, and concise examples
  - `--json` documented clearly (pure JSON, no stdout noise)
- Scripts:
  - `--help` shows complete options, concise examples
  - Emphasize self-contained, minimal design
- Skills:
  - SKILL.md includes clear “When to use” bullets and trigger hints
  - Instructs model to default to `--json` and call `--help` first
- Migration guides:
  - “Pick your path” entry points are present and correct
  - Per-tool mapping sheets are maintained and referenced


## 12) CI Plan

- Jobs:
  - Lint: ruff/flake8, black check, optional mypy
  - Unit/Integration tests: run CLI and scripts for sample scenarios
  - Golden snapshots:
    - Keep a small set of fixed, deterministic commands
    - Regenerate only when intentional changes occur
  - JSON validity:
    - Verify that `--json` outputs are valid and schema-conforming
  - Exit codes:
    - Assert exit 0 for happy paths, exit 1 for invalid inputs
- Optional:
  - Mocked tests for offline CI (use fixtures)
  - Publish test artifacts (JSON outputs) for auditing


## 13) Release and Change Management

- CLI is canonical for API logic and JSON contracts
- MCP is pinned to a compatible CLI version (if versioning introduced)
- Scripts mirror CLI semantics; remain self-contained
- Document breaking changes:
  - Changelog entries
  - `--help` epilogues
  - Update per-tool mapping sheets alongside code changes
- Compatibility matrix:
  - Track CLI versions vs MCP server compatibility if needed


## 14) Metrics and Reporting

- Key metrics:
  - Parity pass rate (CLI vs Script vs MCP)
  - JSON validity rate
  - Exit code correctness rate
  - Cache effectiveness (if applicable): cold vs warm deltas
  - Skill trigger reliability (manual inspection)
- Reporting:
  - CI summary with pass/fail per category
  - Periodic manual validation notes for Skills and Docs


## 15) Triage and Bug Workflow

- Repro steps:
  - Include exact command, flags, environment details, and outputs
- Categorize:
  - Parity regression, Error handling bug, Pagination/cursor issue, Docs inconsistency, Skill discovery issue
- Ownership:
  - CLI changes reviewed first (canonical)
  - Scripts mirror fixes next
  - MCP updated last (if wrapping CLI)
  - Skills updated if instructions or script paths change
- Golden updates:
  - Only update golden JSON when changes are intended and documented


## 16) Acceptance Criteria (Per Capability)

- Parity:
  - CLI and Scripts produce equivalent JSON in `--json` mode
  - MCP (if present) matches CLI JSON for the same params
- Reliability:
  - Correct exit codes (0 success, 1 failure)
  - JSON error envelope under `--json` on failure
- Usability:
  - `--help` shows accurate flags and examples
  - Skill invokes scripts autonomously and defaults to `--json`
- Documentation:
  - Mapping sheet complete and up-to-date
  - Links in README and guides are discoverable and correct
- Optional:
  - Caching behavior observed and documented (where applicable)


## 17) Example Commands

- CLI (JSON mode):
  - uv run yourcmd status --json | jq .
  - uv run yourcmd markets --limit 5 --json | jq '.items | length'
- Scripts (JSON mode):
  - uv run scripts/status.py --json | jq .
  - uv run scripts/markets.py --limit 5 --json | jq '.items | length'
- Error handling:
  - uv run yourcmd markets --limit -1 --json | jq .
  - uv run scripts/markets.py --limit -1 --json | jq .
- Pagination:
  - uv run yourcmd markets --limit 2 --json | tee page1.json
  - uv run yourcmd markets --limit 2 --cursor "$(jq -r .cursor page1.json)" --json | jq .
- Claude Skills (manual):
  - Prompt Claude Code: “What’s the exchange status?”, “Search markets for ‘xyz’”
  - Verify skill invocation and `--json` usage


## 18) Optional Golden Test Harness

- Script to:
  - Run a curated set of commands (CLI/scripts)
  - Normalize with jq -S
  - Diff against committed goldens under .golden/
  - Exit non-zero on mismatch
- Update goldens only after intentional changes and documentation updates


## 19) Risks and Mitigations

- Live API drift:
  - Prefer deterministic endpoints for goldens; allow relaxed matching on volatile fields
- Rate limits:
  - Throttle tests; mock when required in CI
- Caching flakiness:
  - Separate caching tests; assert behavior, not exact timestamps
- Skill discovery variance:
  - Keep triggers high-signal and specific; document prompts used for validation


## 20) Final Notes

- Treat the CLI as the single source of truth for remote I/O behavior and JSON contracts.
- Keep scripts self-contained and minimal to preserve progressive disclosure and reduce context cost.
- Use Claude Skills as an additive, discoverable layer over scripts.
- Maintain per-tool mapping sheets to prevent drift and simplify onboarding.
- This plan is designed to be extended as capabilities grow.
