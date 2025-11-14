# MCP → CLI Migration Guide (Authoritative, Standalone)

Purpose
- Provide a precise, end-to-end process for migrating an MCP server to a robust CLI with clean JSON output and consistent contracts.
- Keep the CLI as the canonical API/contract layer. MCP can wrap the CLI via subprocess for compatibility.

This guide stands alone. If you are also targeting File-System Scripts or Claude Skills, keep overlapping conventions (flags, JSON, exit codes) identical across all surfaces for parity.


## 1) When to choose a CLI

Choose a CLI when you need:
- Portability across shells, CI/CD, containers, and development environments.
- A single source of truth for HTTP calls, retries, pagination, caching, and JSON contracts.
- A surface that MCP can wrap via subprocess without duplicating remote I/O code.
- Easy automation and composition with other tools (pipeable `--json`).

Keep MCP if:
- You have clients expecting MCP transport or streaming behaviors.
- You are shipping MCP already and want an additive path forward (MCP wraps CLI).


## 2) Migration strategies

Two supported strategies. Pick one per project, but you can mix as needed.

A) Single-format migration (CLI only)
- Goal: Migrate all or selected functionality from MCP to CLI.
- Outcome: A consistent, portable CLI that is the canonical contract for all consumers (including MCP).

B) Split / Multi-format migration (CLI plus others)
- Goal: Migrate specific tools to the best-suited formats (e.g., bulk/data ops in CLI, lightweight tasks as File-System Scripts, autonomous discovery via Claude Skills).
- Outcome: A matrix mapping—per tool—of which targets it goes to, while the CLI remains canonical for remote I/O.

Tool mapping guidance (works for both strategies):
- Start by listing all MCP tools with parameters and outputs.
- For each tool, decide:
  - Should it exist as a CLI subcommand? (Usually “yes”—this is your canonical layer)
  - Will it also be offered as a File-System Script? (Prefer for minimal context and progressive disclosure)
  - Will it be exposed as a Claude Skill? (Prefer for discovery/activation by Claude Code)
- Keep parameter semantics identical across all chosen surfaces.


## 3) Planning and inventory

Create a per-tool mapping sheet (one per capability):
- Tool intent (1–2 lines in user language)
- Inputs (name, type, required, default)
- Output schema summary (key fields, pagination/cursor behavior)
- Error semantics (when non-zero exit)
- Auth and rate limits (if any)
- Notes (caching semantics, volatility, size limits)

This sheet becomes your source of truth for consistent behavior across CLI and any additional surfaces.


## 4) CLI design standards

Follow these conventions for a high-quality, automatable CLI.

Naming and structure
- Binary name: short and thematic (e.g., `kalshi`, `yourcmd`).
- Subcommands: mirror domain nouns/verbs (e.g., `status`, `markets`, `market`, `search`).
- File structure: simple and explicit. Example:

  ```
  apps/2_cli/
  ├── pyproject.toml
  └── your_cli/
      ├── __init__.py
      ├── cli.py          # registers all subcommands
      └── modules/
          ├── client.py   # shared HTTP client, retries, caching (optional)
          ├── formatters.py
          └── constants.py
  ```

Flags and parameters
- Use flags for all inputs (avoid positional unless clearly beneficial).
- Preserve MCP parameter names and semantics (e.g., `--limit`, `--cursor`, `--series-ticker`).
- Support enums and ranges; validate early with clear errors.

Output modes
- Default mode: concise human-readable output (short, stable, no verbose logs).
- Machine mode: `--json` flag prints strict JSON on stdout with no extra text.
  - All logs/errors go to stderr in `--json` mode.
  - If an error occurs in `--json` mode, print a simple envelope:
    - `{ "error": "<message>" }`

Exit codes
- 0 on success.
- 1 on failure (validation, network, API error).
- Do not invent more exit codes unless you have a strong operational need.

Pagination and cursoring
- Provide `--limit` and `--cursor` flags where the API supports them.
- Return cursor fields in JSON consistently.
- Document pagination semantics in `--help`.

Auth and configuration (if needed)
- Prefer environment variables for secrets; never print secrets in `--json` mode.
- Fail with clear error if required auth is missing.

