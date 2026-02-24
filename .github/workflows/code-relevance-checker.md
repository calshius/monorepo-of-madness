---
on:
  schedule: weekly
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  pull-requests: read
safe-outputs:
  create-issue:
    title-prefix: "[code-relevance] "
    labels: [maintenance, code-health]
    close-older-issues: true
---

## Code Relevance & Freshness Check

Analyse the repository and assess how current and relevant the codebase is. Create a GitHub issue with findings.

## What to analyse

### Dependencies
- Check `backend/pyproject.toml` for outdated or deprecated Python packages
- Check `frontend/package.json` for outdated or deprecated npm packages
- Flag any dependencies with known security advisories

### Code Patterns
- Identify deprecated API usage or patterns in both backend and frontend
- Flag any TODO/FIXME/HACK comments that may indicate unfinished work
- Check for dead code or unused imports

### Test Coverage
- Assess whether tests adequately cover the existing endpoints and components
- Identify any untested code paths

### Documentation Drift
- Check if `AGENTS.md` files accurately reflect the current project structure
- Verify README accuracy against the actual codebase

## Output Format

- Use a traffic light system: 🟢 Good, 🟡 Attention needed, 🔴 Action required
- Group findings by category (Dependencies, Code, Tests, Docs)
- Provide specific recommendations for each finding
