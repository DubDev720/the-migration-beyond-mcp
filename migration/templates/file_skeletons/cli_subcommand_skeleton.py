#!/usr/bin/env python3
"""
CLI Subcommand Skeleton

Purpose:
- Provide a ready-to-copy skeleton for adding a new subcommand to your CLI.
- Enforces conventions from the migration guides:
  - --json flag for machine-friendly output
  - Concise human-readable default output
  - Non-zero exit codes on failure
  - Minimal/no stdout noise in JSON mode (stderr for human diagnostics)

How to use:
1) Drop this file into your CLI project or copy the command function into your existing CLI module.
2) Register the `cli` group (if you don't already have one) or merge the command into your root group.
3) Replace the placeholder logic in `example_cmd` with your real endpoint / business logic.
4) Keep parameter names and semantics consistent with MCP, file-system scripts, and Claude skills.

Notes:
- Use your CLI as the canonical source of truth for HTTP logic and JSON contracts.
- MCP servers can wrap this CLI via subprocess and parse JSON.
- Scripts should remain self-contained; skills should wrap those scripts for Claude Code discovery.

Dependencies:
- click
- httpx
"""

import json
import sys
import typing as t

import click
import httpx

# ----- Optional configuration (replace with your own) -----
DEFAULT_TIMEOUT = 30.0
DEFAULT_USER_AGENT = "Your-CLI/1.0"
DEFAULT_API_BASE_URL = "https://example.com/api"
# ----------------------------------------------------------


@click.group()
def cli():
    """Your CLI root.

    Add additional subcommands here or import them from other modules.
    Keep help text concise; include examples and behavior notes in epilogues.
    """


@cli.command("example")
@click.option(
    "--param1",
    type=str,
    required=True,
    help="Example required parameter (maps to MCP/script param).",
)
@click.option(
    "--limit",
    type=int,
    default=10,
    show_default=True,
    help="Max items to return (preserve semantics across MCP/scripts/skills).",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Emit pure JSON on stdout (no logs). Human-readable output otherwise.",
)
def example_cmd(param1: str, limit: int, output_json: bool) -> None:
    """
    Example subcommand template.

    Conventions:
    - --json → machine output (strict JSON, no extra stdout noise)
    - default → concise human-readable output
    - exit(0) on success; exit(1) on failure
    - stderr for human diagnostics in JSON mode
    """
    try:
        # Replace with your real logic.
        # For HTTP calls, keep the client lifecycle scoped to the command.
        with httpx.Client(
            base_url=DEFAULT_API_BASE_URL,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        ) as client:
            # Example GET (replace path/params with real values):
            # resp = client.get("/v1/items", params={"q": param1, "limit": limit})
            # resp.raise_for_status()
            # data: t.Dict[str, t.Any] = resp.json()

            # Placeholder stub payload (remove when implementing real logic):
            data: t.Dict[str, t.Any] = {
                "param1": param1,
                "limit": limit,
                "items": [],
                "note": "Replace this stub with real HTTP/API logic.",
            }

        if output_json:
            # Strict JSON only on stdout.
            click.echo(json.dumps(data))
        else:
            # Concise human-readable output; avoid excessive verbosity.
            click.echo(
                f"param1={param1} • limit={limit} • items={len(data.get('items', []))}"
            )

        # Define your success semantics. For list endpoints, exit 0 even if empty is typical.
        sys.exit(0)

    except httpx.HTTPStatusError as e:
        # Server/client error with response context
        message = f"HTTP error: {e.response.status_code} - {e.response.text}"
        if output_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"Error: {message}", err=True)
        sys.exit(1)

    except httpx.RequestError as e:
        # Network/transport error
        message = f"Network error: {str(e)}"
        if output_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"Error: {message}", err=True)
        sys.exit(1)

    except Exception as e:
        # Unexpected failure; avoid leaking sensitive info
        message = f"Unexpected error: {str(e)}"
        if output_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"Error: {message}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
