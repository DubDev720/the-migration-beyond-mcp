# Template Prime File System Scripts

Understand how to use the file system scripts for <DOMAIN_NAME> data.

## Variables (Customize Before Use)

PROJECT_SCRIPTS_PATH_ROOT_DIR: `<apps/3_file_system_scripts | <your-root>>`
PROJECT_SCRIPTS_PATH_SCRIPTS_DIR: `<apps/3_file_system_scripts/scripts | <your-scripts-dir>>`
DOMAIN_NAME: `<Kalshi | Finance | InternalOps | Etc>`
PRIMARY_DATA_FOCUS: `<markets | events | resources | assets>`
SECONDARY_DATA_FOCUS: `<series | metadata | analytics>`
DEFAULT_OUTPUT_MODE: `<--json | human>`
HIGH_VALUE_CRITERIA: `<volume | recency | priority | status:active>`
SCRIPT_INVOCATION_PREFIX: `<uv run | python | ./>`
PARSING_TOOL_HINT: `<jq | yq | custom-parser>`
SCRIPT_READ_POLICY: `<help-only | restricted | full>`
MAX_INITIAL_LIMIT: `<10 | 25>`
CACHE_REBUILD_FLAG: `<--rebuild-cache | --refresh | (none)>`
ALLOWED_EXTENSIONS: `<.py>`
PROGRESSIVE_DISCLOSURE_CONFIRMATION_TEXT: `I will not read script source unless help text is insufficient.`

## Instructions

- Default to using `<DEFAULT_OUTPUT_MODE>` for all script invocations unless user asks for human-readable summaries.
- Prioritize items matching `<HIGH_VALUE_CRITERIA>` when listing or filtering.
- Use `<PARSING_TOOL_HINT>` to parse JSON output when chaining operations.
- IMPORTANT: Follow `<SCRIPT_READ_POLICY>`:
  - If `help-only`: DO NOT open full source; only run `<script>.py --help` when clarification needed.
  - If `restricted`: Open source only after explicit user request.
  - If `full`: You may read, but prefer `--help` first to reduce context usage.
- Never load unrelated scripts preemptively—progressive disclosure is the goal.
- Prefer smaller `--limit` (e.g. `<MAX_INITIAL_LIMIT>`) on first invocation to validate output shape.
- If a cache-based script (e.g. search) is slow initially, note build time and avoid premature cancellation.
- Use consistent invocation prefix: `<SCRIPT_INVOCATION_PREFIX> <script>.py [options]`.

## Workflow

1. LIST directory structure of `<PROJECT_SCRIPTS_PATH_SCRIPTS_DIR>` (names only).
2. READ the README (if present) at `<PROJECT_SCRIPTS_PATH_ROOT_DIR>/README.md` for global context.
   - DO NOT read individual script files unless policy allows or `--help` output is insufficient.
3. BUILD internal capability map:
   - Identify scripts likely related to `<PRIMARY_DATA_FOCUS>` and `<SECONDARY_DATA_FOCUS>`.
   - Categorize by verbs: list / get / search / analytics / status / metrics / timeseries / cache.
4. For user requests:
   - MAP request intent to one script.
   - RUN `<SCRIPT_INVOCATION_PREFIX> <script>.py --help` ONLY if arguments/flags unknown.
   - INVOKE with `<DEFAULT_OUTPUT_MODE>` and minimal required flags.
5. If large result sets:
   - Start with `--limit <MAX_INITIAL_LIMIT>`.
   - Expand only after confirming relevance.
6. For search/cached scripts:
   - If results slow: Explain cache build (use `<CACHE_REBUILD_FLAG>` if rebuild requested).
7. For chaining:
   - Always choose `--json` to enable structured follow-up parsing.
8. LOG each script used, purpose, and whether help looked at (internal tracking).
9. PREPARE report (see Report section).

## Report

Report your understanding of the file system scripts for `<DOMAIN_NAME>` data and when you will use each script.

Format:
```
<DOMAIN_NAME> File System Scripts Prime Report

Scripts Directory: <PROJECT_SCRIPTS_PATH_SCRIPTS_DIR>
Policy: <SCRIPT_READ_POLICY>

Capability Map:
- <script_name.py>: <inferred purpose> (use when: <scenario>)
- ...

Invocation Strategy:
- Default output mode: <DEFAULT_OUTPUT_MODE>
- Initial limits: <MAX_INITIAL_LIMIT>
- High value filter: <HIGH_VALUE_CRITERIA>

Cache / Slow Operations:
- <script>: cache behavior / rebuild flag <CACHE_REBUILD_FLAG>

Progressive Disclosure:
<PROGRESSIVE_DISCLOSURE_CONFIRMATION_TEXT>

Planned Usage Examples:
1. Status check: <SCRIPT_INVOCATION_PREFIX> status.py <flags>
2. Listing high-value items: <SCRIPT_INVOCATION_PREFIX> list_<PRIMARY_DATA_FOCUS>.py --limit <MAX_INITIAL_LIMIT> --json
3. Detail retrieval: <SCRIPT_INVOCATION_PREFIX> <PRIMARY_DATA_FOCUS>.py <identifier> --json
4. Search: <SCRIPT_INVOCATION_PREFIX> search.py "<term>" --limit <MAX_INITIAL_LIMIT> --json

Next Steps:
- Await user queries; do not pre-load additional scripts.
```

Confirm in the report that you did not read the script source bodies beyond allowed policy.

## Example Invocation Patterns (Template)

```
# List primary entities
<SCRIPT_INVOCATION_PREFIX> list_<PRIMARY_DATA_FOCUS>.py --limit <MAX_INITIAL_LIMIT> --json

# Get single entity
<SCRIPT_INVOCATION_PREFIX> <PRIMARY_DATA_FOCUS>.py <identifier> --json

# Search (cached)
<SCRIPT_INVOCATION_PREFIX> search.py "<keyword>" --limit <MAX_INITIAL_LIMIT> --json

# Timeseries / analytics
<SCRIPT_INVOCATION_PREFIX> <PRIMARY_DATA_FOCUS>_candlesticks.py <series> <ticker> --start-ts <start> --end-ts <end> --interval 60 --json
```

## Error Handling Conventions (Insert Once Known)

| Scenario | Expectation | Reaction |
|----------|-------------|----------|
| Network error | JSON: {"error": "..."} | Retry (bounded) or report |
| Validation error | Helpful message in help output | Adjust flags |
| Empty results | Legitimate; confirm filters | Refine query |
| Cache build delay | Minutes-scale first run | Inform user & wait |

## Extension Placeholders

- AUTHENTICATION_FLAG: `<--api-key | --auth-token | (none)>`
- RATE_LIMIT_STRATEGY: `<sleep-and-retry | exponential-backoff | none>`
- PAGINATION_PARAM: `<--cursor | --page>`
- SECONDARY_FILTERS: `<--status | --category | --tag | --series>`

## Progressive Disclosure Confirmation Template

Use exactly:
```
I confirm I will only read directory listings and help text unless explicitly required. I will not open source code bodies without necessity.
```

(End template)