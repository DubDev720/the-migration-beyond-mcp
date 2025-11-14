# Generalized Migration Guidelines:
# Converting an MCP Server into: CLI tools, Fine‑Grained File‑System Scripts, and Claude Skills

Note: This comprehensive playbook has been superseded by format-specific, standalone guides. Use these for authoritative instructions:
- migration_guide/guide_cli_migration.md — MCP → CLI
- migration_guide/guide_file_system_scripts_migration.md — MCP → File‑System Scripts
- migration_guide/guide_claude_skills_migration.md — MCP → Claude Skills
- migration_guide/migration_split_and_docs_plan.md — Decide which tools map to which formats; structure separate end-user docs and agent permissions.

This document remains as a deep reference and aggregated background but will be phased out after the refactor.

This guide expands on the excellent beyond-mcp examples by IndyDevDan and adds a generalized, end‑to‑end migration playbook so you can:
- migrate an existing MCP server into a 1:1 CLI,
- extract fine‑grained, self‑contained file‑system scripts,
- and publish the same capabilities as Claude Skills.

These three targets can co‑exist and reinforce each other. Use this as an addition to the beyond-mcp repository—not a replacement.

References to the beyond-mcp exemplars:
- Original MCP server: `beyond-mcp/apps/1_mcp_server`
- CLI: `beyond-mcp/apps/2_cli`
- File‑system scripts: `beyond-mcp/apps/3_file_system_scripts`
- Claude skill: `beyond-mcp/apps/4_skill`

Owner/creator attribution: beyond-mcp by "IndyDevDan".


## 0. Executive Summary

- Problem: MCP servers concentrate capability behind protocol boundaries that may be overkill for many agents and LLM runtimes (extra process, transport overhead, context loss across calls).
- Strategy: Split capabilities into three transport‑agnostic surfaces:
  1) CLI: 1:1 mapping of commands to underlying APIs with clean JSON output for automation.
  2) File‑system scripts: fine‑grained, self‑contained scripts (single‑file, zero shared runtime) that support progressive disclosure and minimal context footprint.
  3) Claude skills: a discoverable, autonomous activation layer that wraps the scripts for Claude Code agents.

- Outcome: Greater reuse, simpler ops (no server process), faster iteration, and better context hygiene while still retaining a robust MCP option when appropriate.


## 1. Audience

- Teams maintaining existing MCP servers who want lighter‑weight alternatives
- Agent developers targeting Claude Desktop/Code, CLI workflows, or plain shell automation
- Platform engineers seeking clear factoring boundaries and progressive disclosure patterns
- Security‑minded devs who prefer the file‑system and least‑privilege compositions


## 2. Glossary

- MCP: Model Context Protocol; a transport and schema for tool servers talking to LLM clients.
- CLI: Command‑line interface; callable program with subcommands, flags, and JSON output mode.
- File‑system scripts: Self‑contained scripts (one file per capability) designed for minimal coupling.
- Claude Skills: Project‑local, file‑based skill definitions and scripts that Claude can auto‑discover and invoke.


## 3. Migration Principles

- 1:1 mappings first: Maintain behavioral parity with the MCP tools before refactoring.
- Single source of truth for remote I/O: Centralize direct HTTP logic in the CLI layer; let MCP wrap the CLI (subprocess) whenever possible.
- Progressive disclosure: Default to reading metadata/help over full code; only load/inspect code when strictly needed.
- Context hygiene: Prefer JSON output and avoid nonessential logging; let the agent consume small, structured blobs.
- Decomposition over inheritance: Scripts should be self‑contained; avoid deep shared libs across scripts unless you must.
- Backwards compatible by default: Keep MCP functional—this is an addition, not a replacement.


## 4. When to Migrate (Decision Matrix)

- Choose CLI as your first target when:
  - You need portability across shells, CI, and MCP servers
  - You want one canonical place for HTTP logic, retries, and JSON output
  - You need uniform automation and piping into other tools

- Choose file‑system scripts when:
  - You want ultra‑low overhead, progressive disclosure, minimal context
  - You want zero shared state between tools (safer, easier to reason about)
  - You want a “drop-in” folder that any agent/runtime can call

