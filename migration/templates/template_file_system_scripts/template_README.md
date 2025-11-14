# Template File System Scripts

Standalone, self‑contained example scripts for <YOUR DOMAIN HERE>.
Each script demonstrates the migration pattern from MCP tools to isolated
file system scripts that embrace progressive disclosure and minimal context consumption.

Replace domain‑specific placeholders (API_BASE_URL, endpoint paths, field names) with
your real project values.

## Progressive Disclosure

Run a script with `--help` first to view options. Only read the actual source if
the help text is insufficient. Agents and humans should load ONE script at a time,
not the entire suite.

Example:
```bash
uv run scripts/status_example.py --help
uv run scripts/status_example.py --json
```

## Core Ideology

1. Single Responsibility – One capability per script.
2. Self-Contained – Avoid shared utility imports until duplication becomes a real cost.
3. Dual Output Modes – Human-readable default + `--json` for structured chaining.
4. Uniform Error Shape – JSON mode errors: `{"error": "<message>"}`; human mode: `❌ Error: <message>`.
5. Deterministic Exit Codes – 0 success; reserved non-zero codes for semantic failure, validation, network, unexpected.
6. Progressive Disclosure – Do not pre-load or parse all scripts; load exactly what is needed.
7. Intentional Duplication – Early isolation > premature abstraction.
8. Portable – Each script can be copied on its own and still function.

## Available Example Scripts

### `scripts/status_example.py`
**When to use:** Check a system/service status (health, connectivity, version).
- Demonstrates: minimal HTTP client, semantic exit codes (healthy vs degraded), lean formatting.

### `scripts/search_example.py`
**When to use:** Perform keyword searches over enumerated resources with optional cache acceleration.
- Demonstrates: pagination-based cache build, keyword filtering, TTL, rebuild flag, structured results.

### `scripts/event_example.py`
**When to use:** List events or retrieve detailed information about a single event.
- Demonstrates: list vs detail mode, optional nested items, pagination, uniform error handling.

(Extend with additional scripts following the same pattern, e.g. `metrics_example.py`, `orderbook_example.py`, `timeseries_example.py`.)

## Architecture Pattern

```
Agent / Human
   ↓ (choose specific capability)
<single script>.py
   ↓
Embedded HTTP client
   ↓
Remote API (read-only endpoints)
```

No shared runtime state. No cross‑script imports. Each invocation stands alone.

## Quick Start

All scripts support `--help` and `--json`:

```bash
uv run scripts/<script_name>.py --help
uv run scripts/<script_name>.py --json
```

Recommended first invocation:
- Use small limits (`--limit 5`)
- Use `--json` when chaining into other tools or automated analysis.

## Adding a New Script

1. Copy one of the example files as a starting point: `cp scripts/status_example.py scripts/new_capability.py`
2. Rename class names & constants to match your capability.
3. Update endpoint paths & expected JSON fields.
4. Provide:
   - `@click.command()` interface
   - Validation for flags/arguments
   - Human formatter + JSON output path
   - Deterministic exit codes
5. Keep LOC concise (< ~250 lines). Break out only if logically necessary.

## Recommended Exit Code Mapping

| Code | Meaning                            |
|------|------------------------------------|
| 0    | Success                            |
| 1    | Semantic failure / unhealthy state |
| 2    | Validation error                   |
| 3    | Network / API error                |
| 4    | Unexpected internal error          |

(Adjust as needed, but keep consistent across scripts.)

## Best Practices

- Truncate long titles/strings when in human mode (token efficiency).
- Use consistent emojis/icons to signal status (🟢 active, 🔴 inactive, ⚪ unknown).
- Prefer explicit flags over environment variable magic (transparency).
- Avoid printing stack traces; provide clean error messages.
- Confirm “progressive disclosure” in documentation & agent prompts.

## Caching Guidelines (Optional)

If a script benefits from caching (e.g. search):
- Store cache under a hidden directory at project root (e.g. `.cache/<name>/`).
- Name files with timestamp for traceability (e.g. `resources_YYYYMMDD_HHMM.csv`).
- Provide:
  - `--rebuild-cache` flag
  - TTL flag (e.g. `--cache-ttl-min`)
  - Quiet mode (`--quiet`) to reduce verbose logs for agents

## Human vs JSON Mode

| Aspect         | Human Mode                              | JSON Mode                         |
|----------------|------------------------------------------|-----------------------------------|
| Purpose        | Quick inspection / summarization         | Chaining / structured processing  |
| Output Size    | Condensed, truncated                     | Full fidelity                     |
| Error Shape    | ❌ Error: message                        | {"error": "message"}              |
| Parsing        | Visual/manual                            | Programmatic/agent-friendly       |

## Minimal Script Skeleton (Reference)

```text
#!/usr/bin/env python3
# /// script
# dependencies = ["click", "httpx"]
# ///
"""
short_description_here
Usage:
  uv run scripts/example.py --json --limit 5
"""
import click, httpx, json, sys

API_BASE_URL = "..."
ENDPOINT = "/..."
DEFAULT_TIMEOUT = 15.0

class Client:
    def __init__(self, timeout):
        self.c = httpx.Client(base_url=API_BASE_URL, timeout=timeout)
    def __enter__(self): return self
    def __exit__(self,*a): self.c.close()
    def fetch(self, **params):
        # PSEUDOCODE:
        # r = self.c.get(ENDPOINT, params=params)
        # r.raise_for_status()
        # return r.json()
        return {"placeholder": True}

def format_human(data):
    return "Example Human Output"

@click.command()
@click.option("--json", "json_mode", is_flag=True)
def main(json_mode):
    try:
        with Client(timeout=DEFAULT_TIMEOUT) as client:
            data = client.fetch()
        if json_mode:
            click.echo(json.dumps(data, indent=2)); sys.exit(0)
        click.echo(format_human(data)); sys.exit(0)
    except Exception as e:
        msg = str(e)
        if json_mode: click.echo(json.dumps({"error": msg}, indent=2))
        else: click.echo(f"❌ Error: {msg}", err=True)
        sys.exit(4)

if __name__ == "__main__":
    main()
```

## Common Anti‑Patterns (Avoid)

| Anti‑Pattern                       | Why It Hurts                                  |
|-----------------------------------|-----------------------------------------------|
| Central mega “utils.py” early     | Increases context load; breaks isolation      |
| Scripts importing each other      | Hidden coupling; undermines portability       |
| Excessive abstraction prematurely | Harder to extend; unnecessary cognitive load  |
| Mixing multiple capabilities      | Reduces precision; larger token footprint     |
| Silent failures (exit 0 w/ error) | Misleads automation & agents                  |

## Extension Ideas

- Add a lightweight `scripts_index.py` to enumerate scripts + usage examples.
- Introduce analytics (timing, request counts) via optional `--debug` flag.
- Provide a `.env.example` if introducing authenticated endpoints later.

## Next Steps

1. Customize example scripts to your actual domain.
2. Add new capabilities following the skeleton.
3. Write a prime prompt instructing agents HOW and WHEN to use each script.
4. (Optional) Measure context savings vs original MCP server.

## License

Insert your preferred license text or reference here (e.g., MIT, Apache-2.0).

---

Template generated for rapid adoption of file system script patterns.
Feel free to remove sections not required for your use case.