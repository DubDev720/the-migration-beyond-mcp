#!/usr/bin/env python3
"""
scripts_index.py

Purpose:
    Enumerate available capability scripts in a repository, extract lightweight metadata
    (name, description summary, size, fingerprint), and optionally generate an agent
    prime prompt for progressive disclosure usage.

General Idea:
    Instead of loading all scripts (and their full content) into an AI agent's context,
    you expose only an index + a concise prime prompt. The agent then selectively
    loads individual scripts it actually needs, reducing total context consumption.

Features:
    - Scans a target scripts directory for *.py files
    - Extracts:
        * name
        * relative path
        * size (bytes)
        * SHA256 first 2KB fingerprint (stability indicator)
        * short description (from top docstring or header comments)
        * first 3 'Usage:' examples if present
    - Outputs JSON metadata (--json)
    - Generates agent prime prompt (--prime-prompt)
    - Pattern filtering (--filter)
    - Optional extended descriptions (--extended)
    - Designed to remain self-contained (stdlib only)

Usage Examples:
    python scripts_index.py
    python scripts_index.py --json
    python scripts_index.py --prime-prompt
    python scripts_index.py --filter market
    python scripts_index.py --json --extended
    python scripts_index.py --prime-prompt --filter trades

Add New Capability Scripts:
    Just drop a self-contained *.py file in the scripts directory. Re-run this index.

Agent Prime Prompt Strategy:
    Provide only:
      1. Concise one-line purpose per script
      2. Usage pattern skeleton
    Let agent decide which script to load next (progressive disclosure).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import textwrap
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ----------------------------
# Configuration
# ----------------------------
DEFAULT_SCRIPTS_DIR_NAMES = [
    "scripts",  # common
    "tools",  # alternative
    "file_system_scripts",  # domain-specific variant
]

MAX_DESCRIPTION_LINES = 8
MAX_USAGE_LINES = 3
FINGERPRINT_READ_LIMIT = 2048  # bytes
SUPPORTED_EXT = (".py",)

# ----------------------------
# Data Model
# ----------------------------


@dataclass
class ScriptMeta:
    name: str
    relative_path: str
    size_bytes: int
    fingerprint: str
    description: str
    usage_examples: List[str]
    modified_ts: str

    def to_prime_line(self) -> str:
        usage_part = (
            f" | Usage: {self.usage_examples[0]}" if self.usage_examples else ""
        )
        return f"{self.name}: {self.description}{usage_part}"


# ----------------------------
# Extraction Utilities
# ----------------------------


def find_scripts_root(start: Path) -> Path:
    """
    Heuristic: Look for a directory that contains capability scripts.
    Priority: explicit 'scripts' else first matching from DEFAULT_SCRIPTS_DIR_NAMES.
    Fallback: return the start if no dedicated directory is found (will scan recursively).
    """
    for dname in DEFAULT_SCRIPTS_DIR_NAMES:
        candidate = start / dname
        if candidate.is_dir():
            return candidate
    # fallback
    return start


def read_file_head(path: Path, max_bytes: int = 4096) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def extract_docstring_or_header(content: str) -> str:
    """
    Extract the top docstring triple-quoted block OR top contiguous comment lines.
    Return a concise multi-line summary (bounded).
    """
    # Try docstring first
    docstring_match = re.search(
        r'^[ \t]*("""|\'\'\')(.*?)(\1)', content, re.DOTALL | re.MULTILINE
    )
    if docstring_match:
        body = docstring_match.group(2).strip()
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    else:
        # Fallback: consecutive comment lines at start
        comment_lines = []
        for ln in content.splitlines():
            stripped = ln.strip()
            if stripped.startswith("#"):
                comment_lines.append(re.sub(r"^#\s?", "", stripped))
            elif stripped == "":
                # allow empty line early
                continue
            else:
                break
        lines = comment_lines

    # Filter overly long lines, take first N
    cleaned = [line_text for line_text in lines if line_text]
    if not cleaned:
        return "No description available."
    return "\n".join(cleaned[:MAX_DESCRIPTION_LINES])


def extract_usage_examples(content: str) -> List[str]:
    """
    Find 'Usage' section lines or lines beginning with typical invocation patterns.
    Strategy:
      - Look for 'Usage:' block
      - Fallback: lines containing 'uv run' or 'python' referencing the script
    """
    examples: List[str] = []
    usage_block = re.search(
        r"Usage:(.*?)(\n\s*\n|\Z)", content, re.DOTALL | re.IGNORECASE
    )
    if usage_block:
        block = usage_block.group(1)
        for ln in block.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            # Keep command-like lines
            if re.search(r"\b(uv run|python|./)\b", ln):
                examples.append(ln)
    if not examples:
        # fallback generic pattern search
        for ln in content.splitlines():
            s = ln.strip()
            if re.search(r"\b(uv run|python)\b.*\.py", s):
                examples.append(s)
            if len(examples) >= MAX_USAGE_LINES:
                break
    return examples[:MAX_USAGE_LINES]


