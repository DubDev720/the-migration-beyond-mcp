# Notice: This guide has been moved

This file has been relocated into the "refactor" folder as part of the documentation split.

Please use the new, format-specific guides:
- migration_guide/guide_cli_migration.md — MCP → CLI
- migration_guide/guide_file_system_scripts_migration.md — MCP → File‑System Scripts
- migration_guide/guide_claude_skills_migration.md — MCP → Claude Skills

And for planning multi-format vs single-format migrations and user-facing docs:
- migration_guide/migration_split_and_docs_plan.md — Decide which tools map to which formats and how to structure separate user documentation and agent permissions.

This legacy file remains temporarily to preserve links. Content below will be removed after the refactor is complete.

## 0. Executive Summary

Note: For a full MCP → CLI → File‑System Scripts → Claude Skills migration playbook (additive to this guide), see:
- migration_guide/mcp_to_scripts_migration.md

This document provides a repeatable, technology‑agnostic methodology for migrating an MCP server (one or more MCP tools) into a suite of standalone Python scripts. The migration aims to:

- Preserve or improve functionality
- Increase operator & developer control over what an AI agent can load
- Minimize context window consumption via progressive disclosure
- Improve portability (copy a single file to reuse a capability)
- Reduce coupling (remove protocol wrappers / framework dependencies)

The end state is a collection of self‑contained scripts (one responsibility per file) each optionally supporting human output and structured JSON (`--json`), enabling selective loading by agents or humans.

---

## 1. Audience

- Engineers maintaining MCP-based integrations who need more granular control.
- Teams optimizing AI agent performance (token efficiency, latency).
- Security / governance stakeholders needing selective exposure of internal capabilities.
- Tooling architects defining best practices for agent-facing code.

---
## Quick Reference: Which path should I pick?

- Use MCP when:
  - You need MCP protocol features (streaming, managed tool catalogs) or already ship MCP-compatible clients
  - You want to keep an existing MCP server while adding other surfaces (additive approach)

- Use CLI when:
  - You want a single canonical place for HTTP logic and JSON contracts
  - You need portability across shells, CI, and other automation (pipeable `--json`)

- Use File‑System Scripts when:
  - You want ultra‑low overhead, progressive disclosure, and minimal context usage
  - You prefer self‑contained, one‑file capabilities that are easy to read and audit

- Use Claude Skills when:
  - You’re targeting Claude Code and want autonomous discovery/activation
  - You want “no server, no setup” ergonomics and easy team sharing via git

Tip: Build once, surface three ways. Treat the CLI as canonical, keep MCP as a wrapper if needed, and offer scripts/skills for lightweight usage.
---

## 2. Glossary

| Term | Meaning |
|------|---------|
| MCP Tool | A callable interface exposed via Model Context Protocol. |
| Progressive Disclosure | Present only the minimal code/context needed for a specific operation. |
| Script | A self-contained Python file that performs one network / IO / transformation task. |
| Capability Surface | The set of operations an agent can invoke. |
| Context Footprint | Total tokens read/loaded by an agent to decide/perform an action. |
| Parity | Functional equivalence between MCP tool and script (inputs, outputs, semantics). |

---

## 3. Migration Principles

1. Single Responsibility: One script = one cohesive capability.
2. Self-Containment: No shared internal imports initially (prefer duplication for isolation).
3. Predictable Interface: Reuse MCP parameter names as command-line flags.
4. Dual Output Modes: Human-readable default + structured JSON via `--json`.
5. Uniform Error Shape: JSON mode errors always `{"error": "<message>"}`.
6. Deterministic Exit Codes: `0` success; non-zero for semantic or operational failures.
7. Minimal Dependencies: Prefer only `httpx`/`click` (add more only when justified).
8. Explicit Gradual Optimization: Start duplicated; refactor only after thresholds are met.
9. Version Visibility: Have script header comment with version/date.
10. Safe Extension: Adding a new capability never requires editing existing scripts (append-only growth).

---

## 4. When to Migrate (Decision Matrix)

| Driver | Indicators | Migrate? |
|--------|-----------|----------|
| Context Efficiency | Tools load large server file every invocation | Yes |
| Governance / Isolation | Need selective exposure per agent / per environment | Yes |
| Portability | Want copy & paste distribution without protocol | Yes |
| Latency | Protocol wrapper + subprocess overhead material | Yes |
| Complexity of Existing Server | Large multi-tool file hard to audit | Yes |
| Real-Time Streaming Needs | Server already optimized / uses streaming | Maybe (keep MCP) |
| Cross-Language Clients | Need standardized tool discovery across ecosystems | Retain MCP |
| Authentication Centralization | Shared auth logic easier in server | Consider hybrid |
| High Shared Utilities | Many tools share heavy logic | Delay migration (refactor first) |

