#!/usr/bin/env python3
"""
CLI Script Generator

Add CLI script generator to scaffold a CLI subcommand and optional standalone script.

This generator creates:
- A CLI subcommand file (Click-based) with:
  - --json output
  - clean exit codes
  - minimal/no stdout noise in JSON mode
  - httpx-based example call to your API endpoint
- A standalone, self-contained script with:
  - --help and --json
  - optional --simulate stub mode
  - minimal httpx client scoped to the script
  - clean exit codes and progressive disclosure conventions

It can also optionally emit:
- A comprehensive test_validation_plan.md with end-to-end guidance
- A GENERATOR_USAGE.md snippet describing how to use this generator

Usage:
  python generate_cli_script.py <name> \
      --target both \
      --binary mycli \
      --endpoint /v1/example \
      --api-base-url https://api.example.com \
      --param limit:int:10 \
      --param query:str \
      --out-cli ./apps/2_cli/my_command.py \
      --out-script ./apps/3_file_system_scripts/scripts/my_command.py \
      --emit-test-plan ./tests/test_validation_plan.md \
      --emit-doc-snippets ./migration_guide/GENERATOR_USAGE.md \
      --force

Notes:
- Param format: name:type[:default]
  - If default is omitted, the parameter is required
  - Supported types: str, int, float, bool
  - Example: --param limit:int:10 --param query:str
- The generated files require `click` and `httpx` for runtime.

This tool writes files relative to the current working directory unless you pass absolute paths.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent, indent

# -------------------------
# Data model and utilities
# -------------------------


@dataclass
class ParamSpec:
    name: str
    type: str  # 'str' | 'int' | 'float' | 'bool'
    required: bool
    default: str | None


SUPPORTED_TYPES = {"str", "int", "float", "bool"}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def snake(s: str) -> str:
    # Convert to snake_case for function/variable names
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s).strip("_")
    return s.lower()


def valid_identifier(s: str) -> bool:
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", s) is not None


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"File exists: {path} (use --force to overwrite)")
    ensure_parent(path)
    if dry_run:
        print(f"[DRY RUN] Would write: {path}")
    else:
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path}")


def parse_param_token(token: str) -> ParamSpec:
    """
    Parse a token of the form:
      name:type[:default]
    Required if no default is provided.
    """
    parts = token.split(":")
    if len(parts) < 2 or len(parts) > 3:
        raise ValueError(
            f"Invalid --param format: '{token}'. Expected 'name:type[:default]'"
        )
    name = parts[0].strip()
    typ = parts[1].strip()
    default = parts[2].strip() if len(parts) == 3 else None
    if not name or not valid_identifier(snake(name)):
        raise ValueError(f"Invalid parameter name: '{name}'")
    if typ not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported type '{typ}' in '{token}'. Supported: {', '.join(sorted(SUPPORTED_TYPES))}"
        )
    required = default is None
    return ParamSpec(name=snake(name), type=typ, required=required, default=default)


def parse_params(tokens: list[str]) -> list[ParamSpec]:
    seen = set()
    specs: list[ParamSpec] = []
    for t in tokens:
        spec = parse_param_token(t)
        if spec.name in seen:
            raise ValueError(f"Duplicate parameter name: '{spec.name}'")
        seen.add(spec.name)
        specs.append(spec)
    return specs


def click_type(typ: str) -> str:
    if typ == "str":
        return "str"
    if typ == "int":
        return "int"
    if typ == "float":
        return "float"
    if typ == "bool":
        # handled differently (is_flag)
        return "bool"
    return "str"


def python_cast_value(typ: str, val: str) -> str:
    if typ == "str":
        return repr(val)
    if typ == "int":
        return str(int(val))
    if typ == "float":
        return str(float(val))
    if typ == "bool":
        if val.lower() in {"1", "true", "yes", "y", "on"}:
            return "True"
        if val.lower() in {"0", "false", "no", "n", "off"}:
            return "False"
        raise ValueError(f"Invalid boolean default: {val}")
    return repr(val)


# -------------------------
# Content generators (CLI)
# -------------------------


def generate_cli_content(
    *,
    name: str,
    binary: str,
    api_base_url: str,
    endpoint: str,
    params: list[ParamSpec],
    description: str | None,
) -> str:
    func_name = f"{snake(name)}_cmd"
    subcommand = name.replace("_", "-")
    user_agent = f"{binary}/1.0"

    # Build click options
    option_lines = []
    param_names_for_signature = []
    param_use_vars = []
    http_params = []

    for p in params:
        if p.type == "bool":
            default_expr = (
                "False"
                if p.required
                else python_cast_value("bool", p.default or "false")
            )
            option_lines.append(
                dedent(
                    f"""
                    @click.option(
                        "--{p.name}",
                        is_flag=True,
                        default={default_expr},
                        show_default=True,
                        help="Boolean flag parameter: {p.name}",
                    )
                    """.rstrip()
                )
            )
            param_names_for_signature.append(f"{p.name}: bool")
            http_params.append(f'"{p.name}": {p.name}')
            param_use_vars.append(p.name)
        else:
            click_typ = click_type(p.type)
            if p.required:
                option_lines.append(
                    dedent(
                        f"""
                        @click.option(
                            "--{p.name}",
                            type={click_typ},
                            required=True,
                            help="Required parameter: {p.name}",
                        )
                        """.rstrip()
                    )
                )
            else:
                default_expr = (
                    python_cast_value(p.type, p.default)
                    if p.default is not None
                    else "None"
                )
                show_default = "True" if p.default is not None else "False"
                option_lines.append(
                    dedent(
                        f"""
                        @click.option(
                            "--{p.name}",
                            type={click_typ},
                            default={default_expr},
                            show_default={show_default},
                            help="Optional parameter: {p.name}",
                        )
                        """.rstrip()
                    )
                )
            param_names_for_signature.append(f"{p.name}: {click_typ}")
            http_params.append(f'"{p.name}": {p.name}')
            param_use_vars.append(p.name)

    # --json option
    option_lines.append(
        dedent(
            """
            @click.option(
                "--json",
                "output_json",
                is_flag=True,
                help="Emit pure JSON on stdout (no logs). Human-readable output otherwise.",
            )
            """.rstrip()
        )
    )

    options_blob = "\n".join(option_lines)

    signature = ", ".join(param_names_for_signature + ["output_json: bool"])

    # Assemble params dict for HTTP query
    http_params_blob = ",\n                ".join(http_params) if http_params else ""

    human_lines = [
        f'f"Command: {subcommand}"',
        f'f"Endpoint: {endpoint}"',
        f'f"Params: '
        + "{"
        + ", ".join([f"{p.name}={{{{ {p.name} }}}}" for p in params])
        + '}"'
        if params
        else 'f"No parameters"',
    ]
    human_blob = "\n            ".join(
        [f"click.echo({line})" for line in human_lines if line]
    )

    desc_line = description.strip() if description else f"{name} subcommand"

    content = f"""#!/usr/bin/env python3