- Choose Claude skills when:
  - You are targeting Claude Code and want autonomous discovery
  - You want to share capabilities with your team via git
  - You want the “no server, no setup” developer ergonomics

- Keep MCP when:
  - You explicitly need MCP transport features, streaming, or managed tool catalogs
  - You already ship MCP to users and want a compatible path forward
  - You want MCP → CLI subprocess calls as a compatibility layer


## 5. High‑Level Migration Phases

1) Discovery: inventory current MCP tools, parameters, and outputs
2) Analysis: confirm API endpoints, auth shape, pagination, and error semantics
3) Design: define equivalent CLI commands, script names, and skill entrypoints
4) Implementation: build CLI, then scripts, then skill wrapper
5) Validation: confirm parity, JSON schemas, and error/exit codes
6) Rollout: ship CLI/scripts/skill alongside MCP; document usage
7) Optimization: add caching, batching, and context reduction strategies


## 6. Detailed Steps

### Phase 1: Discovery

- List all MCP tools and their parameters.
- Capture input validation rules, defaults, and shapes of returned JSON.
- Note cross‑cutting features: pagination, filtering, cursoring, caching, rate limits.

Quick crosswalk in beyond-mcp:
- MCP tools live in `beyond-mcp/apps/1_mcp_server/server.py` (wrap CLI via subprocess).
- CLI commands live in `beyond-mcp/apps/2_cli/kalshi_cli/cli.py` with modules under `kalshi_cli/modules`.
- File‑system scripts live in `beyond-mcp/apps/3_file_system_scripts/scripts/`.
- Claude skill lives in `beyond-mcp/apps/4_skill/.claude/skills/kalshi-markets/` with `SKILL.md` and scripts.

### Phase 2: Analysis

- Confirm each MCP tool maps to exactly one CLI subcommand.
- Ensure the CLI supports a `--json` mode that prints pure JSON (no logs).
- Decide which script boundary is “one file per capability.”
- For Claude skills, identify which trigger keywords and descriptions help autonomous invocation.

### Phase 3: Design

Design the 1:1 CLI surface:
- Subcommand naming mirrors the MCP tool name (or domain nouns/verbs that match user intent).
- Flags map to MCP parameters; use sensible defaults and clear help text.
- All commands support `--json`.

Design file‑system scripts:
- One file per capability with its own tiny HTTP client.
- Each script supports `--help` and `--json`.
- No shared internal imports between scripts unless necessary (keep them portable).

Design Claude skill:
- `SKILL.md` declares name, description, and high‑signal triggers.
- Scripts placed under `.claude/skills/<skill-name>/scripts/`.
- Instructions emphasize progressive disclosure and default to `--json`.

### Phase 4: Implementation

Order of operations:
1) Build/confirm the CLI surface (the canonical API logic).
2) Update MCP server to call the CLI (subprocess + JSON parse).
3) Extract file‑system scripts (lift logic into self‑contained single files).
4) Add Claude skill wrapper that points to the scripts and documents intent triggers.

Examples mirrored by beyond-mcp (attribution: IndyDevDan):
- MCP wrapping CLI: `beyond-mcp/apps/1_mcp_server` calls into `apps/2_cli` via subprocess.
- CLI with `httpx`, JSON, and caching: `beyond-mcp/apps/2_cli`.
- Ten standalone scripts: `beyond-mcp/apps/3_file_system_scripts/scripts/*.py`.
- Claude skill entry with `SKILL.md`: `beyond-mcp/apps/4_skill/.claude/skills/kalshi-markets/`.

### Phase 5: Validation

- For each MCP tool, exercise the equivalent CLI command and script; compare JSON.
- Validate error handling:
  - CLI non‑zero exit codes on failure
  - Scripts emit JSON error envelopes if `--json` used
  - MCP converts subprocess errors to structured errors
- Smoke test Claude skill with prompts likely to trigger it.

### Phase 6: Rollout

- Keep MCP in place; document the three new surfaces as additions.
- Provide a “pick your path” section for users (MCP, CLI, scripts, Claude skill).
- Encourage contributors to add new capabilities first to CLI, then wire into MCP/scripts/skill.

### Phase 7: Optimization (Optional)

