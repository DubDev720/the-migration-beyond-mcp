#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx",
#     "click",
# ]
# ///
"""
File‑System Script Skeleton

Purpose:
- Provide a self‑contained, one‑file template for a capability your agents can invoke directly.
- Enforce progressive disclosure and agent‑friendly conventions:
  - `--help` explains options succinctly
  - `--json` emits strict JSON on stdout (no extra noise)
  - Non‑zero exit codes on failure
  - Minimal context footprint (no shared project imports required)

How to adapt:
1) Replace API_BASE_URL, endpoints, and request/response handling with your real logic.
2) Keep parameter names, defaults, and semantics consistent with your MCP and CLI surfaces.
3) Preserve strict JSON output when `--json` is used (no logs on stdout).
4) Validate exit codes and error envelopes for automation.

Usage examples:
  uv run script_skeleton.py --param1 foo --limit 5
  uv run script_skeleton.py --param1 foo --limit 5 --json
  uv run script_skeleton.py --param1 foo --simulate --json

Notes:
- This template includes a `--simulate` flag to return stub data without making a network call.
  Remove it once you wire up real HTTP logic.
"""

import json
import sys
from typing import Any, Dict, Optional

import click
import httpx

# -----------------------------
# Configuration (customize me)
# -----------------------------
API_BASE_URL = "https://example.com/api"
API_TIMEOUT = 30.0  # seconds
USER_AGENT = "Your-Script/1.0"

# Optional: Default headers for your API
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    # Add auth headers here only if needed; prefer env vars or secure stores for secrets.
    # "Authorization": f"Bearer {os.environ.get('YOUR_API_TOKEN', '')}",
}


class Client:
    """
    Minimal HTTP client for your API.
    Keep this client limited to what the script needs to remain small and self‑contained.
    """

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout: float = API_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers=headers or DEFAULT_HEADERS,
        )

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.client.close()

    # Replace this method with your real endpoint logic.
    def fetch_example(self, param1: str, limit: int) -> Dict[str, Any]:
        """
        Example fetch. Replace path/params with real values and shape the returned JSON
        to match what your CLI and MCP expose.

        Returns:
            Dict[str, Any]: Payload to emit in `--json` mode.
        """
        response = self.client.get(
            "/example",  # ← Replace with your real path, e.g., "/v1/items"
            params={
                "q": param1,
                "limit": limit,
            },
        )
        response.raise_for_status()
        return response.json()


def format_human(data: Dict[str, Any]) -> str:
    """
    Concise human‑readable formatter for default (non‑JSON) output.
    Keep this brief to minimize tokens if an agent reads it.

    Args:
        data: The payload to format

    Returns:
        A small string suitable for terminal display.
    """
    # Adjust these fields for your real payload
    param1 = data.get("param1") or data.get("query") or "N/A"
    items = data.get("items") or data.get("results") or []
    count = (
        len(items)
        if isinstance(items, list)
        else (items.get("count") if isinstance(items, dict) else "N/A")
    )

    lines = []
    lines.append("Example Results")
    lines.append("=" * 40)
    lines.append(f"param1: {param1}")
    lines.append(f"count:  {count}")
    return "\n".join(lines)


@click.command()
@click.option(
    "--param1",
    required=True,
    type=str,
    help="Example required parameter (keep naming consistent with MCP/CLI).",
)
@click.option(
    "--limit",
    default=10,
    show_default=True,
    type=click.IntRange(min=1),
    help="Max items to return (preserve semantics across surfaces).",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Emit strict JSON on stdout (no logs). Human-readable output otherwise.",
)
@click.option(
    "--simulate",
    is_flag=True,
    help="Return stub data instead of making a network call (remove once real logic is implemented).",
)
def main(param1: str, limit: int, output_json: bool, simulate: bool) -> None:
    """
    Self‑contained script entry point.

    Conventions:
    - `--json` → machine output (strict JSON, no extra stdout noise)
    - default → concise human‑readable output
    - exit(0) on success; exit(1) on failure
    - stderr for human diagnostics in JSON mode
    """
    try:
        if simulate or API_BASE_URL == "https://example.com/api":
            # Stub payload to make this template runnable out of the box.
            data: Dict[str, Any] = {
                "param1": param1,
                "limit": limit,
                "items": [
                    {"id": "ex_1", "name": "Example 1"},
                    {"id": "ex_2", "name": "Example 2"},
                ][:limit],
                "_note": "Simulated data. Wire up real HTTP logic and remove --simulate.",
            }
        else:
            with Client() as client:
                data = client.fetch_example(param1, limit)

        if output_json:
            # Strict JSON only on stdout.
            click.echo(json.dumps(data))
        else:
            # Concise human output; avoid excessive verbosity.
            click.echo(format_human(data))

        # Define success semantics. For list endpoints, empty results can still be success (exit 0).
        sys.exit(0)

    except httpx.HTTPStatusError as e:
        message = f"HTTP error: {e.response.status_code} - {e.response.text}"
        if output_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"❌ Error: {message}", err=True)
        sys.exit(1)

    except httpx.RequestError as e:
        message = f"Network error: {str(e)}"
        if output_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"❌ Error: {message}", err=True)
        sys.exit(1)

    except Exception as e:
        # Unexpected failure; avoid leaking sensitive info.
        message = f"Unexpected error: {str(e)}"
        if output_json:
            click.echo(json.dumps({"error": message}))
        else:
            click.echo(f"❌ Error: {message}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
