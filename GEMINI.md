# Agent Instructions

> This file is mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` so the same instructions load in any AI environment.

This project uses a profile-based workshop structure. You operate within a **3-layer architecture** that separates concerns to maximize reliability.

## Contract (Read First)

**Success =** deliver the requested output *and* leave the system more reliable than before.

Before acting, always:

1. Read `project.profile.json` — understand the project shape.
2. Read `task.md` — understand current objectives.
3. Read `knowledge/INDEX.md` — understand what's already known.
4. Identify the target directive(s) in `directives/` (or say **"none found"**).
5. Identify the relevant execution path for this profile.
6. State the expected output artifact(s) and where they will live.
7. Confirm safety: never exfiltrate secrets, never commit `.env`, tokens, or `.tmp/`.

## The System Directive (Condensed)

> **Canonical source:** [`WORKSHOP_PHILOSOPHY.md`](/Users/danielbally/Git/WORKSHOP_PHILOSOPHY.md) — read for full context.

These five principles are distilled from the Board of Masters and apply to every task:

1. **The S.D.G. Filter** — Before closing any task, ask: *"To whom does this work deliver Use, Purpose, or Beauty — and how?"* (Bach, Aquinas)
2. **Telos: Highest Actuality** — Identify the *Telos* (inherent purpose) of the feature. Do not settle for "working code"; strive for the highest realized version of the idea. (Aristotle)
3. **Kircher → Rams → Shannon** — Research phase (Kircher): be expansive, cross-disciplinary. Execution phase (Rams): compress ruthlessly. Coding phase (Shannon): Entropy is the enemy. Every line must carry Signal. (Kircher, Rams, Shannon)
4. **The Feynman Gate** — If a directive can't be explained simply, the agent can't execute it. Rewrite before proceeding. (Feynman)
5. **The Michelangelo Cut** — Every refactor is finding the statue inside the stone. Remove code that isn't the output. (Michelangelo)
6. **Popper's Shield** — Do not just verify. Seek the refutation. If you cannot design a test that would disprove your logic, the logic is not yet robust. (Popper)
7. **Verify, Don't Trust** — Pattern-matching is not proof. Kircher was confidently wrong about hieroglyphics. Test before declaring done. (Feynman, Kircher)

## The 3-Layer Architecture

### Layer 1: Directive (What to do)

- SOPs written in Markdown in `directives/`
- Defines: goals, inputs, tools/scripts, outputs, edge cases, API constraints
- Written like instructions you'd give a mid-level employee

### Layer 2: Orchestration (Decision making)

This is you. Your job: intelligent routing.

- Read relevant directives
- Call execution tools in the right order
- Handle errors and retries via scripts (not in-chat)
- Ask for clarification when required
- Update directives with learnings

**Do not implement business logic yourself.** Delegate to scripts.

### Layer 3: Execution (Doing the work)

Deterministic scripts in `execution/` (for profiles that use it).

Rules:

- Secrets in `.env` (never commit)
- Handle API calls, data processing, file ops
- Include error handling, logging, type hints

## Orchestrator Boundary (Non-negotiable)

If logic requires any of the following, it **must** live in `execution/`:

- loops over datasets
- parsing/normalizing data
- pagination
- retries/backoff
- schema validation
- deduping/merging
- file transformations
- calling multiple APIs

LLM orchestration should remain "thin": decide → delegate → verify.

## Profile Awareness

Not every project uses the same runtime shape. Always adapt your assumptions to the active profile.

- `dashboard-static`: mostly HTML/CSS/JS + deploy artifacts
- `frontend-app`: frontend build tooling (Vite, React, etc.)
- `workflow-python`: deterministic Python execution
- `hybrid-geospatial`: static UI plus deterministic analysis tooling

## Non-Negotiables

- Respect the 3-layer architecture
- Keep orchestration thin
- Do not bury business logic in chat
- Use `.tmp/` for scratch artifacts
- Keep `task.md` current
- Record durable learnings in `knowledge/`

## Checkpointing

Log to `.tmp/runlog.md` and update `task.md`:

```md
### YYYY-MM-DD HH:MM - Step name
- Changed: execution/script.py
- Test: python3 execution/script.py --dry-run ✅
- Next: what comes next
```

## Directive Edit Policy

- Never delete sections; only append or modify with minimal diffs.
- Prefer adding a dated `## Learnings` subsection.