Caching (optional)
- If an endpoint benefits from caching (e.g., heavy search), implement it at the CLI layer.
- Document TTL and `--refresh` behavior in `--help`.
- Never cache sensitive data unless clearly documented and safe.

Performance and context hygiene
- Default payloads should be compact. Add `--full` to opt-in for large/verbose objects.
- Keep human-readable output short; machines should use `--json` for full data.

Help and usage
- `--help` must list flags, defaults, and examples for both human and `--json` modes.
- Provide usage examples that show pipes to `jq` and file redirection.


## 5) Implementation steps

1. Scaffold the CLI project
   - Create `pyproject.toml` (or `uv` metadata) with dependencies: `click`, `httpx`, optional `rich`/`tabulate` for human output.
   - Define an entry point (console script) that invokes your `cli()` function.

2. Implement the HTTP client
   - Base URL, timeout, headers (User-Agent), optional retries/backoff.
   - No printing in the client; return data or raise exceptions.

3. Implement subcommands (1:1 with MCP tools)
   - Each subcommand:
     - Defines flags mirroring MCP parameters.
     - Calls the client and handles responses.
     - Prints JSON on `--json`, human output otherwise.
     - Exits 0 on success, 1 on failure; JSON error envelope in `--json` mode.

4. Keep semantics consistent
   - Parameter names, defaults, and ranges must match MCP.
   - JSON fields must match the per-tool mapping sheet.

5. Add global or shared options only if essential
   - E.g., `--api-base-url`, `--timeout`, `--auth-token` (via env var by default).


## 6) Parity and validation

Parity with MCP
- Execute each subcommand with representative inputs; capture `--json`.
- Execute the original MCP tool (if still present); compare outputs.
- Ensure structural equivalence and key field parity. Minor formatting differences (ordering, whitespace) are OK for human mode; not OK for JSON fields.

Golden tests (recommended; see migration_guide/test_validation_plan.md)
- Save known `--json` outputs for representative calls as goldens.
- Diff them in CI to catch regressions.
- For volatile endpoints, either mock or validate shapes/keys instead of full equality.

Error and exit-code behavior
- Validate missing required flags, invalid enums/ranges, network failures.
- Confirm JSON error envelopes in `--json` mode and exit 1.

Pagination
- Validate `--limit` and `--cursor` for list endpoints.
- Confirm consistent cursor fields and expected page boundaries.

Caching (if implemented)
- Validate TTL and refresh behavior.
- Measure first-run vs subsequent-run latency.


## 7) Distribution and usage

Local usage
- Use `uv run yourcmd <subcommand> [flags]`.
- Support `--help` and `--json` for every subcommand.

Packaging (optional)
- Publish as a Python package with a console entry point.
- Pin compatible dependency versions in `pyproject.toml`.

Embedding in other surfaces
- MCP server: call the CLI via subprocess and parse `--json`.
- File-System Scripts and Claude Skills: keep semantics aligned with the CLI’s `--json` contract.

Examples
- Human:
  ```
  uv run yourcmd markets --limit 5
  ```
- JSON:
  ```
  uv run yourcmd markets --limit 5 --json | jq '.items | length'
  ```


## 8) Documentation for users and agent permissions

Author a user-facing CLI README (separate from this migration guide):
- Overview and “when to use”
- Quick start (install, `uv run`, examples)
- Commands summary
- JSON mode examples (`--json`, piping to `jq`)
- Pagination (`--limit`, `--cursor`)
- Caching notes (if applicable)
- Auth configuration (env vars; scopes)
- Error and exit code behavior
- Common workflows (monitoring, exports, scripting)
- License and attribution if needed

Agent permissions and ops notes
- If agents invoke the CLI, document:
  - Allowed subcommands and flags (per role).
  - Expected data volumes and rate limits.
  - Location of the CLI binary and environment configuration.
  - Any resource limits or sandboxing.
- Provide a policy snippet or allowlist file for ops to review and adjust:
  - Example format:
    - allowed_commands: [“status”, “markets”, “search”]
    - max_limit_default: 50
    - disallowed_flags: [“--full”] (if too verbose by default)


