# AI Docs Template

Central index for documentation URLs to ingest and store as local Markdown for agent use.
Inspired by the documentation style of the Model Context Protocol Python SDK.

Reference:
- MCP Python SDK README: https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md

## Purpose

- Curate a list of project-relevant online documentation URLs in one place.
- Automate fetching and converting those docs into local Markdown for fast, offline agent context.
- Keep a repeatable, low-friction workflow for refreshing and validating documentation.

## Quick Start

1. Add your documentation URLs to the Sources section below.
2. Use your docs-loading command/prompt (e.g., “Load External Docs”) that:
   - Reads this file to gather URLs
   - Scrapes each URL to Markdown
   - Saves outputs into your configured docs directory (e.g., `ai_docs/`)
3. Verify outputs and iterate.

Example flow (pseudo):
- Confirm variables in your load command/prompt (e.g., output directory and staleness threshold).
- Kick off the “load docs” workflow.
- Inspect the report and spot-check a few generated files.

## Variables (suggested)

- DOCS_INDEX_README: Path to this file (e.g., `ai_docs/README.md`)
- OUTPUT_DIR: Directory for generated Markdown files (e.g., `ai_docs/`)
- FRESH_HOURS: Age threshold for re-scraping (e.g., `24`)
- SCRAPER_AGENT: The scraping agent name or profile (e.g., `docs-scraper`)
- PARALLEL_LIMIT: Concurrency cap for scraping tasks (e.g., `5`)
- MIN_LENGTH: Minimum acceptable content length (e.g., `200` chars)

## Guidelines

- Keep URLs precise and stable (link to canonical docs pages where possible).
- Avoid adding generic home pages unless necessary—prefer deep links (Quick Start, API Reference).
- If a site is multi-part, list distinct URLs for key sections.
- When a URL’s structure changes, update it here and re-run your loader.

## Sources

Place one URL per line in the list below. Duplicates will be deduplicated by your loader (if configured). These URLs will be scraped and saved as Markdown.

<!-- Replace these lines with your project's online resource documentation, quick-start guides, and references -->
<!-- https://docs.your-project-resource.urls -->
<!-- https://docs.your-starter-documentation.com/quick-start -->

- https://example.com/docs/overview
- https://example.com/docs/getting-started
- https://example.com/docs/api-reference
- https://example.com/docs/faq

(Add, remove, or reorder URLs as needed.)

## Output Expectations

- Each URL becomes a single `.md` file in `OUTPUT_DIR`.
- Filenames should be deterministic (e.g., kebab-case from title or URL path).
- Content should be full-fidelity Markdown:
  - Preserve headings (#, ##, ###)
  - Preserve code blocks and tables
  - Remove only navigation chrome and duplicated menus

## Refresh & Maintenance

- Re-run the loader periodically or on-demand.
- Use freshness thresholds to avoid unnecessary re-scrapes.
- Consider a lightweight diff check or checksum to detect meaningful changes.
- Track failures in the report and fix invalid/redirecting URLs promptly.

## Example Agent Usage

- “Load AI Docs” command reads this README, scrapes listed URLs, saves `.md` files to `ai_docs/`, and produces a report.
- Your coding/analysis agent can then open the relevant `.md` files (not the live web) for consistent, reproducible context.

## Contributing

- Keep this list tidy and relevant.
- Prefer structured, authoritative documentation sources.
- When adding new product/feature docs, annotate them with a short rationale in the commit message.