- Add caching on read‑heavy endpoints (consider TTL and invalidation strategy).
- Batched calls where possible (reduce API round‑trips).
- Schema trims: return only fields most often used; keep `--raw` or `--full` for complete payloads.


## 7. Tool Type Conversion Patterns

From an MCP tool shape:
- Name → CLI subcommand → Script filename → Skill bullet
- Parameters → CLI flags → Script options → Documented in `SKILL.md`
- Return dict → stdout JSON → stdout JSON → Agent‑consumable JSON

Pattern examples (see beyond-mcp for live code):
- MCP `get_exchange_status` → CLI `status` → Script `status.py` → Skill script `status.py`
- MCP `list_markets` → CLI `markets` → Script `markets.py` → Skill script `markets.py`
- MCP `search_markets` → CLI `search` → Script `search.py` → Skill script `search.py`


## 8. Script Design Standards

- Self‑contained single file; embed the minimal HTTP client and options parsing.
- Support `--json` for machine consumption; default is human‑readable.
- Don’t import shared project utilities; prefer local constants.
- Exit with 0 on success; non‑zero on meaningful failure.
- Keep code clear and discoverable with `--help`.

Example headings to include in each script:
- Short description and usage
- Options (flags, defaults)
- Example invocations (inline comments)
- Structured output description


## 9. Parameter Mapping Guidelines

- Keep semantics identical across MCP, CLI, scripts, and skills.
- Use explicit types in help text and validations (ints, enums, timestamps).
- Normalize naming: `--series-ticker`, `--event-ticker`, `--limit`, `--cursor`.
- Favor additive flags with defaults over positional parameters for clarity.
- Preserve pagination/cursor behavior intact.


## 10. Error & Exit Code Conventions

- CLI and scripts:
  - exit 0 on success
  - exit 1 on expected operational failures (validation, not found, API error)
  - print JSON error envelope when `--json` is provided; otherwise a concise human message

- MCP:
  - Convert subprocess non‑zero to structured MCP tool errors with meaningful messages
  - Include stderr in diagnostics when safe

- Keep error messages stable where possible; avoid leaking sensitive data.


## 11. Security Considerations

- Default read‑only if possible; scope tokens if/when you add auth.
- Avoid writing credentials to disk; prefer env vars or secure stores.
- Validate/whitelist external URLs; do not accept arbitrary endpoints from user input.
- For scripts, avoid unintended file system writes; keep them read‑only unless clearly documented.


## 12. Progressive Disclosure Techniques

- In Claude skills, instruct the agent to call `--help` first and only open code files when strictly necessary.
- Keep scripts ~200–300 lines when possible to minimize context overhead.
- Provide concise `--help` with examples so the model avoids opening code to learn usage.
- Document that `--json` is the default for agent processing; human output is a bonus for developers.


## 13. Context Consumption Optimization

- Always support `--json` and avoid noisy logging on stdout (stderr for human diagnostics).
- Use narrow default field sets for list endpoints; add `--full` to expand if needed.
- When returning large collections, default to `--limit` plus a `--cursor` for follow‑up calls.


## 14. Caching Strategies

- CLI-level caching for compute‑heavy fetches (e.g., search indexing); expose TTL and eager/refresh options.
- Make caching explicit in help text so users know the first call may be slow but subsequent calls are instant.
- For scripts, consider lightweight on‑disk caches per capability; document size, path, and TTL.


## 15. Testing Methodology

- Golden JSON comparisons across MCP → CLI → scripts for a representative sample.
- Contract tests for parameter validation and error shapes.
- Smoke tests for Claude skill triggers (manually prompt strategic keywords).
- CI: run CLI and script tests; optionally launch MCP in test mode and exercise tools.


## 16. Refactoring Thresholds

- Only refactor shared helpers when duplication is provably harmful.
- Prefer duplicating <50 lines of simple code over adding cross‑script dependencies.
- If a helper must exist, keep it tiny, stable, and documented.


## 17. Versioning Strategy

- Tag the CLI when you add or change commands/flags.
- Keep MCP server pinned to a compatible CLI version.
- Scripts are versionless by default; use repo tags/releases to track changes.
- Note breaking changes clearly in CHANGELOG and `--help` epilogues.


## 18. Agent Priming Templates

