#!/usr/bin/env python3
# /// script
# dependencies = [
#     # Intentionally empty: dependency-free stub (no external libs)
# ]
# ///
"""
event_example.py (LEAN TEMPLATE)

Purpose:
    Show structure for an "event" capability script (list + detail) WITHOUT
    external dependencies (no click/httpx). This is a lint-friendly placeholder,
    not intended to run as-is. Replace stub logic with real API calls when adopting.

Ideology / Principles:
    1. Single Responsibility (list & optional detail only)
    2. Self-Contained (no shared internal modules)
    3. Progressive Disclosure (agents inspect --help first)
    4. Dual Output Modes (--json vs human)
    5. Uniform Errors (human: ❌ Error..., json: {"error": "..."})
    6. Deterministic Exit Codes (0 success, 2 validation, 4 unexpected)
    7. Intentional Duplication (optimize later only if necessary)

Usage (conceptual):
    python event_example.py --limit 5
    python event_example.py --event-id EVT-001 --json
    python event_example.py --limit 10 --status-filter active
    python event_example.py --event-id EVT-002 --with-items

Stub Data Model:
    Static in-memory list of events; detail mode returns nested items when requested.
"""

import argparse
import json
import sys
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration (Adjust for real project)
# ---------------------------------------------------------------------------
MAX_LIMIT_HARD_CAP = 200
DEFAULT_LIMIT = 10
_DEFAULT_TIMEOUT = 20.0  # placeholder timeout constant (unused outside parse_args)

# Stub dataset (replace with real fetched events)
STATIC_EVENTS: List[Dict[str, object]] = [
    {
        "event_id": "EVT-001",
        "title": "Distributed Systems Summit",
        "status": "active",
        "category": "conference",
        "items": [
            {"item_id": "ITM-001A", "title": "Opening Keynote"},
            {"item_id": "ITM-001B", "title": "Resilience Panel"},
        ],
    },
    {
        "event_id": "EVT-002",
        "title": "Quarterly Financial Review",
        "status": "closed",
        "category": "finance",
        "items": [
            {"item_id": "ITM-002A", "title": "Earnings Overview"},
            {"item_id": "ITM-002B", "title": "Sector Performance"},
            {"item_id": "ITM-002C", "title": "Q&A"},
        ],
    },
    {
        "event_id": "EVT-003",
        "title": "Security Incident Simulation",
        "status": "active",
        "category": "ops",
        "items": [
            {"item_id": "ITM-003A", "title": "Red Team Exercise"},
        ],
    },
]


# ---------------------------------------------------------------------------
# Stub Client
# ---------------------------------------------------------------------------
class ExampleEventClient:
    """
    Stub client simulating list and detail retrieval.
    Replace methods with real HTTP logic when making executable.
    """

    def __init__(self, timeout: float):
        self.timeout = timeout  # Retained for structural realism

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close network resources here if added later
        pass

    def list_events(
        self,
        limit: int,
        status_filter: Optional[str],
        cursor: Optional[str],  # Unused in stub (placeholder for pagination)
        with_items: bool,
    ) -> Dict[str, object]:
        events = STATIC_EVENTS
        if status_filter:
            events = [
                e
                for e in events
                if str(e.get("status", "")).lower() == status_filter.lower()
            ]
        # Truncate to limit
        events = events[:limit]
        # In real implementation, you'd remove items unless with_items requested.
        if not with_items:
            stripped = []
            for e in events:
                copy = dict(e)
                copy.pop("items", None)
                stripped.append(copy)
            events = stripped
        return {"events": events, "cursor": None}

    def get_event(self, event_id: str, with_items: bool) -> Dict[str, object]:
        for e in STATIC_EVENTS:
            if e.get("event_id") == event_id:
                if with_items:
                    return {
                        "event": {k: v for k, v in e.items() if k != "items"},
                        "items": e.get("items", []),
                    }
                return {"event": {k: v for k, v in e.items() if k != "items"}}
        raise RuntimeError("Event not found")


# ---------------------------------------------------------------------------
# Formatting (Human Mode)
# ---------------------------------------------------------------------------
def format_event_summary(event: Dict[str, object], index: int) -> str:
    # Coerce potentially 'object' typed values into expected concrete types
    event_id = str(event.get("event_id", "N/A"))
    title = str(event.get("title", "Untitled"))
    status = str(event.get("status", "unknown")).lower()
    category = str(event.get("category", "unclassified"))  # renamed to avoid diagnostic
    raw_items = event.get("items")
    items: List[Dict[str, object]] = raw_items if isinstance(raw_items, list) else []

    # Safely derive item_count without passing arbitrary 'object' to int()
    raw_item_count = event.get("item_count")
    item_count_field: int = 0
    if isinstance(raw_item_count, int):
        item_count_field = raw_item_count
    elif isinstance(raw_item_count, float):
        # Truncate toward zero (consistent with int() behavior)
        item_count_field = int(raw_item_count)
    elif isinstance(raw_item_count, str):
        try:
            item_count_field = int(raw_item_count.strip())
        except ValueError:
            item_count_field = 0
    # If items list present, prefer its length; otherwise use parsed field value
    item_count = len(items) if items else item_count_field

    status_icon = {
        "active": "🟢",
        "open": "🟢",
        "closed": "🔴",
        "inactive": "🔴",
        "settled": "⚪",
    }.get(status, "⚪")

    lines: List[str] = []
    lines.append(f"{index}. {status_icon} {event_id}")
    # Safe slicing now that title is guaranteed a str
    lines.append(f"   {title[:70]}{'...' if len(title) > 70 else ''}")
    lines.append(f"   Category: {category} | Status: {status}")
    if item_count:
        lines.append(f"   Items: {item_count}")
    return "\n".join(lines)


