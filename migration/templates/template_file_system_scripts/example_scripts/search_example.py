#!/usr/bin/env python3
# /// script
# dependencies = [
#     # Intentionally empty: no external dependencies (pure stdlib template)
# ]
# ///
"""
search_example.py (TEMPLATE / STUB)

Purpose:
    Illustrates the structure of a standalone keyword search script migrated
    from an MCP server tool into a file-system script with:
      - Progressive disclosure (inspect --help before reading source)
      - Dual output modes (--json vs human)
      - Deterministic exit codes
      - No external dependencies (argparse + stdlib only)

Status:
    This is NOT a runnable production script. All network/cache behavior is stubbed.
    Replace placeholder logic with real enumeration and filtering when adopting.

Key Principles:
    1. Single Responsibility (search only)
    2. Self-Contained (no shared helpers)
    3. Progressive Disclosure (minimal help, lean source)
    4. Dual Output Modes (human default, structured JSON when requested)
    5. Uniform Error Shape (human: '❌ Error: ...', json: {"error": "..."})
    6. Deterministic Exit Codes:
         0 success
         2 validation error
         4 unexpected/internal error
    7. Intentional Duplication (optimize only when duplication becomes painful)

Conceptual Usage (illustrative only):
    python search_example.py "resilience" --limit 5
    python search_example.py "energy policy" --limit 10 --json
    python search_example.py "tokenization" --rebuild-cache
    python search_example.py "bond yields" --status-filter active

Stub Cache Model:
    - Stores a static dataset to a JSON file in a hidden cache directory
    - TTL-based validity (rebuild with --rebuild-cache)
    - Real implementation should enumerate API resources and persist results
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration (Adjust when implementing for real)
# ---------------------------------------------------------------------------
_CACHE_DIR_NAME = ".example_cache"
_CACHE_FILE_PREFIX = "search_stub_"
DEFAULT_CACHE_TTL_MIN = 360  # minutes (6 hours)
DEFAULT_LIMIT = 10

# Static stub dataset (replace with real data)
_STATIC_ITEMS: List[Dict[str, object]] = [
    {
        "id": "ITEM-001",
        "title": "Resilience in Distributed Systems",
        "description": "Discussion of resilience strategies and patterns.",
        "status": "active",
        "updated_ts": 111,
    },
    {
        "id": "ITEM-002",
        "title": "Energy Policy Review 2024",
        "description": "Summary of global energy policy shifts.",
        "status": "active",
        "updated_ts": 222,
    },
    {
        "id": "ITEM-003",
        "title": "Bond Yields Quarterly Outlook",
        "description": "Projected yield movements and macro factors.",
        "status": "inactive",
        "updated_ts": 333,
    },
    {
        "id": "ITEM-004",
        "title": "Tokenization Framework Overview",
        "description": "Conceptual framework for asset tokenization.",
        "status": "active",
        "updated_ts": 444,
    },
]


# ---------------------------------------------------------------------------
# Stub TTL Cache
# ---------------------------------------------------------------------------
class StubCache:
    """
    Minimal TTL cache wrapper around a static list.
    Replace methods with real enumeration + persistence logic when making executable.
    """

    def __init__(self, root: Path, ttl_minutes: int):
        self.root = root
        self.ttl_minutes = ttl_minutes
        self.cache_dir = root / _CACHE_DIR_NAME
        self._items: Optional[List[Dict[str, object]]] = None

    def _latest_file(self) -> Optional[Path]:
        if not self.cache_dir.exists():
            return None
        matches = list(self.cache_dir.glob(f"{_CACHE_FILE_PREFIX}*.json"))
        if not matches:
            return None
        return max(matches, key=lambda f: f.stat().st_mtime)

    def _is_valid(self) -> bool:
        f = self._latest_file()
        if not f:
            return False
        age_min = (time.time() - f.stat().st_mtime) / 60.0
        return age_min < self.ttl_minutes

    def load(self, quiet: bool) -> Optional[List[Dict[str, object]]]:
        if not self._is_valid():
            return None
        f = self._latest_file()
        if not f:
            return None
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if not quiet:
                print(f"[CACHE] Loaded {len(data)} items")
            return data
        except Exception as e:
            if not quiet:
                print(f"[CACHE] Failed to read cache: {e}")
            return None

    def save(self, items: List[Dict[str, object]], quiet: bool):
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M")
            path = self.cache_dir / f"{_CACHE_FILE_PREFIX}{ts}.json"
            path.write_text(json.dumps(items), encoding="utf-8")
            if not quiet:
                print(f"[CACHE] Saved {len(items)} items -> {path.name}")
        except Exception as e:
            if not quiet:
                print(f"[CACHE] Failed to save cache: {e}")

    def rebuild(
        self, quiet: bool, status_filter: Optional[str]
    ) -> List[Dict[str, object]]:
        """
        PSEUDOCODE FOR REAL BUILD:
            items = []
            cursor = None
            while True:
                page = fetch_page(cursor, status_filter)
                items.extend(page.items)
                cursor = page.next_cursor
                if not cursor: break
            save(items)
        """
        if not quiet:
            print("[CACHE BUILD] Rebuilding (stub dataset)...")
        items = _STATIC_ITEMS
        if status_filter:
            items = [
                itm
                for itm in items
                if str(itm.get("status", "")).lower() == status_filter.lower()
            ]
        self.save(items, quiet=quiet)
        return items

        def search(
            self, keyword: str, limit: int, quiet: bool
        ) -> List[Dict[str, object]]:
            """
            Search cached (or static) items by keyword in title or description.

            Diagnostic Fix:
                Original sort key returned type 'object', triggering a type-checker
                complaint because list.sort expects a key producing a value with rich
                comparison methods. We now coerce 'updated_ts' to int explicitly to
                guarantee a comparable type.
            """
            if self._items is None:
                self._items = self.load(quiet=quiet)

            if self._items is None:
                if not quiet:
                    print("[CACHE] No valid cache; using static dataset.")
                self._items = _STATIC_ITEMS

            kw = keyword.lower()

            def _safe_updated_ts(item: Dict[str, object]) -> int:
                """
                Ensure the key function returns an int (SupportsRichComparison).
                Falls back to -1 if coercion fails so malformed entries sink.
                """
                v = item.get("updated_ts", 0)
                try:
                    return int(v)
                except Exception:
                    return -1

            filtered: List[Dict[str, object]] = []
            for item in self._items:
                title = str(item.get("title", "")).lower()
                desc = str(item.get("description", "")).lower()
                if kw in title or kw in desc:
                    filtered.append(item)

            filtered.sort(key=_safe_updated_ts, reverse=True)
            return filtered[:limit]


# ---------------------------------------------------------------------------
# Formatting (Human Mode)
# ---------------------------------------------------------------------------
def format_results(keyword: str, items: List[Dict[str, object]]) -> str:
    lines: List[str] = []
    lines.append("")
    lines.append(f"🔍 Search Results for '{keyword}'")
    lines.append("=" * 60)
    if not items:
        lines.append("No matches found.")
        lines.append("Tip: Broaden keyword or rebuild cache.")
    else:
        for i, item in enumerate(items, 1):
            title = str(item.get("title", "N/A"))
            desc_full = str(item.get("description", ""))
            desc = desc_full[:90]
            status = str(item.get("status", "unknown")).lower()
            status_icon = {"active": "🟢", "inactive": "🔴"}.get(status, "⚪")
            lines.append(
                f"{i}. {status_icon} {title[:70]}{'...' if len(title) > 70 else ''}"
            )
            if desc:
                lines.append(f"   {desc}{'...' if len(desc_full) > 90 else ''}")
            if "updated_ts" in item:
                lines.append(f"   updated_ts: {item['updated_ts']}")
            lines.append("")
        lines.append("Use --json for structured output.")
    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argparse Interface
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stub search script (no external deps)."
    )
    parser.add_argument(
        "keyword",
        nargs="?",
        help="Keyword to search (required unless rebuilding cache).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum results to return.",
    )
    parser.add_argument(
        "--status-filter",
        help="Filter items by status before keyword search.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output.",
    )
    parser.add_argument(
        "--cache-ttl-min",
        type=int,
        default=DEFAULT_CACHE_TTL_MIN,
        help="Cache TTL minutes.",
    )
    parser.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Force cache rebuild.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational messages.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    # Validation
    if args.limit < 1 or args.limit > 1000:
        msg = "Limit must be between 1 and 1000."
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(2)
    if args.cache_ttl_min <= 0:
        msg = "Cache time-to-live must be positive."
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(2)

    # Determine pseudo project root (adjust if directory layout differs)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    cache = StubCache(root=project_root, ttl_minutes=args.cache_ttl_min)

    # Diagnostic fix: define helper outside unreachable block (was previously nested after sys.exit).
    def _safe_updated_ts(item: Dict[str, object]) -> int:
        """
        Normalize updated_ts for sorting.
        Accepts int, float (truncates), or numeric string.
        Returns -1 for malformed values so they sort last.
        """
        v_raw = item.get("updated_ts", 0)
        if isinstance(v_raw, int):
            return v_raw
        if isinstance(v_raw, float):
            return int(v_raw)
        if isinstance(v_raw, str):
            v_str = v_raw.strip()
            if not v_str:
                return -1
            try:
                return int(v_str)
            except ValueError:
                return -1
        return -1

    try:
        if args.rebuild_cache:
            if not args.quiet:
                print("[CACHE] Rebuilding cache...")
            items = cache.rebuild(quiet=args.quiet, status_filter=args.status_filter)
            cache._items = items
            if args.keyword is None:
                payload = {"status": "cache_rebuilt", "count": len(items)}
                if args.json:
                    print(json.dumps(payload, indent=2))
                else:
                    print(f"✅ Cache rebuilt with {len(items)} items.")
                sys.exit(0)

        if args.keyword is None:
            msg = "Keyword is required unless rebuilding cache."
            if args.json:
                print(json.dumps({"error": msg}, indent=2))
            else:
                print(f"❌ Error: {msg}", file=sys.stderr)
            sys.exit(2)

        # Load or build cache items if needed (mirrors previous behavior).
        if cache._items is None:
            loaded = cache.load(quiet=args.quiet)
            if loaded is not None:
                cache._items = loaded

        if cache._items is None and not cache._is_valid():
            if not args.quiet:
                print("[CACHE] No valid cache; building now (stub).")
            cache._items = cache.rebuild(
                quiet=args.quiet, status_filter=args.status_filter
            )

        items_source = cache._items if cache._items is not None else _STATIC_ITEMS

        kw = args.keyword.lower()
        filtered: List[Dict[str, object]] = []
        for item in items_source:
            title = str(item.get("title", "")).lower()
            desc = str(item.get("description", "")).lower()
            if kw in title or kw in desc:
                filtered.append(item)
        filtered.sort(key=_safe_updated_ts, reverse=True)
        results = filtered[: args.limit]

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(format_results(args.keyword, results))

        sys.exit(0)

    except Exception as e:
        msg = f"Unexpected internal error: {e}"
        if args.json:
            print(json.dumps({"error": msg}, indent=2))
        else:
            print(f"❌ Error: {msg}", file=sys.stderr)
        sys.exit(4)


# ---------------------------------------------------------------------------
# Entry Point (template)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Progressive disclosure: invoke main only when executed directly.
    # This keeps import side-effects minimal if ever inspected programmatically.
    main()


# (Removed duplicate entry point block – single __main__ guard retained above)
