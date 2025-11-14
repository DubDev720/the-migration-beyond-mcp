# Migration Plan
Decide which MCP tools to migrate to which formats (CLI, File‑System Scripts, Claude Skills), and how to document the resulting surfaces so users can quickly review, modify, and use the tools while ops can adjust agent permissions.

This plan is additive. It complements:
- migration/guides/guide_cli_migration.md
- migration/guides/guide_file_system_scripts_migration.md
- migration/guides/guide_claude_skills_migration.md
- tests/test_validation_plan.md

Reference: beyond-mcp by IndyDevDan offers a complete example of MCP + CLI + Scripts + Skills built with consistent semantics across surfaces.


## 1) Purpose and Scope
- Provide a repeatable decision framework to map each MCP tool to one or more target formats:
  - CLI
  - File‑System Scripts
  - Claude Skills
- Provide a standardized documentation strategy so users and operators can:
  - discover capabilities quickly,
  - understand parameters and outputs,
  - adjust agent permissions confidently.
- Support two migration modes:
  - Single‑format migration: all or selected functionality to one format
  - Split / multi‑format migration: per‑tool mapping to different formats based on needs


## 2) Inputs and Prerequisites
- Inventory of MCP tools:
  - Tool name, intent (1–2 lines), parameters (name, type, required, default), output fields (schema summary), error semantics, pagination/cursor, caching, auth/rate limits, data volume, latency sensitivity.
- Target audiences:
  - End users (human operators), automation (CI/scripts), and agents (Claude/others).
- Constraints:
  - Security/compliance policies, environment/network constraints, team ownership.


## 3) Decision Framework (Tool → Format Mapping)
Use these axes to decide where each tool fits best. A tool can map to multiple formats.

Business/UX axes
- Audience: human operators (prefer CLI), agent usage (prefer Scripts/Skills), both (prefer CLI + Scripts; optionally Skills).
- Frequency of use: frequent ad‑hoc human use (CLI), frequent autonomous agent use (Scripts/Skills).
- Sharing & onboarding: git‑shareable scripts/skills help teams ramp quickly.

Technical axes
- Data volume: high (CLI with `--json`, pagination; caution in Skills), low (Scripts/Skills fine).
- Latency: tight latency (CLI/Script direct), tolerant latency (any).
- Streaming/long‑running: favor MCP or CLI; Skills/Script typically short, atomic.
- Stability/contract: canonical JSON contract should live in CLI (highly recommended). Scripts/Skills mirror it.

Operational axes
- Deployment: CLI is easy to distribute; Scripts are copy-and-run; Skills are zero-server but editor-specific.
- Permissions: scripts/skills per-file allowlists; CLI per-subcommand allowlists.
- Observability: CLI lends itself to piping/logging in automation; Skills rely on editor agent logs.

Rules of thumb
- Prefer building the CLI first as the canonical JSON contract. Then:
  - Extract File‑System Scripts for minimal context and progressive disclosure.
  - Wrap scripts with Claude Skills for autonomous discovery in Claude Code.
- Tools that primarily serve human/automation workflows → CLI (and optionally Scripts).
- Tools the agent should autonomously discover and use → Skills (over Scripts).
- Tools with heavy data or complex paging → CLI first; Scripts/Skills must preserve pagination flags and defaults.


## 4) Mapping Outcomes
A) Single‑format migration (one target)
- Example goals:
  - “All read‑only tools → CLI”
  - “Selected top-5 tools → Scripts only”
- Use the per‑tool mapping worksheet (Section 6) and implement the chosen format consistently.

B) Split / multi‑format migration (mixed targets)
- Example goals:
  - “All tools → CLI; subset → Scripts; smaller subset → Skills”
  - “Human‑facing monitoring → CLI; agent analyst flows → Skills; some utilities → Scripts”
- Ensure identical parameter semantics and JSON outputs across chosen surfaces.
- Keep CLI as the canonical API contract; Scripts/Skills mirror it.


## 5) Deliverables and Directory Layout (Docs + Artifacts)
- migration/
  - guides/
    - guide_cli_migration.md (authoritative, standalone)
    - guide_file_system_scripts_migration.md (authoritative, standalone)
    - guide_claude_skills_migration.md (authoritative, standalone)
  - migration_plan.md (this file)
  - templates/
    - file_skeletons/
      - cli_subcommand_skeleton.py
      - script_skeleton.py
    - template_per_tool_mapping.md
- tests/
  - test_validation_plan.md (end‑to‑end parity & validation)
- scripts/
  - generate_cli_script.py
- Per‑format project areas:
  - (add your CLI/scripts/skills code under your chosen structure)
