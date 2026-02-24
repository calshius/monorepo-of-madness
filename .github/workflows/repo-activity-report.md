---
on:
  schedule: daily
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  pull-requests: read
safe-outputs:
  create-issue:
    title-prefix: "[activity-report] "
    labels: [report, activity]
    close-older-issues: true
---

## Daily Repository Activity Report

Create a concise daily activity report for the team as a GitHub issue.

## What to include

- Recent commits, merges, and branch activity
- New, closed, and in-progress issues
- Pull request activity (opened, reviewed, merged)
- Test results and CI status from recent runs
- Any notable code changes in `backend/` or `frontend/`

## Style

- Keep it brief and scannable
- Use bullet points and tables where appropriate
- Highlight blockers or failed CI runs
- End with 2-3 actionable next steps