---

## 5. High-Level Migration Phases

1. Discovery
2. Analysis
3. Design
4. Implementation
5. Validation
6. Rollout
7. Optimization (optional)

---

## 6. Detailed Steps

### Phase 1: Discovery
- Enumerate MCP tool functions (name, parameters, defaults, docstrings).
- Capture response schemas (example outputs).
- Identify shared utilities (HTTP client, caching, formatting).
- Note side effects (disk IO, network calls, environment usage).

### Phase 2: Analysis
- Classify tools:
  - Simple fetch (e.g., status, get_resource)
  - Filtered list / pagination
  - Mutation / write operations
  - Aggregate / composite operations
  - Long-running / cache-building
- Flag sensitive vs non-sensitive operations.
- Determine parameter patterns (required vs optional, enumerations).

### Phase 3: Design
- Define script naming: `verb_noun.py` or `noun_list.py` for lists.
- Decide parameter mapping → CLI flags.
- Establish baseline formatting conventions.
- Define error & exit code catalog.
- Choose duplication vs shared module (start with duplication).
- Plan cache strategy (if needed): location, TTL, rebuild triggers.

### Phase 4: Implementation
For each tool:
1. Create script header with description, usage, version.
2. Implement minimal HTTP/client & core operation.
3. Add CLI interface with `click`.
4. Provide `--json` flag.
5. Add human formatting (truncate long fields; show summary).
6. Standardize error handling.
7. Document edge cases (e.g., empty results; rate limits).
8. Keep LOC under threshold (≤250 lines recommended).

### Phase 5: Validation
- Functional parity tests: same inputs → same essential outputs.
- JSON schema comparison (order-insensitive).
- Error scenarios: invalid param, network failure, unexpected server response.
- Context measurement: token count before vs after migration.
- Performance measurement: latency difference (protocol removal).

### Phase 6: Rollout
- Introduce scripts alongside MCP server (dual mode).
- Update developer docs & agent priming prompts.
- Gradually shift agents to script invocation.
- Deprecate MCP server tools in phases (announce timeline).

### Phase 7: Optimization (Optional)
- Introduce shared library only after duplication causes measurable pain:
  - Bugs repeated ≥3 times
  - Maintenance overhead >30 min/week
  - >20 scripts carrying identical HTTP logic

---

## 7. Tool Type Conversion Patterns

| Tool Type | Script Strategy | Special Notes |
|-----------|-----------------|---------------|
| Simple GET | Single request; zero formatting complexity | Include semantic exit code if meaningful (e.g., status). |
| Paginated List | Add `--limit` and `--cursor` options | Display pagination hint in human mode. |
| Search / Composite | Cache build step (lazy) | Provide `--rebuild-cache` / `--stats`. |
| Mutation / POST | Add dry-run (`--dry-run`) flag | Clear warning in human mode before action. |
| Streaming / Long Poll | Consider whether script should stream or return snapshot | If streaming, maybe retain MCP for protocol features. |
| Bulk Fetch & Merge | Multi-call sequence with progress output | Add `--quiet` for agent usage. |

---

## 8. Script Design Standards

Header Block (Recommended):
```
#!/usr/bin/env python3
# script: <name>
# version: 2024-11-13
# purpose: <short purpose>
# dependencies: httpx, click
"""
<Concise description>
Usage Examples:
  uv run <script>.py --json ...
"""
```

Core Sections:
1. Constants (BASE_URL, TIMEOUT, HEADERS)
2. Client Class (context manager)
3. Operation Method(s)
4. Formatting Functions
5. CLI Entrypoint (`main()`)
6. `if __name__ == "__main__": main()`

LOC Budget:
- Keep under 250 lines initially.
- Split if script grows beyond single responsibility.

---

## 9. Parameter Mapping Guidelines

| MCP Param Type | CLI Representation | Rule |
|----------------|--------------------|------|
| Required identifier (id/ticker) | Positional argument | Keep order minimal (1–2 positional max). |
| Optional scalar | `--flag value` | Match MCP name exactly (snake-case). |
| Boolean | `--flag` (store_true) | Default = False. |
| Enum | `--flag` with `click.Choice([...])` | Provide same accepted values. |
| List / comma-separated | Single string flag | Do not parse unless necessary; let agent supply. |
| Timestamp / numeric | `int` type validation | Validate ranges early. |

---

## 10. Error & Exit Code Conventions