Claude Skill SKILL.md starter (customize per domain):

```/dev/null/SKILL.md#L1-80
---
name: your-skill-name
description: Short, actionable description. Include nouns/verbs that will appear in user prompts.
---

# Your Skill Name

Self-contained scripts for <your domain>. Each script is independently executable with zero shared dependencies.

## Instructions

- Default to `--json` for all commands when processing data
- Prefer `--help` to discover options; only read code when necessary
- Use smallest sufficient command and limit results to reduce context

## Triggers

- "keywords"
- "problem phrases"
- "domain terms"

## Available Scripts

### scripts/foo.py
When to use: <one-line intent>
### scripts/bar.py
When to use: <one-line intent>
```

CLI help footer ideas:

```/dev/null/cli-help.txt#L1-40
Examples:
  uv run yourcmd status --json
  uv run yourcmd list --limit 10 --json | jq '.items[] | {id, name}'
Notes:
  - Use --json for automation. Human output is concise by default.
  - List endpoints accept --limit and --cursor for pagination.
```


## 19. Anti‑Patterns to Avoid

- Over‑centralizing logic into shared libraries that every script must import.
- Printing logs to stdout during `--json` mode (breaks parsers).
- Mutating global state or writing to disk in unexpected places.
- Diverging parameter semantics between MCP/CLI/scripts/skill.
- Hiding important options solely in README; ensure `--help` is complete.


## 20. Checklist (Master)

Discovery
- [ ] Inventory all MCP tools, params, and outputs
- [ ] Identify pagination/cursor and caching needs

Design
- [ ] Define CLI subcommands and flags (1:1 with MCP tools)
- [ ] Choose script filenames (one per capability)
- [ ] Draft SKILL.md with triggers and usage guidance

Implementation
- [ ] Implement CLI with `--json` and helpful `--help`
- [ ] Update MCP to wrap CLI via subprocess
- [ ] Extract self‑contained scripts with `--json` and `--help`
- [ ] Add Claude skill folder and SKILL.md

Validation
- [ ] Parity tests across MCP, CLI, and scripts
- [ ] Error/exit code checks
- [ ] Manual skill trigger prompts

Rollout
- [ ] Update docs with “pick your path” guidance
- [ ] Announce non‑breaking addition; MCP remains available

Optimization
- [ ] Add caching where beneficial
- [ ] Tune default fields and limits


## 21. Worked Example Using beyond-mcp (Attribution: IndyDevDan)

- Original MCP server: `beyond-mcp/apps/1_mcp_server/server.py`
  - Uses FastMCP
  - Wraps the CLI with subprocess
  - Exposes a tool per command

- CLI: `beyond-mcp/apps/2_cli`
  - `kalshi_cli/cli.py` implements commands with `httpx`
  - `--json` for clean machine output
  - Search uses an intelligent cache

- File‑system scripts: `beyond-mcp/apps/3_file_system_scripts/scripts/`
  - Ten single‑file scripts (e.g., `status.py`, `markets.py`, `search.py`)
  - Self‑contained HTTP clients
  - `--help` and `--json` for discoverability and automation

- Claude skill: `beyond-mcp/apps/4_skill/.claude/skills/kalshi-markets/`
  - `SKILL.md` defines description and triggers
  - Scripts mirror the file‑system approach
  - Emphasizes progressive disclosure


## 22. FAQ (Generalized)

Q: Should I keep my MCP server?
- Yes. This is additive. MCP can remain a consumer of your canonical CLI, which stabilizes maintenance.

Q: Why a CLI first?
- It’s the most portable and easiest to adopt across environments, tests, CI, and MCP subprocess calls.

Q: Why separate scripts if I have a CLI?
- Scripts prioritize minimal context and discoverability. They are zero‑setup, small, and safe to open in agents.

Q: Do Claude skills replace the scripts?
- Skills wrap scripts for autonomous discovery by Claude. They’re complementary; keep both.

Q: How big should scripts be?
- Aim for 200–300 lines; keep them single‑purpose and self‑contained.


## 23. Migration Timeline Template (Example)

