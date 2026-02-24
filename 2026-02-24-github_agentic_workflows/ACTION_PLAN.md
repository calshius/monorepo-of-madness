# Action Plan: GitHub Agentic Workflows Demo

**Goal:** Build a minimal FastAPI + SvelteKit repo that demonstrates GitHub Agentic Workflows (gh-aw) — specifically using agentic workflows to run tests and maintain `AGENTS.md` files. Simple enough for a Substack blog post.

**Monorepo note:** This project lives at `monorepo-of-madness/2026-02-24-github_agentic_workflows/`. The `.github/workflows/` files are authored inside this project folder and are designed to work when the project is pushed to its own standalone GitHub repo. They will not interfere with sibling projects in the monorepo.

---

## Phase 1 — Scaffold the Applications

### 1. FastAPI backend (`backend/`)
- Init with `uv` (`uv init`)
- Simple FastAPI app with 2-3 endpoints (`GET /health`, `GET /items`, `POST /items`)
- Add `pytest` tests covering all endpoints
- Keep it trivial — an in-memory list of items, no database

### 2. SvelteKit frontend (`frontend/`)
- Init with SvelteKit (`npx sv create`)
- A single page that fetches from the API and displays items, with a form to add one
- Add Vitest/Playwright tests (SvelteKit ships with these options)
- Minimal — just enough to have a testable UI

---

## Phase 2 — Standard CI (GitHub Actions)

### 3. Create `workflows/ci.yml`
- Standard GitHub Actions workflow triggered on `push` and `pull_request`
- Job 1: Run `pytest` for the backend (using `uv`)
- Job 2: Run `vitest`/`playwright` for the frontend
- This is the deterministic CI that the agentic workflow will observe
- Authored in `workflows/` within this project folder — to be moved to `.github/workflows/` when the project gets its own repo

---

## Phase 3 — Agentic Workflows

### 4. Create `workflows/repo-activity-report.md`
- An agentic workflow scheduled daily (also manually triggerable)
- The agent analyses recent repo activity and creates a GitHub issue with a summary
- Uses `safe-outputs: create-issue` with auto-close of older reports
- Shows the "Daily Status Report" pattern from the docs

### 5. Create `workflows/code-relevance-checker.md`
- An agentic workflow scheduled weekly (also manually triggerable)
- The agent analyses the codebase for outdated dependencies, deprecated patterns, test coverage gaps, and documentation drift
- Uses `safe-outputs: create-issue` with traffic-light findings
- Demonstrates the "Continuous Improvement" pattern

> All workflow files live in `workflows/` within this project folder. When the project is pushed to its own GitHub repo, rename/move this to `.github/workflows/`.

---

## Phase 4 — AGENTS.md Files

### 6. Create `backend/AGENTS.md`
- Describes the backend: tech stack (FastAPI, Python, uv), how to run tests (`uv run pytest`), project structure, coding conventions

### 7. Create `frontend/AGENTS.md`
- Describes the frontend: tech stack (SvelteKit, TypeScript), how to run tests (`npm test`), project structure, conventions

### 8. Create root `AGENTS.md`
- Top-level overview linking to both sub-project AGENTS.md files
- Repo-wide conventions and workflow descriptions

---

## Phase 5 — Repo Glue

### 9. Create root `README.md`
- Brief description of the demo project and what it showcases

### 10. Push to standalone repo & compile agentic workflows
- Copy/push this project folder to its own GitHub repo
- Move `workflows/` to `.github/workflows/`
- Run `gh aw compile` to generate `.lock.yml` files

---

## Target File Structure

```
2026-02-24-github_agentic_workflows/
├── AGENTS.md
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── src/
│   │   └── main.py
│   ├── tests/
│   │   └── test_main.py
│   └── AGENTS.md
├── frontend/
│   ├── package.json
│   ├── src/
│   │   └── routes/+page.svelte
│   ├── tests/
│   │   └── ...
│   └── AGENTS.md
└── workflows/                              # Move to .github/workflows/ in standalone repo
    ├── ci.yml                              # Standard CI
    ├── repo-activity-report.md             # Agentic: daily activity report
    └── code-relevance-checker.md           # Agentic: weekly code freshness check
```

---

## Implementation Order (Prompt Sequence)

| Prompt | Work |
|--------|------|
| **Prompt 1** | Scaffold FastAPI backend with uv, endpoints, and tests |
| **Prompt 2** | Scaffold SvelteKit frontend with page and tests |
| **Prompt 3** | Create standard CI workflow (`workflows/ci.yml`) |
| **Prompt 4** | Create the two agentic workflow `.md` files + all three `AGENTS.md` files |