| Scenario | Human Output | JSON Output | Exit Code |
|----------|--------------|-------------|-----------|
| Success | Formatted result | Raw JSON / structured object | 0 |
| Validation error | `❌ Error: <detail>` | `{"error": "<detail>"}` | 2 |
| Network / HTTP | `❌ Error: API error <code>` | `{"error": "API error <code>: <text>"}` | 3 |
| Unexpected | `❌ Error: Unexpected: <detail>` | `{"error": "Unexpected: <detail>"}` | 4 |
| Semantic failure (e.g., inactive) | Clear status message | JSON with state | 1 |

Consistency aids agents in automated branching.

---

## 11. Security Considerations

| Aspect | Guidance |
|--------|----------|
| Secrets | Prefer env vars (e.g. `API_TOKEN`); add `--api-key` only if needed. |
| Logging | Avoid printing sensitive tokens or raw headers. |
| File Cache | Sanitize filenames; avoid user-supplied direct paths. |
| Network | Timeouts explicit; consider retry (bounded). |
| Validation | Strictly check numeric bounds to prevent resource abuse. |

---

## 12. Progressive Disclosure Techniques

- Each script self-contained → agent loads only what it needs.
- Avoid bundling unrelated utilities.
- Keep human description concise (top docstring ≤ 15 lines).
- Offer “extended help” via `--help` only (agent chooses to load).

---

## 13. Context Consumption Optimization

| Technique | Benefit |
|-----------|---------|
| Truncate long titles in human mode | Reduce tokens | 
| Use stable icons / status markers | Fast parsing by model |
| Avoid generic commentary | Prevent token waste |
| Provide summary first, details second | Agent can stop early |

---

## 14. Caching Strategies

| Pattern | Use Case | Notes |
|---------|----------|-------|
| Lazy build (first invocation) | Expensive enumeration (search) | Provide progress lines; optional `--quiet`. |
| Time-based TTL | Stale data acceptable for read/lookups | Store timestamp in metadata file. |
| Manual rebuild flag | Allow control when currency needed | `--rebuild-cache`. |
| Stats introspection | Agent decision gating | `--stats` interaction. |

Cache Directory Convention: Project root `.cache/<tool_name>/`.

---

## 15. Testing Methodology

| Test Type | Description | Tool |
|-----------|-------------|------|
| Parity | MCP output vs script JSON | Diff ignoring ordering |
| Error Injection | Invalid params / simulated network drop | Monkeypatch DNS / use invalid host |
| Performance | Latency measurement | Wrap with timing shell script |
| Token Footprint | Character count | `wc -c script.py` |
| Static Analysis | Basic lint (optional) | `ruff`, `flake8` |
| Copy Portability | Copy file to temp dir; run | Ensures no hidden relative assumptions |

---

## 16. Refactoring Thresholds

Trigger shared module creation only when BOTH:
- ≥3 scripts require identical bug fix OR improvement.
- Shared logic LOC duplication > 400 lines total.

Then:
- Introduce `shared_lib/` with stable versioned modules.
- Maintain backwards compatibility (never break existing script without version bump).

---

## 17. Versioning Strategy

| Element | Approach |
|---------|---------|
| Script Internal | `# version: YYYY-MM-DD` |
| Collection | Git tag `scripts-vX.Y.Z` |
| Breaking Changes | Rename or suffix `_v2.py` (avoid silent behavior drift) |
| Deprecation | Keep legacy for ≥1 release cycle with warning comment |

---

## 18. Agent Priming Template

Embed in docs or deliver as initial context:

```
You can invoke capabilities via standalone Python scripts.
Each script supports --json for structured output.
Load only scripts relevant to the current task.
Prefer human mode for quick inspection; use --json for chaining.
Check --help before invoking unfamiliar scripts.
```

---

## 19. Anti-Patterns to Avoid

| Anti-Pattern | Why Harmful |
|--------------|-------------|
| Giant “utils.py” central file early | Increases context load; defeats isolation. |
| Scripts importing each other | Hidden coupling; hinders portability. |
| Over-formatting (ASCII tables, colors) | Wastes tokens; harder for agent parsing. |
| Silent failures (exit 0 with error message) | Agents misinterpret; break automation. |
| Mixing unrelated operations (e.g., search + write) | Breaks single responsibility. |
| Over-eager DRY (premature abstraction) | Increases complexity; slows migration. |

---

## 20. Checklist (Master)

| Step | Status |
|------|--------|
| Inventory MCP tools | ☐ |
| Capture sample JSON outputs | ☐ |
| Classify tool types | ☐ |
| Define naming convention | ☐ |
| Draft script template | ☐ |
| Implement simple fetch scripts | ☐ |
| Implement list/paginated scripts | ☐ |
| Implement composite/search scripts | ☐ |
| Add JSON mode across all | ☐ |
| Standardize error handling | ☐ |
| Add exit code semantics | ☐ |
| Performance baseline recorded | ☐ |
| Parity tests passing | ☐ |
| Context footprint measured | ☐ |
| Documentation updated | ☐ |
| Agent priming prompt added | ☐ |
| Deprecation notice for MCP server (if retiring) | ☐ |

