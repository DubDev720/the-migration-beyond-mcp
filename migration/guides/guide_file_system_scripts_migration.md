# MCP → File‑System Scripts Migration Guide (Authoritative, Standalone)
Note: For a comprehensive test plan, see tests/test_validation_plan.md

Purpose
- Provide a precise, end‑to‑end process for migrating an MCP server to a suite of self‑contained, one‑file scripts.
- Optimize for progressive disclosure, minimal context footprint, and easy review/modification by users and teams.
- Keep parameter semantics and JSON contracts consistent with any existing CLI or MCP server to ensure parity.

This guide stands alone. If you also ship a CLI or Claude Skills, keep overlapping conventions (flags, JSON shape, exit codes) identical across all surfaces for parity.

---

1) When to choose File‑System Scripts
Choose File‑System Scripts when you need:
- Progressive disclosure and minimal context usage (agents read just a script’s help or run it with flags).
- Self‑contained, portable capabilities that can be reviewed, audited, and versioned easily.
- Zero shared runtime and low coupling between capabilities (one responsibility per file).
- Easy “drop-in” usage: copy a file or folder to reuse a capability instantly.

Keep MCP and/or CLI if:
- You have clients expecting MCP transport and tool catalogs, or need streaming.
- You want a canonical place for remote I/O logic and JSON contracts (CLI), with scripts as a lightweight companion.

---

2) Migration strategies
Pick one per project or mix as needed per capability.

A) Single‑format migration (Scripts only)
- Goal: Migrate all or selected MCP tools into standalone scripts.
- Outcome: A minimal, auditable folder of scripts with consistent flags and JSON output.

B) Split / Multi‑format migration (Scripts + others)
- Goal: Migrate some tools to scripts (for minimal context), keep CLI for canonical I/O, and optionally add Claude Skills for autonomous discovery.
- Outcome: A per‑tool matrix specifying which surfaces each capability targets, while maintaining identical parameter semantics and JSON across surfaces.

Tool mapping guidance (works for both):
- List each MCP tool with its parameters and outputs.
- Decide if a tool should exist as a script (usually “yes” for read‑only, single‑purpose operations).
- Maintain identical flags, defaults, and JSON fields across MCP/CLI/scripts to preserve parity.

---

3) Planning and inventory
Create a per‑tool mapping sheet (one per capability):
- Intent (1–2 lines in user language).
- Inputs: name, type, required, default; validations and enums.
- Output: JSON schema summary (key fields; pagination/cursor behavior).
- Error semantics: when to exit non‑zero; JSON error envelope shape.
- Auth and rate limits (if any).
- Notes: caching, volatility, size limits.

This becomes the source of truth for consistent behavior across all surfaces.

---

4) Script design standards
- One file per capability; no shared project imports if possible.
- Support --help (concise, example usage) and --json (strict JSON, no stdout noise).
- Exit codes: 0 success; 1 failure (validation, API/network error).
- Error envelope under --json: {"error": "<message>"}.
- Human output: short, stable summaries; use JSON for machines and agents.
- Parameter names/defaults: identical to MCP/CLI (e.g., --limit, --cursor, --series-ticker).
- Pagination/cursor: provide the same flags and return the same fields as other surfaces.
- Read‑only by default; no writes to disk unless explicitly documented.
- Progressive disclosure: consumers should learn usage from --help without opening the code.
- Size target: ~200–300 lines per script (pragmatic; small enough for review and agent context).
- Naming: scripts/<capability>.py with docstring describing what, when, and how.

---

5) Implementation steps
1. Scaffold a scripts/ folder
   - Place one script per capability (e.g., scripts/status.py, scripts/markets.py).

2. Add a minimal HTTP client per script
   - Base URL, timeout, headers (User‑Agent).
   - Return data or raise exceptions; do not print from the client.

3. Parse options with click
   - Flags mirror MCP/CLI: required/optional, defaults, ranges.
   - Validate early; provide helpful errors.