def compute_fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            chunk = f.read(FINGERPRINT_READ_LIMIT)
            h.update(chunk)
        return h.hexdigest()[:16]  # short fingerprint
    except Exception:
        return "ERROR"


def gather_script_metadata(script_path: Path, root: Path) -> ScriptMeta:
    content = read_file_head(script_path)
    description = extract_docstring_or_header(content)
    usage = extract_usage_examples(content)
    stat = script_path.stat()
    rel = script_path.relative_to(root.parent if root.parent != root else root)
    return ScriptMeta(
        name=script_path.stem,
        relative_path=str(rel),
        size_bytes=stat.st_size,
        fingerprint=compute_fingerprint(script_path),
        description=single_line(description),
        usage_examples=usage,
        modified_ts=datetime.utcfromtimestamp(stat.st_mtime).isoformat() + "Z",
    )


def single_line(text: str) -> str:
    """
    Collapse multi-line description to a single concise line.
    Steps:
      - Strip individual lines
      - Discard empty lines
      - Join with single spaces
      - Normalize excess whitespace
      - Truncate to 300 characters
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    combined = " ".join(lines)
    combined = re.sub(r"\s{2,}", " ", combined)
    return combined[:300].strip()


def scan_scripts(root: Path, filter_pattern: Optional[str] = None) -> List[ScriptMeta]:
    scripts_root = find_scripts_root(root)
    metas: List[ScriptMeta] = []
    for path in scripts_root.rglob("*"):
        if path.is_file() and path.suffix in SUPPORTED_EXT:
            if filter_pattern and filter_pattern.lower() not in path.name.lower():
                continue
            metas.append(gather_script_metadata(path, scripts_root))
    # Sort for stability
    metas.sort(key=lambda m: m.name)
    return metas


# ----------------------------
# Prime Prompt Generation
# ----------------------------


def generate_prime_prompt(metas: List[ScriptMeta], extended: bool = False) -> str:
    """
    Build a concise agent priming prompt listing capabilities without dumping full code.
    """
    lines = []
    lines.append("You have access to the following capability scripts.")
    lines.append(
        "Load only the script you need; each supports '--json' for structured output."
    )
    lines.append("")
    for meta in metas:
        # Basic line
        lines.append(f"- {meta.name}: {meta.description}")
        if meta.usage_examples:
            lines.append(f"  Example: {meta.usage_examples[0]}")
        if extended and len(meta.usage_examples) > 1:
            for ex in meta.usage_examples[1:]:
                lines.append(f"  Alt: {ex}")
    lines.append("")
    lines.append("Strategy: Ask for the minimal script to accomplish the next step.")
    lines.append(
        "If chaining operations, request '--json' output for downstream automation."
    )
    return "\n".join(lines)


# ----------------------------
# CLI
# ----------------------------


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Index and describe capability scripts for progressive disclosure."
    )
    p.add_argument("--root", default=".", help="Root directory to start scanning.")
    p.add_argument("--filter", help="Case-insensitive substring filter on script name.")
    p.add_argument("--json", action="store_true", help="Output metadata as JSON.")
    p.add_argument(
        "--prime-prompt", action="store_true", help="Generate agent prime prompt."
    )
    p.add_argument(
        "--extended",
        action="store_true",
        help="Include extended usage in prime prompt.",
    )
    p.add_argument(
        "--limit", type=int, help="Limit number of scripts returned (for large sets)."
    )
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    root_path = Path(args.root).resolve()

    metas = scan_scripts(root_path, filter_pattern=args.filter)

    if args.limit is not None and args.limit >= 0:
        metas = metas[: args.limit]

    if args.json:
        payload = [asdict(m) for m in metas]
        print(json.dumps(payload, indent=2))
        return 0

    if args.prime_prompt:
        prompt = generate_prime_prompt(metas, extended=args.extended)
        print(prompt)
        return 0

    # Default human summary
    print(
        f"Discovered {len(metas)} script(s). Use --json or --prime-prompt for structured output.\n"
    )
    for meta in metas:
        print(f"{meta.name} ({meta.size_bytes} bytes)  fp={meta.fingerprint}")
        print(f"  {wrap(meta.description)}")
        if meta.usage_examples:
            print(f"  Example: {meta.usage_examples[0]}")
        print("")
    print("Run with --prime-prompt for agent priming text.")
    print("Run with --json for machine-readable metadata.")
    return 0


def wrap(text: str, width: int = 88) -> str:
    return textwrap.fill(text, width=width)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
