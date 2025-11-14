# Template Prime

Understand the <PROJECT_NAME> project and its file structure.

## Variables (Customize These)

PROJECT_NAME: <YourProjectName>
ROOT_README_PATH: <path/to/README.md>
APP_READMES_GLOB: <apps/*/README.md>
ADDITIONAL_DOCS_GLOBS: <docs/**/*.md | optional>
EXCLUDE_PATH_PATTERNS: <tests/**, vendor/** | optional>
INCLUDE_EXTRA_NOTES: <true|false>
OUTPUT_STYLE: <concise|detailed>

## Workflow

1. RUN `git ls-files` to enumerate the tracked file structure.
2. READ <ROOT_README_PATH>
3. READ all readme files matching <APP_READMES_GLOB>
4. IF <ADDITIONAL_DOCS_GLOBS> provided, READ those (respect <EXCLUDE_PATH_PATTERNS>)
5. IF <INCLUDE_EXTRA_NOTES> == true, IDENTIFY any architecture or design documents (e.g. ARCHITECTURE.md, DESIGN.md) and READ them.
6. SUMMARIZE directory purposes (top-level first, then apps/services/modules).
7. IDENTIFY:
   - Primary entry points (e.g. main server, CLI, scripts)
   - Configuration files (pyproject.toml, package.json, Dockerfile, etc.)
   - Tooling / automation (CI configs, scripts/)
   - Domain-specific modules (business logic vs infrastructure)
8. LIST any obvious extension points or plugin interfaces.
9. NOTE any cache, temp, or generated artifact directories you will avoid reading deeply (progressive disclosure).
10. PREPARE the report according to <OUTPUT_STYLE> (concise = bullet summary; detailed = sectioned narrative).

## Report

Produce a report of your understanding of the project:
- High-level purpose
- Structural overview (key top-level folders and roles)
- Core components and their responsibilities
- Notable conventions (naming, layering, patterns)
- Potential extension points
- Areas requiring deeper inspection later (flag but do not dive now)

Confirm explicitly that you followed progressive disclosure and did not read files outside the specified patterns.

Format:
```
<PROJECT_NAME> Prime Report
Purpose:
  <one or two sentences>

Structure:
  - <folder>: <purpose>
  - ...

Core Components:
  - <component>: <role>
  - ...

Conventions:
  - ...

Extension Points / Future Exploration:
  - ...

Deferred Deep Dives (Flagged):
  - ...

Progressive Disclosure Confirmation:
  Only the targeted README and allowed doc files were read. No unrelated source files were opened.
```