## 9) Security and compliance

- No secrets in stdout for `--json` mode; stderr only for diagnostics.
- Prefer env vars or secret stores for tokens; avoid config files with secrets.
- Implement rate-limiting/backoff if required by the API.
- Validate/whitelist URLs; don’t accept arbitrary endpoints unless explicitly intended.
- Log minimal request metadata (if any) and ensure PII is handled appropriately.


## 10) Versioning and change management

- CLI as canonical contract:
  - Use semver if public. Document breaking changes clearly.
  - Maintain a CHANGELOG and include a “Breaking changes” section when applicable.
- MCP pinning:
  - If MCP wraps CLI, pin to a compatible CLI version.
- Deprecation policy:
  - Provide a transition period and warnings before removing/renaming commands/flags.
- Keep per-tool mapping sheets updated with any changes.


## 11) Example CLI command template

Below is a minimal pattern (illustrative). Keep yours concise, `--json`-friendly, and explicit.

```
# Example: your_cli/cli.py
import json
import sys
import typing as t
import click
import httpx

API_BASE_URL = "https://api.example.com/v1"
TIMEOUT = 30.0
USER_AGENT = "YourCLI/1.0"

@click.group()
def cli():
    "Root of your CLI."

@cli.command("markets")
@click.option("--limit", type=int, default=10, show_default=True, help="Max items to return")
@click.option("--cursor", type=str, default=None, help="Pagination cursor")
@click.option("--json", "as_json", is_flag=True, help="Emit pure JSON on stdout")
def markets(limit: int, cursor: t.Optional[str], as_json: bool):
    try:
        with httpx.Client(base_url=API_BASE_URL, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as c:
            resp = c.get("/markets", params={"limit": limit, "cursor": cursor})
            resp.raise_for_status()
            data = resp.json()

        if as_json:
            click.echo(json.dumps(data))
        else:
            items = data.get("items", [])
            click.echo(f"Markets: {len(items)} (limit={limit})")
            if "cursor" in data:
                click.echo(f"Next cursor: {data['cursor']}")
        sys.exit(0)

    except httpx.HTTPStatusError as e:
        message = f"HTTP error: {e.response.status_code}"
        if as_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"Error: {message}", err=True)
        sys.exit(1)

    except httpx.RequestError as e:
        message = f"Network error: {str(e)}"
        if as_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"Error: {message}", err=True)
        sys.exit(1)

    except Exception as e:
        message = f"Unexpected error: {str(e)}"
        if as_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"Error: {message}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()
```

Keep code for each subcommand similarly structured and consistent with your mapping sheets.


## 12) Checklist (copy/paste)

Planning
- [ ] Inventory all MCP tools, parameters, outputs
- [ ] Create per-tool mapping sheets
- [ ] Decide single-format vs multi-format plan

Design
- [ ] Subcommand names and flags defined (mirror MCP semantics)
- [ ] `--json` mode produces strict JSON; no stdout noise
- [ ] Exit codes: 0 success, 1 failure
- [ ] Pagination (`--limit`, `--cursor`) is consistent
- [ ] Caching behavior (if any) documented

Implementation
- [ ] HTTP client (httpx) with base URL, timeout, headers
- [ ] Subcommands implemented 1:1 with mapping sheets
- [ ] Human-readable defaults; `--json` for machines
- [ ] No secrets printed; stderr for diagnostic errors

Validation
- [ ] Parity checks vs MCP (and other formats, if present)
- [ ] Golden tests for representative calls
- [ ] Error/exit code tests
- [ ] Pagination flow tests

Docs and Ops
- [ ] User-facing CLI README with quick start, examples, `--json` usage
- [ ] Agent permissions/allowlist documented
- [ ] CHANGELOG updated
- [ ] Mapping sheets committed and linked

Release
- [ ] Package and/or distribute via repo with clear versioning
- [ ] Announce changes and any deprecations


## 13) References

- beyond-mcp (owner/creator: IndyDevDan) — a practical example of MCP wrapping a CLI, with scripts and Claude Skills also provided as complementary surfaces. The CLI there is designed with `--json` for clean machine output and acts as a canonical source of HTTP/API logic.
