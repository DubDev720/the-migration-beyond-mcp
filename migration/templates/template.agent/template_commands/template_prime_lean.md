# Template Prime (Lean)

Understand the <PROJECT_NAME> structure quickly and minimally.

## Vars
PROJECT_NAME=<YourProjectName>
ROOT_README=<path/to/README.md>
APP_READMES_GLOB=<apps/*/README.md>
EXTRA_DOCS_GLOB=<docs/**/*.md | optional>
OUTPUT_STYLE=<concise|detailed>

## Minimal Workflow
1. List tracked files: run git ls-files.
2. Read ROOT_README.
3. Read all APP_READMES_GLOB matches.
4. (Optional) Read EXTRA_DOCS_GLOB if explicitly provided.
5. Identify:
   - Purpose (1–2 sentences)
   - Top-level directories & roles
   - Main entry points (server, CLI, scripts)
   - Config files (package/pyproject, env, docker)
   - Extension points / plugin hooks (if any)
6. Do NOT open source code files unless absolutely necessary for high-level understanding.
7. Produce report in chosen OUTPUT_STYLE.

## Report Format
```
<PROJECT_NAME> Prime Report
Purpose:
  <short purpose>

Structure:
  - <dir>: <role>
  - ...

Entry Points:
  - <file or dir>: <function>

Configs:
  - <config-file>: <notes>

Extension Points:
  - <item>: <possible use>

Deferred (Needs deeper dive later):
  - <area>

Progressive Disclosure Confirmation:
  Only README and allowed high-level docs were read; source bodies skipped.
```

## Rules (Lean)
- Keep total output short.
- No deep dives.
- No code analysis.
- Confirm progressive disclosure in report.