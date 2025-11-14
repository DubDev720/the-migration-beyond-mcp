# Agent Prime Prompt: File System Script Mode

You have access to a suite of standalone Python scripts that expose system / API capabilities with minimal context footprint. Each script is single‑purpose, self‑contained, and supports `--json` for structured output. Load ONLY the scripts needed for the current task.

## Core Principles
1. Progressive disclosure: Do not read or open unrelated scripts.
2. Human vs JSON:
   - Default (no flag): Human‑readable summary (token efficient).
   - `--json`: Structured data for chaining, extraction, transformation.
3. Failure handling: Check exit code or presence of `{"error": ...}` in JSON mode.
4. Parity: Script flags typically match prior MCP tool parameter names.

## Capability Patterns (Generic Examples)
(Exact filenames may differ—adapt to the repository you see.)

| Purpose | Script | Typical Invocation |
|---------|--------|--------------------|
| System / service status | `status.py` | `uv run status.py --json` |
| List entities/resources | `resources_list.py` | `uv run resources_list.py --limit 25` |
| Get entity details | `resource.py` | `uv run resource.py <id>` |
| Filtered query / search | `search.py` | `uv run search.py "keyword" --limit 15` |
| Aggregated metrics / analytics | `metrics.py` | `uv run metrics.py --range 24h --json` |
| Orderbook / depth style data | `orderbook.py` | `uv run orderbook.py <symbol> --depth 20 --json` |
| Trades / events stream snapshot | `trades.py` | `uv run trades.py --limit 50` |
| Series / taxonomy enumeration | `series_list.py` | `uv run series_list.py --category finance --json` |
| Series / template details | `series.py` | `uv run series.py <series_code>` |
| Candlestick / timeseries (market) | `market_candlesticks.py` | `uv run market_candlesticks.py <series> <ticker> --start-ts ... --end-ts ... --interval 60 --json` |
| Candlestick / timeseries (aggregate) | `event_candlesticks.py` | `uv run event_candlesticks.py <series> <event> --start-ts ... --end-ts ... --interval 1440` |

## Decision Flow (Ask Yourself Before Invoking)
1. What specific data do I need? → Choose the narrowest script.
2. Do I need machine‑consumable output? → Add `--json`.
3. Am I chaining multiple scripts? → Prefer JSON for each step.
4. Is a cache likely involved (search, large enumeration)? → Check flags like `--rebuild-cache` or `--stats`.
5. Will this produce large output? → Use limiting flags (`--limit`, `--depth`) first.

## Safe Invocation Guidelines
- Always start with a small `--limit` (e.g., 5 or 10) to confirm shape.
- Use positional arguments only where required (avoid guessing optional flags).
- If a script supports `--help`, inspect it instead of opening source unless necessary.
- In JSON mode, validate presence of expected keys before continuing.

## Error Pattern Recognition
- Human mode: `❌ Error: <message>`
- JSON mode: `{"error": "<message>"}` → Stop further chained operations; reassess parameters.

## Output Handling Tips
- For summarization tasks: Use human mode, then optionally re-run with `--json` for extraction.
- For transformation / analytics: Always start with `--json`.
- For multi-step reasoning: Capture intermediate JSON outputs verbatim before summarizing.

## Example Agent Interactions
Prompt: "Show me 5 resources about renewable energy."
Action:
```
uv run search.py "renewable energy" --limit 5 --json
```
Then summarize results—do not load unrelated scripts.

Prompt: "Get detailed info on the third result."
Action:
1. From previous JSON, extract the identifier (`id`, `ticker`, etc.).
2. Invoke:
```
uv run resource.py <ID> --json
```

Prompt: "Provide hourly metrics for that resource yesterday."
Action:
```
uv run market_candlesticks.py <series> <ticker> --start-ts <unix_start> --end-ts <unix_end> --interval 60 --json
```
Convert returned OHLC data into requested summary.

## Minimal Index Script Pattern (Optional)
If you need to enumerate available capabilities without scanning each file, create a simple `scripts_index.py`:

```
#!/usr/bin/env python3
# version: 2024-11-13
"""
List available scripts and short usage hints.
Usage:
  uv run scripts_index.py
  uv run scripts_index.py --json
"""
import json, sys

SCRIPTS = [
  {"name": "status.py", "purpose": "System/service status", "usage": "uv run status.py --json"},
  {"name": "search.py", "purpose": "Keyword search", "usage": "uv run search.py <keyword> --limit 10"},
  {"name": "resource.py", "purpose": "Get one resource detail", "usage": "uv run resource.py <id>"},
  {"name": "resources_list.py", "purpose": "List resources", "usage": "uv run resources_list.py --limit 20"},
]

def main(json_mode: bool):
    if json_mode:
        print(json.dumps(SCRIPTS, indent=2)); sys.exit(0)
    print("Available Scripts:\n")
    for s in SCRIPTS:
        print(f"- {s['name']}: {s['purpose']}\n  Example: {s['usage']}\n")
    sys.exit(0)

if __name__ == "__main__":
    jm = "--json" in sys.argv
    main(jm)
```

## Agent Behavior Expectations
- Avoid speculative file inspection: rely on documented usage.
- Minimize token usage: do not open all scripts preemptively.
- Prefer smallest data footprint first, expand only if needed.
- Detect repeated failures—adjust parameters instead of brute-forcing large limits.

## Summary Cheatsheet
- Need list? → `<entity>_list.py --limit N`
- Need single detail? → `<entity>.py <identifier>`
- Need structured chaining? → Add `--json`
- Need search? → `search.py <keyword>`
- Need time series? → `*_candlesticks.py` with timestamps
- Unsure? → `scripts_index.py` (if present) or run `--help`

Focus: Precision, minimal context, structured outputs when chaining operations.

(End of prime prompt)