import json
import sys
import typing as t

import click
import httpx

DEFAULT_TIMEOUT = 30.0
DEFAULT_USER_AGENT = {repr(user_agent)}
DEFAULT_API_BASE_URL = {repr(api_base_url)}

@click.group()
def cli():
    \"\"\"{binary} root CLI group.
    Add or import additional commands into this group.
    \"\"\"


@cli.command({repr(subcommand)})
{indent(options_blob, "")}
def {func_name}({signature}) -> None:
    \"\"\"{desc_line}.
    Conventions:
    - --json → machine output (strict JSON on stdout)
    - default → concise human-readable output
    - exit(0) on success; exit(1) on failure
    - stderr for human diagnostics in JSON mode
    \"\"\"
    try:
        with httpx.Client(
            base_url=DEFAULT_API_BASE_URL,
            timeout=DEFAULT_TIMEOUT,
            headers={{"User-Agent": DEFAULT_USER_AGENT}},
        ) as client:
            # Replace with your real HTTP logic and response shaping
            resp = client.get(
                {repr(endpoint)},
                params={{
                {indent(http_params_blob, "                ")}
                }},
            )
            resp.raise_for_status()
            data: t.Dict[str, t.Any] = resp.json()

        if output_json:
            click.echo(json.dumps({{
                "endpoint": {repr(endpoint)},
                "params": {{
{indent(http_params_blob, "                    ")}
                }},
                "data": data
            }}))
        else:
            {human_blob}
            click.echo(f"Items: {{len(data) if isinstance(data, list) else 'N/A'}}")

        sys.exit(0)

    except httpx.HTTPStatusError as e:
        message = f"HTTP error: {{e.response.status_code}} - {{e.response.text}}"
        if output_json:
            click.echo(json.dumps({{"error": message}}))
        else:
            click.echo(f"Error: {{message}}", err=True)
        sys.exit(1)

    except httpx.RequestError as e:
        message = f"Network error: {{str(e)}}"
        if output_json:
            click.echo(json.dumps({{"error": message}}))
        else:
            click.echo(f"Error: {{message}}", err=True)
        sys.exit(1)

    except Exception as e:
        message = f"Unexpected error: {{str(e)}}"
        if output_json:
            click.echo(json.dumps({{"error": message}}))
        else:
            click.echo(f"Error: {{message}}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
"""
    return content


# -------------------------
# Content generators (Script)
# -------------------------


def generate_script_content(
    *,
    name: str,
    binary: str,
    api_base_url: str,
    endpoint: str,
    params: list[ParamSpec],
    description: str | None,
    include_simulate: bool,
) -> str:
    func_suffix = snake(name)
    method_name = f"fetch_{func_suffix}"
    user_agent = f"{binary}-script/1.0"

    # Build click options
    option_lines = []
    signature_names = []
    param_for_query = []

    for p in params:
        if p.type == "bool":
            default_expr = (
                "False"
                if p.required
                else python_cast_value("bool", p.default or "false")
            )
            option_lines.append(
                dedent(
                    f"""
                    @click.option(
                        "--{p.name}",
                        is_flag=True,
                        default={default_expr},
                        show_default=True,
                        help="Boolean flag parameter: {p.name}",
                    )
                    """.rstrip()
                )
            )
            signature_names.append(f"{p.name}: bool")
            param_for_query.append(f'"{p.name}": {p.name}')
        else:
            click_typ = (
                f"click.{click_type(p.type).capitalize()}"
                if p.type in {"int", "float"}
                else click_type(p.type)
            )
            if p.required:
                option_lines.append(
                    dedent(
                        f"""
                        @click.option(
                            "--{p.name}",
                            type={click_typ},
                            required=True,
                            help="Required parameter: {p.name}",
                        )
                        """.rstrip()
                    )
                )
            else:
                default_expr = (
                    python_cast_value(p.type, p.default)
                    if p.default is not None
                    else "None"
                )
                show_default = "True" if p.default is not None else "False"
                option_lines.append(
                    dedent(
                        f"""
                        @click.option(
                            "--{p.name}",
                            type={click_typ},
                            default={default_expr},
                            show_default={show_default},
                            help="Optional parameter: {p.name}",
                        )
                        """.rstrip()
                    )
                )
            signature_names.append(f"{p.name}")
            param_for_query.append(f'"{p.name}": {p.name}')

    # --json option
    option_lines.append(
        dedent(
            """
            @click.option(
                "--json",
                "output_json",
                is_flag=True,
                help="Emit strict JSON on stdout (no logs). Human-readable output otherwise.",
            )
            """.rstrip()
        )
    )
    # --simulate option (optional)
    if include_simulate:
        option_lines.append(
            dedent(
                """
                @click.option(
                    "--simulate",
                    is_flag=True,
                    help="Return stub data instead of making a network call.",
                )
                """.rstrip()
            )
        )

    options_blob = "\n".join(option_lines)
    signature = ", ".join(
        signature_names + ["output_json"] + (["simulate"] if include_simulate else [])
    )
    params_blob = (
        ",\n                    ".join(param_for_query) if param_for_query else ""
    )

    desc_line = description.strip() if description else f"{name} script"

    simulate_stub = ""
    if include_simulate:
        simulate_stub = dedent(
            f"""
            if simulate:
                data = {{
                    "endpoint": {repr(endpoint)},
                    "params": {{
{indent(params_blob, "                        ")}
                    }},
                    "items": [{{"id": "ex_1"}}, {{"id": "ex_2"}}],
                    "_note": "Simulated data. Wire up real HTTP logic and remove --simulate.",
                }}
            else:
                with Client() as client:
                    data = client.{method_name}({", ".join([p.name for p in params])})
            """
        ).strip()
    else:
        simulate_stub = f"with Client() as client:\n            data = client.{method_name}({', '.join([p.name for p in params])})"

    content = f"""#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx",
#     "click",
# ]
# ///

\"\"\"{desc_line}.
Self-contained script with minimal HTTP client.

Conventions:
- `--help` shows options
- `--json` prints strict JSON on stdout (no logs)
- Exit 0 on success; exit 1 on failure
- Keep code ~200–300 lines when possible to reduce context
\"\"\"

import json
import sys
from typing import Any, Dict, Optional

import click
import httpx

API_BASE_URL = {repr(api_base_url)}
API_TIMEOUT = 30.0
USER_AGENT = {repr(user_agent)}
DEFAULT_HEADERS = {{
    "User-Agent": USER_AGENT,
    # Add auth headers here if needed; prefer env vars/secure stores.
}}

class Client:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL, timeout=API_TIMEOUT, headers=DEFAULT_HEADERS)

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb):
        self.client.close()

    def {method_name}(self, {", ".join([p.name for p in params])}) -> Dict[str, Any]:
        \"\"\"
        Replace this implementation with your real logic.
        Keep return shape consistent with your CLI and MCP surfaces.
        \"\"\"
        resp = self.client.get(
            {repr(endpoint)},
            params={{
{indent(params_blob, "                ")}
            }},
        )
        resp.raise_for_status()
        return resp.json()


