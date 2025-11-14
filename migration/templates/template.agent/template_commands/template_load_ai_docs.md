---
description: <DESCRIPTION e.g. "Load external documentation into local markdown for agent context">
allowed-tools: <ALLOWED_TOOLS_LIST e.g. Task, WebFetch, Write, Edit, Bash(ls*), ScrapeTool>
---

# Template: Load External Docs

Load documentation from specified websites into local markdown files our agents can use as context.

## Variables (Set Before Running)

DOCS_ROOT_DIR: <root docs directory, e.g. ai_docs/>
DOCS_INDEX_README_PATH: <path to index file listing target URLs, e.g. ai_docs/README.md>
MARKDOWN_OUTPUT_DIR: <directory for generated markdown files, e.g. ai_docs/>
DELETE_OLD_DOCS_AFTER_HOURS: <number of hours to treat existing docs as fresh, e.g. 24>
SCRAPER_AGENT_NAME: <agent name used for scraping tasks, e.g. agent-docs-scraper>
SCRAPER_TASK_PROMPT_TEMPLATE: <prompt template passed to each scraping Task>
SCRAPE_PARALLELISM_LIMIT: <integer limit for concurrent tasks, e.g. 5>
URL_LIST_SOURCE_SECTION: <optional section header in README to scope URLs, or leave blank>
REPORT_INCLUDE_TIMESTAMP: <true|false>
REPORT_INCLUDE_FILE_SIZE: <true|false>
MARKDOWN_FILE_NAMING_CONVENTION: <e.g. kebab-case-domain-section.md>

## Preconditions

- DOCS_INDEX_README_PATH exists and contains one URL per line OR a structured list.
- Output directory writable.
- Allowed tools available in environment.

## Workflow

1. READ DOCS_INDEX_README_PATH
2. PARSE URL list:
   - If URL_LIST_SOURCE_SECTION is set, ONLY parse URLs under that section.
   - Normalize: trim whitespace, remove duplicates, ignore empty/comment lines.
3. INVENTORY existing markdown files in MARKDOWN_OUTPUT_DIR matching MARKDOWN_FILE_NAMING_CONVENTION.
4. For each existing file:
   1. CHECK its modification time.
   2. IF age (hours) < DELETE_OLD_DOCS_AFTER_HOURS:
      - MARK as SKIPPED (fresh).
   3. ELSE:
      - DELETE file.
      - MARK as DELETED (stale).
5. BUILD scrape task plan:
   - EXCLUDE URLs whose fresh file already exists.
   - LIMIT concurrency to SCRAPE_PARALLELISM_LIMIT.
6. For each remaining URL:
   - CREATE a Task using SCRAPER_TASK_PROMPT_TEMPLATE with variable injection:
     <SCRAPER_TASK_PROMPT_TEMPLATE Example>
     Use @<SCRAPER_AGENT_NAME> agent - pass the URL as the prompt.
     Return cleaned markdown, remove navigation clutter, ensure headings preserved.
     </SCRAPER_TASK_PROMPT_TEMPLATE>
   - STORE task reference.
7. AWAIT all Tasks completion.
8. For each completed Task:
   - VALIDATE content length (> minimal threshold, e.g. 200 chars).
   - ASSIGN output filename derived from URL using MARKDOWN_FILE_NAMING_CONVENTION.
   - WRITE markdown file into MARKDOWN_OUTPUT_DIR.
   - RECORD success or failure status.
9. GENERATE report in specified format.
10. IF REPORT_INCLUDE_TIMESTAMP true, append generation timestamp.
11. IF REPORT_INCLUDE_FILE_SIZE true, append file size for each success.

## Edge Cases & Handling

- Duplicate URLs: process once.
- Non-200 HTTP responses: mark as failure.
- Empty scrape result: failure.
- Existing fresh file with different checksum: KEEP original (avoid churn).
- Rate limits: throttle or temporarily skip; record failure reason.
- Redirect chains: accept final URL; derive filename from final destination host/path.

## Naming Convention Guidance

Transform URL to filename:
1. Lowercase host + path segments.
2. Replace non-alphanumeric with '-'.
3. Collapse multiple '-' to single '-'.
4. Ensure suffix '.md'.
Example:
https://docs.example.com/Guide/Intro -> docs-example-com-guide-intro.md

## <scrape_loop_prompt>

Exact prompt passed to each parallel scraping task (template, replace placeholders):
```
Use @<SCRAPER_AGENT_NAME> agent - pass this URL as the prompt:
<URL>
Instructions:
- Return clean markdown only.
- Preserve heading levels (#, ##, ###).
- Remove sidebars / nav / cookie banners.
- Keep code blocks verbatim.
- Do not include raw HTML unless necessary.
```

## Report Format

```
Docs Load Report:
<If REPORT_INCLUDE_TIMESTAMP>true: Timestamp: <ISO8601></If>
Summary:
- Total URLs: <TOTAL_URLS>
- Skipped (fresh): <COUNT_SKIPPED>
- Deleted (stale): <COUNT_DELETED>
- Attempted (scrape): <COUNT_ATTEMPTED>
- Successes: <COUNT_SUCCESS>
- Failures: <COUNT_FAILURE>

Per-URL Results:
- <✅ Success|❌ Failure|⏭ Skipped|🗑 Deleted>: <url>
  File: <markdown file path or "(skipped)">
  <If success and REPORT_INCLUDE_FILE_SIZE>true: Size: <N bytes></If>
  <If failure>: Reason: <error summary></If>
```

## Post-Run Validation Checklist

- Confirm all expected new markdown files exist.
- Spot-check 1–2 files for formatting integrity.
- Verify skipped files were within freshness threshold.
- Ensure no unintended large binary artifacts got written.

## Extension Ideas (Optional)

- Add checksum manifest file (docs_manifest.json).
- Integrate diffing to detect substantive content changes (notify only when >5% delta).
- Compress older docs after N days.
- Schedule automatic re-run via task scheduler.

## Progressive Disclosure Confirmation

Only the index README and targeted markdown outputs were examined. No unrelated repository files were read.
