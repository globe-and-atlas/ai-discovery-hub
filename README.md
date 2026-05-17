# Ai Discovery Hub


## Run

Use the project-specific files first, then run the local app or workflow with the runtime listed in `project.profile.json`.

```bash
# Inspect the project shape
cat project.profile.json

# Review current work
cat task.md
```

## Structure

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` — mirrored agent instructions
- `directives/` — SOPs and validation contracts when this project uses directives
- `knowledge/` — session, error, decision, domain, and procedural notes
- `task.md` — current objective and acceptance criteria

## Notes

Ai Discovery Hub is tracked as an active workspace project using `python`. Before feature work, update `task.md` with project-specific acceptance criteria and run the relevant local build, test, or workflow command.

## Health Check

- Confirm dependencies before running the pipeline.
- Keep generated outputs out of source control unless they are intended deliverables.
- Record deterministic failures in `knowledge/ERRORS.md`.
- Update `knowledge/SESSION.md` after each significant pipeline run.
