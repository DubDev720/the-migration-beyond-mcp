#!/usr/bin/env python3
# /// script
# dependencies = [
#     # Intentionally empty: keep this script dependency-free.
# ]
# ///
"""
status_example.py (LEAN TEMPLATE)

Purpose:
    Illustrate structure for a status-style file system script WITHOUT external
    dependencies (no httpx, no click). This version is NOT meant to run; it is
    a lint-friendly placeholder demonstrating best practices & progressive disclosure.

Ideology / Principles:
    1. Single Responsibility (one capability per script)
    2. Self-Contained (no shared imports)
    3. Progressive Disclosure (agents use --help first, then execute)
    4. Dual Output Modes (human vs --json)
    5. Uniform Errors (human: '❌ Error: ...', json: {"error": "..."})
    6. Deterministic Exit Codes (0 success, 1 degraded, 2 validation, 3 network, 4 unexpected)
    7. Lean Implementation (no premature abstraction)
    8. Intentional Duplication (optimize later only if needed)

Usage Examples (conceptual only):
    python status_example.py
    python status_example.py --json
    python status_example.py --timeout 10
    python status_example.py --json --quiet

NOTE:
    This template stubs network behavior with pseudocode. Replace the
    placeholder logic with real implementation when making it executable.
"""

import argparse
import json
import sys
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# Configuration (Customize These Per Project)
# ---------------------------------------------------------------------------
_API_BASE_URL = "https://api.example.com/v1"  # placeholder (unused stub)
_CLIENT_ENDPOINT = "/system/status"  # placeholder (unused stub)
DEFAULT_TIMEOUT = 15.0  # Seconds (used for --timeout validation)
_USER_AGENT = "Example-Scripts/1.0"  # placeholder (unused stub)

# Expected response keys (adjust for real API):
# {
#   "service_active": true,
#   "db_connected": true,
#   "version": "1.2.3",
#   "message": "OK",
#   "timestamp": 1731543600
# }


class ExampleStatusClient:
    """
    Placeholder HTTP client (NO real network calls).

    PSEUDOCODE FOR REAL IMPLEMENTATION:
    -----------------------------------
    1. Open connection (e.g., requests or httpx)
    2. GET f"{API_BASE_URL}{CLIENT_ENDPOINT}"
    3. Parse JSON
    4. Validate presence of required keys
    5. Return dict

    CURRENT:
    Returns a static dictionary simulating a healthy service.
    """

    def __init__(self, timeout: float):
        self.timeout = timeout  # retained for structural realism

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Would close network client here if one existed
        pass

    def fetch_status(self) -> Dict[str, object]:
        """
        Simulated status fetch. Replace with real HTTP logic.
        """
        # PSEUDOCODE (replace):
        # response = http_client.get(CLIENT_ENDPOINT, timeout=self.timeout)
        # data = response.json()
        # if "service_active" not in data: raise ValueError(...)
        # return data

        # Static placeholder:
        return {
            "service_active": True,
            "db_connected": True,
            "version": "0.0.0-template",
            "message": "Template OK",
            "timestamp": 0,
        }


def format_human(status: Dict[str, object], quiet: bool) -> str:
    """
    Human-readable formatting (token-efficient).
    Diagnostics Fix: ensure booleans are properly typed before icon()
    """
    lines = []
    lines.append("")
    lines.append("Example Service Status (Template)")
    lines.append("=" * 40)

    # Extract and narrow types for diagnostics
    _service_raw = status.get("service_active")
    service_active: Optional[bool] = (
        _service_raw if isinstance(_service_raw, bool) else None
    )

    _db_raw = status.get("db_connected")
    db_connected: Optional[bool] = _db_raw if isinstance(_db_raw, bool) else None

    version = status.get("version", "unknown")
    message = status.get("message", "")
    timestamp = status.get("timestamp")

    def icon(value: Optional[bool]) -> str:
        if value is True:
            return "🟢"
        if value is False:
            return "🔴"
        return "⚪"

    lines.append(f"{icon(service_active)} Service: {service_active}")
    lines.append(f"{icon(db_connected)} Database: {db_connected}")
    lines.append(f"🔖 Version: {version}")
    if message:
        lines.append(f"💬 Message: {str(message)[:120]}")
    if timestamp is not None:
        lines.append(f"🕒 Timestamp: {timestamp}")

    if not quiet:
        lines.append("=" * 40)
        lines.append(
            "Tip: Use --json for structured output. Exit code 1 signals unhealthy state."
        )

    return "\n".join(lines)


def determine_exit_code(status: Dict[str, object]) -> int:
    """
    Semantic exit code logic (template).
    """
    service = status.get("service_active")
    db = status.get("db_connected")

    if service is True and db is True:
        return 0
    if service is False or db is False:
        return 1
    return 1  # Unknown treated as degraded


def parse_args() -> argparse.Namespace:
    """
    Minimal argparse interface replacing click.
    """
    parser = argparse.ArgumentParser(
        description="Template status script (no external dependencies)."
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Simulated timeout (positive float).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress tips in human mode."
    )
    return parser.parse_args()


def main():
    """
    Main entry point:
      - Parse args
      - Validate
      - Simulate status fetch
      - Output (human or JSON)
      - Exit with semantic code
    """
    args = parse_args()

    # Validation
    if args.timeout <= 0:
        msg = "Timeout must be positive."
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(2)

    try:
        with ExampleStatusClient(timeout=args.timeout) as client:
            status_data = client.fetch_status()

        if args.json:
            print(json.dumps(status_data, indent=2))
        else:
            print(format_human(status_data, quiet=args.quiet))

        sys.exit(determine_exit_code(status_data))

    except Exception as e:
        # Unified unexpected error path (no network differentiation here since stub)
        msg = f"Unexpected internal error: {e}"
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(4)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