4. Produce output
   - --json: strict JSON on stdout; no logs or extra text.
   - Default: concise human output; keep lines short and stable.
   - Exit 0 on success, 1 on failure.

5. Handle errors consistently
   - httpx HTTPStatusError → {"error": "HTTP error: <code> - <text>"} (in JSON mode).
   - httpx RequestError → {"error": "Network error: <message>"} (in JSON mode).
   - Other exceptions → {"error": "Unexpected error: <message>"} (in JSON mode).
   - Human mode prints concise errors to stderr.

6. Validate parity and semantics
   - Compare script JSON outputs to CLI/MCP for the same inputs.
   - Keep pagination and cursor behavior identical.

7. Optional: Caching
   - If expensive, read‑heavy operations benefit, add a small on‑disk cache with TTL.
   - Document location, TTL, and refresh behavior; never cache secrets.

---

6) Parity and validation
- Compare JSON outputs between script, CLI, and MCP for representative inputs.
- Validate error/exit code behavior:
  - Missing required flags → exit 1, helpful error.
  - Invalid enums/ranges → exit 1, helpful error.
  - Network/API failures → exit 1 with JSON error envelope in --json mode.
- Pagination: verify --limit and --cursor handling matches other surfaces.
- Caching (if implemented): verify cold vs warm performance; TTL/refresh works as documented.

---

7) Distribution and usage
- Run via uv or python directly:
  - uv run scripts/<capability>.py --help
  - uv run scripts/<capability>.py --json
- Make scripts portable:
  - Self‑contained; no repo‑global imports.
  - Document external dependencies in the script header or via script metadata comments.
- Integrate optionally into MCP or Claude Skills:
  - MCP can wrap scripts (less common) or more appropriately wrap the CLI.
  - Claude Skills can point to scripts for autonomous discovery.

---

8) User‑facing documentation (separate from this guide)
Author a per‑script README entry or index page users can skim quickly:
- Title and “When to use” (1–2 sentences).
- Quick start and flags with defaults.
- Example invocations (human and --json).
- JSON schema overview (fields most users care about).
- Pagination and limits (if applicable).
- Caching notes (if implemented).
- Exit code semantics.
- Change notes and version/date.
- Attribution (if referencing or inspired by beyond‑mcp by IndyDevDan).

Agent permissions and ops notes:
- Provide an allowlist with scripts and safe defaults:
  - allowed_scripts: ["status.py", "markets.py", "search.py"]
  - defaults: {"limit": 25}
  - disallowed_flags: ["--full"] (if too verbose)
- Document environment needs (e.g., read‑only network access, rate limits).
- Encourage agents to use --json and consult --help before opening code.

---

9) Security and compliance
- Prefer read‑only operations; if writes are needed, document precisely and require explicit flags.
- No secrets in stdout for --json; stderr only for diagnostics.
- Prefer env vars for any credentials (if later introduced); avoid writing secrets to disk.
- Validate/whitelist endpoints; do not accept arbitrary URLs unless intended.
- Enforce timeouts; consider backoff/retries for transient failures.

---

10) Versioning and change management
- Scripts live in source control; treat them as versioned assets.
- Keep parameter semantics stable; document breaking changes in a CHANGELOG and in script help epilogues.
- Maintain per‑tool mapping sheets alongside code changes.
- If scripts mirror a CLI, update scripts after CLI schema/flag changes to preserve parity.

---

