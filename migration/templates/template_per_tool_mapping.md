# Per-Tool Mapping Template

A reusable mapping sheet to keep strict parity across MCP → CLI → File‑System Scripts → Claude Skills.

This template is intended to be copied and filled out once per capability. It helps teams maintain consistent parameters, outputs, error handling, and documentation across all surfaces.

Attribution: The patterns used here build upon the excellent examples in the beyond-mcp repository by IndyDevDan. Use this as an addition, not a replacement.


## How to use this template

1) Copy the “Template” section below into a new file for your tool (for example: migration/tool_mappings/<tool_name>.md).
2) Fill in each field precisely. Keep semantics identical across MCP, CLI, scripts, and skills.
3) Validate by running golden outputs across surfaces and updating this sheet when behavior changes.
4) Keep this sheet close to code changes. It becomes your source of truth for parity.

Tip: Treat your CLI as canonical for remote I/O and JSON output. Have your MCP server wrap the CLI (subprocess + JSON parse), and keep scripts self‑contained and minimal. Claude Skills should wrap the scripts and provide discovery/activation for Claude Code.


---

## Template (copy from here)

Title
- Tool: <tool_name> — <one-line summary>

MCP Tool
- Name: <mcp_tool_name>
- Purpose: <single-line intent expressed in user language>
- Inputs:
  - <param>: <type> (required=<true|false>, default=<value>) — <description>
  - <param>: <type> (required=<true|false>, default=<value>) — <description>
- Output (JSON schema summary):
  - <field>: <type> — <meaning>
  - <field>: <type> — <meaning>
- Notes:
  - Pagination/Cursor: <yes|no>, <mechanics>
  - Caching: <yes|no>, <TTL/strategy>
  - Auth: <none|api key|oauth>, scope=<...>
  - Rate limits: <numbers/strategy>
  - Constraints: <e.g., max limits, enum values>

CLI Command (canonical API logic and JSON contract)
- Binary: <binary_name>
- Subcommand: <subcommand_name>
- Flags (mapping to MCP params):
  - --<flag> <type> (default=<value>) → maps to <param>
  - --<flag> <type> (default=<value>) → maps to <param>
- Output modes:
  - --json: pure JSON on stdout (no logs)
  - default: concise human-readable
- Exit codes:
  - 0: success (define “success” precisely)
  - 1: failure (validation failure, API error, etc.)
- Examples:
  - <binary_name> <subcommand> --flag value --json
  - <binary_name> <subcommand> --flag value | jq '.items[] | {id, name}'

File‑System Script (self‑contained, minimal)
- Filename: scripts/<script_name>.py
- Options (mapping to MCP params):
  - --<option> → <param>, default=<value>
  - --json for pure JSON output
- Behavior:
  - Self‑contained client; no shared project imports if possible
  - Human output by default; machine output with --json
  - Non‑zero exit on failure
- Notes:
  - Keep ~200–300 lines when possible; prefer progressive disclosure via --help
  - Avoid stdout noise in --json mode

Claude Skill (autonomous discovery in Claude Code)
- Skill folder: .claude/skills/<skill-name>/
- Script: .claude/skills/<skill-name>/scripts/<script_name>.py
- SKILL.md entry:
  - name: <skill-name>
  - description: <when Claude should invoke this>
  - instructions: default to --json; call --help before reading code
- Triggers (keywords/phrases the model will recognize):
  - "<keyword1>", "<keyword2>", "<domain term>"
- “When to use” bullet (end‑user phrasing):
  - Use when the user asks for <task/intention>

Parity and Semantics
- Parameter names, defaults, and value ranges are identical across surfaces
- Output fields and meaning are identical (minor formatting differences allowed)
- Pagination/cursor behavior is identical
- Error conditions and exit codes are defined and consistent

Error Handling
- CLI and scripts: exit 0 on success; exit 1 on failure
- JSON error envelope when --json is used: { "error": "<message>" }
- Avoid printing logs to stdout during --json; use stderr for human diagnostics

Caching (optional)
- Cache scope: <command or script>
- TTL: <duration>
- Storage: <path/mechanism>
- Invalidation/refresh logic: <strategy>
- User-facing flags: --refresh, --ttl, etc.

Security
- Auth required: <none|api key|oauth>
- Storage of secrets: <env vars|keychain|none>
- Data sensitivity: <low|medium|high>
- Additional constraints: <whitelists, allowed endpoints>