- Week 1: Inventory MCP tools; design CLI surface; scaffold CLI; ship 2–3 commands
- Week 2: Complete CLI; switch MCP to wrap CLI; parity tests
- Week 3: Extract scripts for top 5 capabilities; add Claude skill and SKILL.md
- Week 4: Finish remaining scripts; add caching and context optimizations; harden docs


## 24. Success Metrics

- Parity: 100% MCP tools available as CLI commands and scripts
- Reliability: Non‑zero exit on failure; JSON error envelopes in `--json` mode
- Context: Reduced tokens per operation; agent avoids opening code except when needed
- Adoption: More contributors can add/modify commands without touching MCP internals


## 25. Final Recommendations

- Treat the CLI as canonical for remote I/O and JSON contracts.
- Keep MCP as a wrapper when MCP is required; otherwise, prefer scripts and skills for simplicity.
- Optimize for discoverability (`--help`, `SKILL.md`, concise READMEs) and context hygiene (`--json`, small results).
- Build once, surface three ways: MCP, CLI, Scripts/Skills.


## 26. Quick Start Summary (Condensed)

- Start with your existing MCP server.
- Design a CLI that mirrors each MCP tool.
- Update MCP to call the CLI via subprocess and parse JSON.
- Extract self‑contained scripts per capability.
- Add a Claude skill that wraps those scripts with clear triggers.

See beyond-mcp by IndyDevDan for a practical, fully‑worked reference:
- MCP server: `beyond-mcp/apps/1_mcp_server`
- CLI: `beyond-mcp/apps/2_cli`
- File‑system scripts: `beyond-mcp/apps/3_file_system_scripts`
- Claude skill: `beyond-mcp/apps/4_skill`

## 27. Per-Tool Mapping Template

Use this template to keep parity across MCP → CLI → Scripts → Skill.

```/dev/null/per-tool-mapping-template.md#L1-120
# Per-Tool Mapping Sheet

MCP Tool
- Name: <mcp_tool_name>
- Purpose: <single-line intent>
- Inputs (type, required, default): 
  - <param1>: <type> (<required?>, default=<default>)
  - <param2>: <type> (<required?>, default=<default>)
- Output: <JSON schema summary>
- Notes: <pagination/cursor, caching, auth, rate limits>

CLI Command
- Command: <binary> <subcommand>
- Flags:
  - --<flag1> <type> (default=<default>) → maps to <param1>
  - --<flag2> <type> (default=<default>) → maps to <param2>
- Output modes: --json (pure JSON), human (concise)
- Exit codes: 0 success, 1 failure
- Examples:
  - uv run <binary> <subcommand> [flags] --json

File-System Script
- Filename: scripts/<script_name>.py
- Options:
  - --<option1> (maps to <param1>)
  - --<option2> (maps to <param2>)
  - --json
- Behavior:
  - Prints JSON when --json used
  - Non-zero exit on failure
- Notes: self-contained HTTP client, progressive disclosure via --help

Claude Skill
- Skill: .claude/skills/<skill-name>/
- Script: .claude/skills/<skill-name>/scripts/<script_name>.py
- SKILL.md bullets:
  - "<when to use>" aligned to user phrasing
  - default to --json for processing
- Triggers:
  - "<keyword1>", "<keyword2>", "<domain term>"
```

Example filled-out mapping (referencing beyond-mcp by IndyDevDan):

```/dev/null/example-per-tool-mapping-kalshi.md#L1-120
MCP Tool
- Name: get_exchange_status
- Purpose: Current Kalshi exchange/trading status
- Inputs: none
- Output: { exchange_active: bool, trading_active: bool, exchange_estimated_resume_time?: string }

CLI Command
- Command: kalshi status
- Flags: --json (pure JSON)
- Output: same JSON fields as above
- Exit codes: 0 if trading_active true, 1 otherwise

File-System Script
- Filename: scripts/status.py
- Options: --json
- Behavior: self-contained HTTP client; JSON/human output; exit 0/1 as above

Claude Skill
- Skill: kalshi-markets
- Script: .claude/skills/kalshi-markets/scripts/status.py
- SKILL.md bullet: "Check if Kalshi exchange is operational"
- Triggers: "prediction markets", "Kalshi markets", "exchange status"
```

## 28. Skeleton Generators (Templates)

Ready-to-copy scaffolds for adding new CLI subcommands and standalone scripts following the conventions in this guide.

