--- 
description: Lean template to load external documentation into local markdown for agent context
allowed-tools: Task, Fetch, Write, Edit, Bash(ls*)
---

# Load External Docs (Lean Template)

Goal: Fetch docs from URLs -> save as clean markdown -> report status.

## Vars
DOCS_INDEX_README: ai_docs/README.md
OUTPUT_DIR: ai_docs/
FRESH_HOURS: 24
SCRAPER_AGENT: docs-scraper
PARALLEL_LIMIT: 5
MIN_LENGTH: 200

## Workflow
1. Read DOCS_INDEX_README, collect unique URLs (ignore blanks/comments).
2. For each existing *.md in OUTPUT_DIR:
   - If modified < FRESH_HOURS hours ago → mark SKIPPED.
   - Else delete → mark DELETED.
3. Build task list for URLs without fresh file (limit PARALLEL_LIMIT concurrently).
4. For each URL:
   - Use primary scrape tool (markdown). Fallback: generic fetch + convert.
   - Clean: remove nav/chrome only; preserve headings/code/tables.
   - Validate length ≥ MIN_LENGTH.
   - Derive filename: kebab-case from path/title + .md.
   - Write file EXACTLY as scraped (no editorial changes).
5. After completion: generate report (see format).

## Report Format
```
Docs Load Report:
- <✅ | ❌ | ⏭ | 🗑>: <url> - <file-or-(none)>
Summary:
  Total: <N_total>
  Skipped (fresh): <N_skipped>
  Deleted (stale): <N_deleted>
  Attempted: <N_attempted>
  Successes: <N_success>
  Failures: <N_fail>
```

## Failure Reasons (choose one)
fetch-error | empty-content | below-min-length | parse-failure | write-error | rate-limited | unexpected-exception

## Filename Rules
- Lowercase
- Replace non-alphanum with '-'
- Collapse multiple '-'
- Ensure .md suffix

## Checklist Per URL
[ ] Fetched OK
[ ] Cleaned minimally
[ ] Length OK
[ ] Filename OK
[ ] Saved
[ ] Logged result

## Notes
- No summarizing. No rewriting.
- Do not re-fetch fresh files.
- Keep process idempotent.

(End Lean Template)