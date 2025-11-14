# Lean Prime File System Scripts (Template)

Goal: Rapid priming to use capability scripts for <DOMAIN_NAME> with minimal context.

## Vars
DOMAIN_NAME: <e.g. Markets>
SCRIPTS_DIR: <path/to/scripts>
INVOCATION_PREFIX: <uv run|python>
DEFAULT_MODE: <--json|human>
MAX_LIMIT: <10>
HIGH_VALUE_FILTER: <status=active|volume>
CACHE_FLAG: <--rebuild-cache>
READ_POLICY: <help-only|restricted|full>

## Rules
- Load only needed script.
- Prefer DEFAULT_MODE unless summarizing.
- Start with --limit MAX_LIMIT.
- Use help (`<script>.py --help`) before reading source if READ_POLICY != full.
- Use HIGH_VALUE_FILTER to focus results.
- For caching scripts: first run may be slow—do not abort; note progress.

## Script Categories (Infer)
list_*      → enumeration
<entity>.py → detail
search.py   → keyword lookup (may build cache)
*candlesticks.py → timeseries
status.py   → service/state check
trades.py / events.py → recent activity or grouped data

## Invocation Patterns
List:    INVOCATION_PREFIX list_<entity>.py --limit MAX_LIMIT --json
Detail:  INVOCATION_PREFIX <entity>.py <id> --json
Search:  INVOCATION_PREFIX search.py "<term>" --limit MAX_LIMIT --json
Series:  INVOCATION_PREFIX series_list.py --limit MAX_LIMIT --json
Time:    INVOCATION_PREFIX <entity>_candlesticks.py <series> <ticker> --start-ts <start> --end-ts <end> --interval 60 --json

## Error Shape
Human: ❌ Error: <message>
JSON:  {"error": "<message>"}
Non-zero exit → adjust params / retry.

## Decision Flow
1. Identify data need.
2. Map to single script.
3. Use --help if flags unclear.
4. Run with minimal limit.
5. Expand / chain using --json.

## Report Skeleton
```
<DOMAIN_NAME> Scripts Prime Report
Dir: SCRIPTS_DIR
Policy: READ_POLICY
Capabilities:
- script.py: purpose (use when ...)
Strategy:
- default mode: DEFAULT_MODE
- limit: MAX_LIMIT
Progressive Disclosure: Will not read sources unless required.
```

## Confirmation
I will only list and use help output; no source reading beyond policy.

(End lean template)