def format_events_list(response: Dict[str, object]) -> str:
    # Defensive extraction to satisfy type checkers (narrow 'object' to concrete list)
    raw_events = response.get("events")
    events: List[Dict[str, object]] = []
    if isinstance(raw_events, list):
        for item in raw_events:
            if isinstance(item, dict):
                events.append(item)
    cursor_raw = response.get("cursor")
    cursor: Optional[str] = (
        str(cursor_raw) if isinstance(cursor_raw, (str, int)) else None
    )

    lines: List[str] = []
    lines.append("")
    lines.append("📁 Events")
    lines.append("=" * 60)
    lines.append(f"Found {len(events)} event(s)")
    lines.append("")
    for i, ev in enumerate(events, 1):
        lines.append(format_event_summary(ev, i))
        lines.append("")
    if cursor:
        lines.append("─" * 60)
        lines.append(f"More results available. Use --cursor {cursor[:24]}...")
    lines.append("=" * 60)
    lines.append("Tip: Use --json for structured output.")
    return "\n".join(lines)


def format_event_detail(response: Dict[str, object], with_items: bool) -> str:
    # Defensive extraction: response is Dict[str, object], but nested values are 'object'
    raw_event = response.get("event")
    event_obj: Dict[str, object] = raw_event if isinstance(raw_event, dict) else {}

    event_id = str(event_obj.get("event_id", "N/A"))
    title = str(event_obj.get("title", "Untitled"))
    status = str(event_obj.get("status", "unknown"))
    category = str(
        event_obj.get("category", "unclassified")
    )  # align spelling with list formatter

    raw_items = response.get("items") if with_items else []
    items: List[Dict[str, object]] = []
    if with_items and isinstance(raw_items, list):
        for it in raw_items:
            if isinstance(it, dict):
                items.append(it)

    status_icon = {
        "active": "🟢",
        "open": "🟢",
        "closed": "🔴",
        "inactive": "🔴",
        "settled": "⚪",
    }.get(status.lower(), "⚪")

    lines: List[str] = []
    lines.append("")
    lines.append("📌 Event Detail")
    lines.append("=" * 60)
    lines.append(f"{status_icon} Event ID: {event_id}")
    lines.append(f"Title: {title}")
    lines.append(f"Status: {status}")
    lines.append(f"Category: {category}")
    if with_items:
        lines.append(f"Items Count: {len(items)}")
        for i, item in enumerate(items[:10], start=1):
            item_id = str(item.get("item_id", f"item-{i}"))
            item_title_raw = item.get("title", "")
            item_title = str(item_title_raw)[:60]
            lines.append(f"  {i}. {item_id} - {item_title}")
        if len(items) > 10:
            lines.append(f"  ... ({len(items) - 10} more)")
    lines.append("=" * 60)
    lines.append("Tip: Use --json for full structured detail.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argparse Interface
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stub event script (no external dependencies)."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Number of events to list (ignored in detail mode).",
    )
    parser.add_argument(
        "--status-filter",
        help="Filter events by status (e.g. active, closed).",
    )
    parser.add_argument(
        "--cursor",
        help="Pagination cursor (placeholder; stub does not paginate).",
    )
    parser.add_argument(
        "--event-id",
        help="Retrieve a single event by identifier (detail mode).",
    )
    parser.add_argument(
        "--with-items",
        action="store_true",
        help="Include nested items array if available.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output instead of human-readable formatting.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=_DEFAULT_TIMEOUT,
        help="Simulated timeout (positive float).",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    # Validation
    if args.timeout <= 0:
        msg = "Timeout must be positive."
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(2)

    if args.event_id is None:
        if args.limit < 1 or args.limit > MAX_LIMIT_HARD_CAP:
            msg = f"Limit must be between 1 and {MAX_LIMIT_HARD_CAP}."
            if args.json:
                print(json.dumps({"error": msg}, indent=2))
            else:
                print(f"❌ Error: {msg}", file=sys.stderr)
            sys.exit(2)

    try:
        with ExampleEventClient(timeout=args.timeout) as client:
            if args.event_id:
                response = client.get_event(
                    event_id=args.event_id, with_items=args.with_items
                )
                if args.json:
                    print(json.dumps(response, indent=2))
                else:
                    print(format_event_detail(response, with_items=args.with_items))
            else:
                response = client.list_events(
                    limit=args.limit,
                    status_filter=args.status_filter,
                    cursor=args.cursor,
                    with_items=args.with_items,
                )
                if args.json:
                    print(json.dumps(response, indent=2))
                else:
                    print(format_events_list(response))
        sys.exit(0)

    except RuntimeError as e:
        msg = str(e)
        # Network/API distinctions removed in stub; treat as unexpected
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(4)
    except Exception as e:
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
