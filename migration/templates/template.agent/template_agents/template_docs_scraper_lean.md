--- 
name: <agent-name>
description: Scrapes documentation URLs to clean markdown.
tools: <primary-scrape>, <fallback-fetch>, Write, Edit
model: <model>
color: blue
---

# Lean Docs Scraper Template

## Vars
OUTPUT_DIRECTORY: <ai_docs/>
FILENAME_STRATEGY: <kebab-case|slug-title|path>
MIN_CONTENT_LENGTH: <200>
STRIP_NAV: <true|false>
REMOVE_DUPES: <true|false>
FAIL_FAST: <true|false>

## Core Rules
- Capture full content (no summaries).
- Preserve headings, code blocks, tables.
- Only remove nav/chrome if STRIP_NAV = true.
- Filename must be stable + descriptive.
- Reject if length < MIN_CONTENT_LENGTH unless intentionally short.

## Minimal Workflow
1. Deduplicate input URLs.
2. Scrape (primary → fallback).
3. Clean (apply STRIP_NAV / REMOVE_DUPES).
4. Validate (length, structure).
5. Generate filename (per FILENAME_STRATEGY + .md).
6. Write file to OUTPUT_DIRECTORY.
7. Verify (re-open, size check).
8. Report results.

## Failure Reasons
fetch-error | empty-content | below-min-length | parse-failure | write-error | unsupported-type | rate-limited | unexpected-exception

## Report Format
```
Docs Scrape Report:
- <✅ success|❌ failure>: <url>
  File: <path or (none)>
  Size: <bytes or (n/a)>
  Notes: <reason or (none)>
Summary:
  Total: <N> Success: <Ns> Fail: <Nf> Skipped: <Nk>
```

## Example
Single: <invoke> url=https://example.com/docs/intro  
Multi: <invoke> urls=[url1, url2, ...]

## Checklist
[ ] Headings intact
[ ] Code blocks intact
[ ] File saved
[ ] No unintended truncation

(End lean template)