11) Minimal script template (pattern)
A concise, self‑contained pattern. Replace endpoint/params with your own. Keep semantics consistent with your MCP/CLI.

    #!/usr/bin/env python3
    # /// script
    # dependencies = [
    #     "httpx",
    #     "click",
    # ]
    # ///
    """
    <Capability Name> Script

    When to use: <one‑line intent in user language>

    Usage:
      uv run scripts/<capability>.py --help
      uv run scripts/<capability>.py --json
    """

    import json
    import sys
    from typing import Any, Dict, Optional

    import click
    import httpx

    API_BASE_URL = "https://api.example.com/v1"
    API_TIMEOUT = 30.0
    USER_AGENT = "<Your-Script>/1.0"

    class Client:
        def __init__(self):
            self.client = httpx.Client(
                base_url=API_BASE_URL,
                timeout=API_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )

        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): self.client.close()

        # Replace params and path with your real call
        def fetch(self, limit: int, cursor: Optional[str]) -> Dict[str, Any]:
            r = self.client.get("/items", params={"limit": limit, "cursor": cursor})
            r.raise_for_status()
            return r.json()

    def format_human(data: Dict[str, Any]) -> str:
        items = data.get("items", [])
        lines = []
        lines.append("<Capability Name> Results")
        lines.append("=" * 40)
        lines.append(f"items: {len(items)}")
        if "cursor" in data:
            lines.append(f"next_cursor: {data['cursor']}")
        return "\n".join(lines)

    @click.command()
    @click.option("--limit", default=10, show_default=True, type=click.IntRange(min=1), help="Max items to return")
    @click.option("--cursor", default=None, type=str, help="Pagination cursor")
    @click.option("--json", "output_json", is_flag=True, help="Emit strict JSON on stdout (no extra text)")
    def main(limit: int, cursor: Optional[str], output_json: bool):
        try:
            with Client() as c:
                data = c.fetch(limit=limit, cursor=cursor)

            if output_json:
                # Strict JSON only on stdout in JSON mode
                click.echo(json.dumps(data))
            else:
                click.echo(format_human(data))

            sys.exit(0)

        except httpx.HTTPStatusError as e:
            msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            if output_json:
                click.echo(json.dumps({"error": msg}))
            else:
                click.echo(f"❌ Error: {msg}", err=True)
            sys.exit(1)

        except httpx.RequestError as e:
            msg = f"Network error: {str(e)}"
            if output_json:
                click.echo(json.dumps({"error": msg}))
            else:
                click.echo(f"❌ Error: {msg}", err=True)
            sys.exit(1)

        except Exception as e:
            msg = f"Unexpected error: {str(e)}"
            if output_json:
                click.echo(json.dumps({"error": msg}))
            else:
                click.echo(f"❌ Error: {msg}", err=True)
            sys.exit(1)

    if __name__ == "__main__":
        main()

Key points illustrated:
- --help and --json supported.
- JSON mode prints only JSON to stdout; errors as JSON envelope.
- Exit 0 on success; 1 on failure.
- Pagination flags and fields are consistent.
- No shared project imports—self‑contained.

---

12) Checklist (copy/paste)
Planning
- [ ] Inventory all MCP tools; decide single‑format vs multi‑format plan
- [ ] Create per‑tool mapping sheets (inputs, outputs, errors, pagination)

Design
- [ ] One file per capability; self‑contained; minimal HTTP client
- [ ] Flags mirror MCP/CLI; identical defaults and validations
- [ ] --json strict output; human output concise
- [ ] Exit codes: 0 success; 1 failure
- [ ] Pagination/cursor semantics consistent
- [ ] Progressive disclosure: learn via --help

Implementation
- [ ] Implement script with click + httpx
- [ ] No stdout noise in JSON mode; errors → stderr in human mode
- [ ] Optional caching documented (path, TTL, refresh)

Validation
- [ ] Parity vs CLI/MCP JSON outputs
- [ ] Error/exit code tests (missing flags, invalid ranges, network)
- [ ] Pagination flow verified
- [ ] Golden outputs for representative calls (optional)

Docs and Ops
- [ ] Per‑script README entries: when to use, flags, examples, JSON schema
- [ ] Agent allowlist and defaults documented
- [ ] CHANGELOG updated; mapping sheets committed

Release
- [ ] Scripts organized under scripts/ with clear names
- [ ] Communicate changes; maintain stability

---

13) References
- beyond‑mcp (owner/creator: IndyDevDan): demonstrates a complementary set of surfaces (MCP, CLI, File‑System Scripts, Claude Skills). Use it as a reference for parity and progressive disclosure patterns. This guide is additive and focuses on the File‑System Scripts format specifically.