### 28.1 CLI Subcommand Skeleton

- Purpose: Add a new subcommand to your CLI that supports `--json`, clean exit codes, and concise human output.
- Integration: Place into your CLI module and register under the root command group.

```/dev/null/cli_subcommand_skeleton.py#L1-160
#!/usr/bin/env python3
import json
import sys
import typing as t

import click
import httpx

@click.group()
def cli():
    "Your CLI root"


@cli.command("example")
@click.option("--param1", required=True, type=str, help="Example required parameter")
@click.option("--limit", default=10, show_default=True, type=int, help="Max items to return")
@click.option("--json", "output_json", is_flag=True, help="Emit pure JSON on stdout")
def example_cmd(param1: str, limit: int, output_json: bool):
    """
    Example subcommand template.
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            # Replace with your real endpoint/logic
            data = {"param1": param1, "limit": limit, "items": []}
        if output_json:
            click.echo(json.dumps(data))
        else:
            click.echo(f"param1={param1} limit={limit} items={len(data['items'])}")
        sys.exit(0)
    except Exception as e:
        if output_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
```

Usage:
- Add or import this command into your CLI root.
- Always test both human and `--json` modes.
- Ensure non-zero exit on failure for automation compatibility.

### 28.2 File‑System Script Skeleton

- Purpose: Ship a self‑contained script with its own minimal HTTP client, `--help`, `--json`, and progressive disclosure.
- Integration: Place in your scripts folder (e.g., `scripts/your_command.py`). Keep it independent of shared project modules when possible.

```/dev/null/script_skeleton.py#L1-200
#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx",
#     "click",
# ]
# ///

import json
import sys
from typing import Any, Dict

import click
import httpx

API_BASE_URL = "https://example.com/api"
API_TIMEOUT = 30.0
USER_AGENT = "Your-Script/1.0"

class Client:
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL, timeout=API_TIMEOUT, headers={"User-Agent": USER_AGENT})
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): self.client.close()

    def fetch_example(self, param1: str, limit: int) -> Dict[str, Any]:
        # Replace path and params with your real call
        r = self.client.get("/example", params={"param1": param1, "limit": limit})
        r.raise_for_status()
        return r.json()

def format_human(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("Example Results")
    lines.append("=" * 40)
    lines.append(f"param1: {data.get('param1')}")
    lines.append(f"count: {len(data.get('items', []))}")
    return "\n".join(lines)

@click.command()
@click.option("--param1", required=True, type=str, help="Example required parameter")
@click.option("--limit", default=10, show_default=True, type=int, help="Max items to return")
@click.option("--json", "output_json", is_flag=True, help="Emit pure JSON")
def main(param1: str, limit: int, output_json: bool):
    try:
        with Client() as c:
            data = c.fetch_example(param1, limit)
        if output_json:
            click.echo(json.dumps(data))
        else:
            click.echo(format_human(data))
        sys.exit(0)
    except Exception as e:
        if output_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Notes:
- Keep scripts self‑contained for portability and progressive disclosure.
- Ensure consistent parameter semantics across MCP, CLI, scripts, and skills.
- Default to `--json` for agent processing; provide concise human output for developers.

## 29. Generator Usage (Quick Start)

Use the provided generator to scaffold a CLI subcommand and/or a standalone script that conform to this guide’s conventions.

```/dev/null/usage.sh#L1-18
# Generate both a CLI subcommand and a standalone script
python migration_guide/templates/generate_cli_script.py markets \
  --target both \
  --binary yourcmd \
  --endpoint /v1/markets \
  --api-base-url https://api.example.com \
  --param limit:int:10 \
  --param query:str \
  --out-cli ./apps/2_cli/markets.py \
  --out-script ./apps/3_file_system_scripts/scripts/markets.py \
  --emit-test-plan ./migration_guide/TEST_VALIDATION_PLAN.md \
  --emit-doc-snippets ./migration_guide/GENERATOR_USAGE.md \
  --force
```

Tips:
- Keep parameter names/types/defaults consistent across MCP, CLI, scripts, and skills.
- Always test human and --json modes. Non-zero exit on failure.
- For Skills, default to --json and prefer calling --help over opening code.