---

## 21. Example Pseudo-Case (Abstracted)

MCP Tool:
```
@mcp.tool()
def list_assets(limit: int = 10, category: Optional[str] = None) -> dict:
    ...
```

Script Equivalent (conceptual):

```
#!/usr/bin/env python3
# version: 2024-11-13
# dependencies: httpx, click
"""
List assets with optional category filter.
Usage:
  uv run assets_list.py --limit 25 --category equity
  uv run assets_list.py --json
"""
import sys, json, click, httpx

BASE_URL="https://api.example.com/v1"

class Client:
    def __init__(self):
        self.c=httpx.Client(base_url=BASE_URL, timeout=20)
    def __enter__(self): return self
    def __exit__(self,*a): self.c.close()
    def list_assets(self, limit, category):
        params={"limit": str(limit)}
        if category: params["category"]=category
        r=self.c.get("/assets", params=params)
        r.raise_for_status()
        return r.json()

def format_assets(data):
    items=data.get("assets", [])
    lines=["Assets:", f"Count: {len(items)}", ""]
    for i,a in enumerate(items[:50],1):
        lines.append(f"{i}. {a.get('symbol','?')} - {a.get('name','')[:60]}")
    if len(items)>50: lines.append(f"... {len(items)-50} more")
    return "\n".join(lines)

@click.command()
@click.option("--limit", default=10, type=int)
@click.option("--category")
@click.option("--json", "json_mode", is_flag=True)
def main(limit, category, json_mode):
    try:
        if limit<1 or limit>1000: raise ValueError("limit out of range")
        with Client() as client:
            data=client.list_assets(limit, category)
        if json_mode:
            click.echo(json.dumps(data, indent=2)); sys.exit(0)
        click.echo(format_assets(data)); sys.exit(0)
    except httpx.HTTPStatusError as e:
        msg=f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        msg=str(e)
    if json_mode:
        click.echo(json.dumps({"error": msg}, indent=2))
    else:
        click.echo(f"❌ Error: {msg}", err=True)
    sys.exit(3)

if __name__=="__main__":
    main()
```

---

## 22. FAQ (Generalized)

| Question | Answer |
|----------|--------|
| Do I have to migrate every tool? | No—migrate high-impact or frequently invoked tools first. |
| Can I keep both MCP and scripts? | Yes, hybrid approach is common during transition. |
| How do agents “discover” scripts? | Provide prime prompt & file naming clarity; optionally a lightweight index script listing available capabilities. |
| Should scripts ever call MCP tools? | Avoid; defeats purpose of reducing protocol overhead. |
| How to handle authentication securely? | Use environment variables and optional `--api-key`; never hardcode secrets. |
| What if output schemas change downstream? | Version script & communicate via commit/tag; keep old script until consumers switch. |

---

## 23. Migration Timeline Template (Example)

| Week | Milestone |
|------|-----------|
| 1 | Inventory & design decisions |
| 2 | Implement simple fetch + list scripts |
| 3 | Implement composite/search & caching |
| 4 | Validation & parity testing |
| 5 | Agent priming + partial rollout |
| 6 | Deprecate non-critical MCP tools |
| 7 | Assess refactoring threshold |
| 8 | Optimize / introduce shared_lib if warranted |

---

## 24. Success Metrics

| Metric | Target |
|--------|--------|
| Functional parity | ≥ 99% key fields match |
| Avg script LOC | ≤ 250 |
| Token reduction per invocation | ≥ 40% vs MCP server file |
| Latency reduction (non-cache ops) | ≥ 10–30% |
| Mean time to patch a bug | Decreases (simpler scope) |
| Number of scripts with duplicate bugs after 2 months | 0–1 (else trigger refactor) |

---

## 25. Final Recommendations

1. Start with highest-frequency & highest-context-cost tools.
2. Treat duplication as a temporary optimization for progressive disclosure—not a permanent liability.
3. Instrument usage (which scripts an agent invokes) to know where to invest future consolidation effort.
4. Document decisions, not just code—future maintainers need rationale to avoid undoing intentional trade-offs.
5. Revisit every 60–90 days to reassess abstraction boundaries.

---

## 26. Quick Start Summary (Condensed)

1. List MCP tools + parameters.
2. Create per-tool script file.
3. Implement HTTP call + `--json`.
4. Add human formatting (short, structured).
5. Test parity.
6. Prime agent with usage prompt.
7. Measure context savings.
8. Iterate for remaining tools.

---

Happy Migrating. Increase control. Decrease context. Maintain clarity.

(End of generalized guidelines)