def format_human(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("{name} Results")
    lines.append("=" * 40)
    lines.append(f"endpoint: {endpoint}")
    # For lists, show a count; adjust for your real schema
    count = len(data) if isinstance(data, list) else (len(data.get("items", [])) if isinstance(data, dict) else "N/A")
    lines.append(f"count:    {{count}}")
    return "\\n".join(lines)


@click.command()
{options_blob}
def main({signature}):
    \"\"\"{desc_line}.\"\"\"
    try:
        {simulate_stub}

        if output_json:
            click.echo(json.dumps(data))
        else:
            click.echo(format_human(data))
        sys.exit(0)

    except httpx.HTTPStatusError as e:
        msg = f"HTTP error: {{e.response.status_code}} - {{e.response.text}}"
        if output_json:
            click.echo(json.dumps({{"error": msg}}))
        else:
            click.echo(f"❌ Error: {{msg}}", err=True)
        sys.exit(1)

    except httpx.RequestError as e:
        msg = f"Network error: {{str(e)}}"
        if output_json:
            click.echo(json.dumps({{"error": msg}}))
        else:
            click.echo(f"❌ Error: {{msg}}", err=True)
        sys.exit(1)

    except Exception as e:
        msg = f"Unexpected error: {{str(e)}}"
        if output_json:
            click.echo(json.dumps({{"error": msg}}))
        else:
            click.echo(f"❌ Error: {{msg}}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
    return content


# -------------------------
# Documentation generators
# -------------------------


def generate_test_plan_content(*, binary: str) -> str:
    return dedent(f"""\
    # End-to-End Test and Validation Plan

    Scope
    - Validate parity, reliability, and ergonomics across four capability surfaces:
      1) MCP Server (wrapping CLI via subprocess)
      2) CLI (canonical API logic and JSON contracts)
      3) File‑System Scripts (self‑contained, progressive disclosure)
      4) Claude Skills (autonomous discovery; wraps scripts)
    - Ensure behavior remains additive—MCP remains available.

    Guiding Principles
    - CLI is the canonical source for remote I/O and JSON.
    - MCP wraps CLI via subprocess (no duplicate HTTP logic).
    - Scripts remain self-contained (no shared project imports).
    - Skills document triggers and default to --json for processing.
    - Strict JSON in machine mode; no stdout noise.

    Test Categories
    1) Parity Checks
       - For each capability/tool:
         - Execute CLI subcommand with representative params; capture JSON.
         - Execute corresponding script with same params; capture JSON.
         - Execute MCP tool (which calls CLI); capture JSON.
         - Compare golden outputs for structural and key field equivalence.
       - Verify parameter semantics: required vs optional, defaults, ranges.

    2) Error and Exit Codes
       - CLI: simulate validation errors (missing required, invalid enum/range).
         - Expect exit 1, JSON error envelope under --json.
       - Scripts: same as CLI.
       - MCP: Ensure subprocess non-zero translates to structured error.
       - Verify no stdout noise in --json mode across CLI/scripts.
       - Confirm consistent error messages (stable shape).

    3) Pagination and Cursors
       - For list endpoints, verify:
         - Default limit applied
         - Cursor propagation (next/prev) where applicable
         - CLI and scripts return identical pagination behavior
         - MCP surfaces identical fields via CLI

    4) Caching (if applicable)
       - If CLI implements caching:
         - First call latency vs subsequent calls
         - TTL respected; refresh behavior with --refresh flag (if implemented)
         - No stale data after TTL expiration
         - Scripts may opt for lightweight cache; document paths and sizes

    5) Performance and Token Hygiene
       - Measure payload sizes (CLI and scripts) with default vs --full modes (if available)
       - Ensure human-readable output remains concise
       - Confirm that skills default to --json and avoid reading code unless necessary

    6) Security and Configuration
       - Ensure no secrets are logged or printed in --json mode
       - For authenticated endpoints (if any):
         - Validate env var-based configuration
         - Confirm minimal scopes; verify failure behavior with missing/invalid creds

    7) Claude Skills: Trigger and Behavior
       - Confirm SKILL.md triggers align with user phrasing
       - Prompt Claude Code with domain-relevant phrases to ensure autonomous invocation
       - Ensure scripts are invoked with --json
       - Validate that skills do not read code unless strictly needed (progressive disclosure)

    8) Documentation Consistency
       - Check that --help for CLI and scripts shows accurate flags, defaults, examples
       - Verify mapping sheets are up-to-date per tool
       - Confirm README “Pick your path” links are discoverable and correct

    9) CI Integration
       - Add a job to run unit/integration tests for CLI and scripts
       - Optional: Golden output checks (snapshot testing) for a subset of commands
       - Linting and basic static checks (flake8/ruff, mypy optional)
       - Ensure test suite fails on non-zero exit or malformed JSON

    Sample Test Commands
    - CLI:
      - uv run {binary} example --json
      - uv run {binary} example --param1 foo --limit 5 --json
    - Scripts:
      - uv run scripts/example.py --param1 foo --limit 5 --json
    - MCP:
      - Use MCP inspector/dev tooling to call the corresponding tool and compare output to CLI JSON

    Exit Criteria
    - 100% parity for the chosen capability set across CLI/scripts/MCP
    - Error and exit code behavior validated and consistent
    - Skill triggers verified via manual prompts
    - Docs updated; mapping sheets exist for each tool

    Ownership and Change Management
    - Treat CLI as the single source of truth for API logic and JSON contracts
    - Pin MCP to a compatible CLI version (if versioning introduced)
    - Scripts mirror CLI semantics; keep self-contained
    - Update mapping sheets, changelog, and --help epilogues on changes

    Attribution
    - This plan builds on patterns inspired by the beyond-mcp repository by IndyDevDan (additive approach).
    """)


def generate_generator_usage_content() -> str:
    return dedent("""\
    # CLI/Script Generator Usage

    This generator scaffolds:
    - A CLI subcommand (Click + httpx)
    - A self-contained file-system script (Click + httpx)
    - Optional documentation (test/validation plan, usage snippet)

    Basic Usage
    ```bash
    python migration_guide/templates/generate_cli_script.py <name> \\
      --target both \\
      --binary yourcmd \\
      --endpoint /v1/example \\
      --api-base-url https://api.example.com \\
      --param limit:int:10 \\
      --param query:str \\
      --out-cli ./apps/2_cli/<name>.py \\
      --out-script ./apps/3_file_system_scripts/scripts/<name>.py \\
      --emit-test-plan ./migration_guide/test_validation_plan.md \
    ```

    Param Spec
    - Format: name:type[:default]
      - If default omitted, parameter is required
      - Supported types: str, int, float, bool
    - Examples:
      - --param limit:int:10
      - --param query:str
      - --param exact:bool:true

    Tips
    - Keep parameter names and defaults consistent with MCP and Skills.
    - Prefer clean JSON outputs and minimal stdout noise for automation.
    - For Skills, default to --json and add clear “When to use” bullets.
    """)


# -------------------------
# CLI entry point
# -------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a CLI subcommand and/or a self-contained script from templates.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "name",
        help="Capability name (used for subcommand and script). Example: markets",
    )
    parser.add_argument(
        "--target",
        choices=["cli", "script", "both"],
        default="both",
        help="What to generate (default: both)",
    )
    parser.add_argument(
        "--binary",
        default="yourcmd",
        help="CLI binary name for user agent strings (default: yourcmd)",
    )
    parser.add_argument(
        "--endpoint",
        default="/example",
        help="API path for HTTP call (default: /example)",
    )
    parser.add_argument(
        "--api-base-url",
        default="https://example.com/api",
        help="Base URL for HTTP client (default: https://example.com/api)",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Parameter spec 'name:type[:default]'. Repeatable.",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="One-line description for the subcommand/script",
    )
    parser.add_argument(
        "--out-cli",
        default=None,
        help="Output path for generated CLI file (e.g., ./apps/2_cli/<name>.py)",
    )
    parser.add_argument(
        "--out-script",
        default=None,
        help="Output path for generated script file (e.g., ./apps/3_file_system_scripts/scripts/<name>.py)",
    )
    parser.add_argument(
        "--no-simulate",
        action="store_true",
        help="Do not include --simulate in the script",
    )
    parser.add_argument(
        "--emit-test-plan",
        default=None,
        help="Path to write a comprehensive test_validation_plan.md",
    )
    parser.add_argument(
        "--emit-doc-snippets",
        default=None,
        help="Path to write a GENERATOR_USAGE.md snippet",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without writing files"
    )

    args = parser.parse_args(argv)

    cap_name = snake(args.name)
    if not valid_identifier(cap_name):
        eprint(f"Invalid name after normalization: '{cap_name}'")
        return 2

    try:
        params = parse_params(args.param)
    except Exception as e:
        eprint(str(e))
        return 2

    # Defaults for output paths
    out_cli = Path(args.out_cli) if args.out_cli else Path(f"./cli_{cap_name}.py")
    out_script = (
        Path(args.out_script) if args.out_script else Path(f"./scripts/{cap_name}.py")
    )

    try:
        if args.target in {"cli", "both"}:
            cli_content = generate_cli_content(
                name=cap_name,
                binary=args.binary,
                api_base_url=args.api_base_url,
                endpoint=args.endpoint,
                params=params,
                description=args.description,
            )
            write_file(out_cli, cli_content, force=args.force, dry_run=args.dry_run)

        if args.target in {"script", "both"}:
            script_content = generate_script_content(
                name=cap_name,
                binary=args.binary,
                api_base_url=args.api_base_url,
                endpoint=args.endpoint,
                params=params,
                description=args.description,
                include_simulate=not args.no_simulate,
            )
            write_file(
                out_script, script_content, force=args.force, dry_run=args.dry_run
            )

        if args.emit_test_plan:
            test_plan_path = Path(args.emit_test_plan)
            write_file(
                test_plan_path,
                generate_test_plan_content(binary=args.binary),
                force=args.force,
                dry_run=args.dry_run,
            )

        if args.emit_doc_snippets:
            doc_snippet_path = Path(args.emit_doc_snippets)
            write_file(
                doc_snippet_path,
                generate_generator_usage_content(),
                force=args.force,
                dry_run=args.dry_run,
            )

        print("Done.")
        return 0

    except FileExistsError as e:
        eprint(str(e))
        return 3
    except Exception as e:
        eprint(f"Failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