Testing Checklist
- Golden outputs (CLI vs script vs MCP) produce identical JSON for known inputs
- Error/edge cases covered (bad params, not found, network fail)
- Exit codes validated
- Skill trigger smoke-tested with representative prompts

Change Management
- Versioning:
  - CLI: <semver guidance>
  - MCP: <compatibility with CLI version>
  - Scripts: <tracked via repo tags>
- Breaking changes documented in CHANGELOG and --help epilogues
- Mapping sheet updated alongside code changes


---

## Example (based on beyond-mcp by IndyDevDan)

Title
- Tool: get_exchange_status — Current Kalshi exchange/trading status

MCP Tool
- Name: get_exchange_status
- Purpose: Check if the Kalshi exchange and trading are currently active
- Inputs:
  - none
- Output (JSON schema summary):
  - exchange_active: boolean — whether exchange is up
  - trading_active: boolean — whether trading is enabled
  - exchange_estimated_resume_time: string (optional) — when trading/exchange may resume
- Notes:
  - Pagination/Cursor: no
  - Caching: no
  - Auth: none (public read-only)
  - Rate limits: standard public API limits
  - Constraints: none

CLI Command (canonical)
- Binary: kalshi
- Subcommand: status
- Flags:
  - --json (pure JSON on stdout)
- Output modes:
  - --json: { "exchange_active": true|false, "trading_active": true|false, "exchange_estimated_resume_time": "<iso8601 or null>" }
  - default: concise human-readable status lines
- Exit codes:
  - 0: success; additionally, returns 0 if trading_active is true (OK) and 1 if inactive (can be used for monitoring)
  - 1: failure (HTTP error, parse error, network issue)
- Examples:
  - uv run kalshi status --json
  - uv run kalshi status

File‑System Script
- Filename: scripts/status.py
- Options:
  - --json
- Behavior:
  - Self‑contained httpx client to Kalshi public API
  - Prints JSON in --json mode; prints formatted human output otherwise
  - Exit 0 if trading_active true; exit 1 otherwise (and on errors)
- Notes:
  - Document that no auth is required

Claude Skill
- Skill folder: .claude/skills/kalshi-markets/
- Script: .claude/skills/kalshi-markets/scripts/status.py
- SKILL.md entry:
  - name: kalshi-markets
  - description: Access Kalshi prediction market data including market prices, orderbooks, trades, events, and series information. Use when the user asks about prediction markets, Kalshi markets, betting odds, market prices, or needs to search or analyze prediction market data.
  - instructions: Default to --json; call <script>.py --help to discover options; only read code if necessary.
- Triggers:
  - "prediction markets", "Kalshi markets", "exchange status", "betting odds", "market status"
- “When to use” bullet:
  - Use when the user asks whether the Kalshi exchange is currently active or if trading is enabled

Parity and Semantics
- All surfaces return the same fields: exchange_active, trading_active, exchange_estimated_resume_time
- No pagination; no auth
- Exit codes: CLI/script exit 0 on success and when trading_active true; 1 when inactive or on error
- MCP wraps CLI via subprocess and returns parsed JSON or structured error

Error Handling
- CLI and script:
  - On error in --json mode, print: { "error": "<message>" } and exit 1
  - On human mode, print concise message to stderr and exit 1
- MCP:
  - Convert non-zero CLI exit to a structured MCP tool error with message

Caching
- Not applicable (simple status endpoint)

Security
- Public, read-only endpoint; no secrets; low data sensitivity

Testing Checklist
- Compare CLI vs script vs MCP JSON for a sample call
- Simulate downtime scenarios if possible (mock) to validate exit code 1 and error messages
- Validate no stdout noise in --json mode

Change Management
- Versioning:
  - CLI: maintain semver; any field additions documented
  - MCP: pin compatible CLI version for subprocess calls
  - Scripts: track via repo tags/releases
- Document any changes in CHANGELOG and in --help epilogues
- Update this mapping sheet with every change


---

## Tips for high-fidelity mappings

- Keep parameter names and defaults identical; use the same enums and ranges everywhere.
- Prefer small, structured outputs; add an optional flag (e.g., --full) for verbose payloads.
- Ensure that error envelopes are stable and machine-readable in JSON mode.
- Avoid logging to stdout when --json is present; reserve stdout for JSON only.
- Validate parity with golden tests and CI so MCP, CLI, and scripts never drift.
