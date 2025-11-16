---
description: Load documentation from their respective websites into local markdown files our agents can use as context.
allowed-tools: Task, WebFetch, Write, Edit, Bash(ls*), mcp__firecrawl-mcp__firecrawl_scrape
---

# Load AI Docs

Load documentation from their respective websites into local markdown files our agents can use as context.

## Variables

DELETE_OLD_AI_DOCS_AFTER_HOURS: 24

This command is a simplified, opinionated instance of the more general `migration/templates/template.agent/template_commands/template_load_ai_docs.md` pattern. It fixes the following assumptions for you:

- DOCS_ROOT_DIR: `ai_docs/`
- DOCS_INDEX_README_PATH: `ai_docs/README.md`
- MARKDOWN_OUTPUT_DIR: `ai_docs/`
- SCRAPER_AGENT_NAME: `docs-scraper`
- SCRAPE_PARALLELISM_LIMIT: implementation-defined by the Task tool; treat tasks as parallel where possible.

In your own project, you should create an `ai_docs/README.md` using `migration/templates/template_ai_docs/template_README.md` as a starting point. This repository does not include `ai_docs/` by default; it is intended to live in the project that consumes these patterns.

## Workflow

1. Read the ai_docs/README.md file
2. See if any ai_docs/<some-filename>.md file already exists
   1. If it does, see if it was created within the last `DELETE_OLD_AI_DOCS_AFTER_HOURS` hours
   2. If it was, skip it - take a note that it was skipped
   3. If it was not, delete it - take a note that it was deleted
3. For each url in ai_docs/README.md that was not skipped, Use the Task tool in parallel and use follow the `scrape_loop_prompt` as the exact prompt for each Task 
   <scrape_loop_prompt>
   Use @docs-scraper agent - pass it the url as the prompt
   </scrape_loop_prompt>
4. After all Tasks are complete, respond in the `Report Format`

## Report Format

```
AI Docs Report:
- <✅ Success or ❌ Failure>: <url> - <markdown file path>
- ...
```
