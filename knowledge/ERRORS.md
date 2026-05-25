# ERRORS — AI Discovery Hub

Log of deterministic errors (concluded) and infrastructure errors (pattern-tracked).

---

## 2026-04-22 — Duplicate GITHUB_TOKEN in .env

**Error:** GitHub API returning 401 on all topic searches.
**Cause:** `.env` had two `GITHUB_TOKEN` entries — old expired token (line 24) and new token appended at end (line 30). Python-dotenv uses the first occurrence, which was the expired one.
**Fix:** Removed the duplicate; kept the new token as the single entry.
**Graduated to:** `knowledge/domain/api_constraints.md` — dotenv loads first occurrence only.

---

## 2026-04-22 — Exercise title drift breaks curriculum links

**Error:** Lab items show CLI command instead of "📖 View tutorial →" link after a full `build_hub.py` run.
**Cause:** `build_hub.py` calls the LLM on every full run. LLM rewrites exercise titles with slightly different wording each time. `_build_curriculum_pages()` slug-matched against filenames, so new titles → no match.
**Fix:** `expand_lab.py` now writes `curriculum_path` back into `hub-output.json` after each successful generation. `_build_curriculum_pages()` reads `exercise["curriculum_path"]` first, falls back to slug glob.
**Graduated to:** `knowledge/procedural/run_pipeline.md` — always run `--render-only` after expanding curricula.

---

## 2026-04-23 — Anthropic API 529 overload on parallel curriculum generation

**Error:** All 4 `expand_lab.py` calls fail with `OverloadedError: Error code: 529`.
**Cause:** Running all 4 as parallel background processes simultaneously. Anthropic rate-limits concurrent requests from the same API key.
**Fix (code):** Added exponential backoff retry (15s / 30s / 45s / fail) to `generate_curriculum()` in `expand_lab.py`.
**Fix (process):** Run sequentially with `for i in 1 2 3 4; do python3 execution/expand_lab.py --item $i; done`.
**Note:** 529 can also be a platform-wide outage (sustained for 10+ min = outage, not rate limit). Wait and retry.
**Graduated to:** `knowledge/domain/api_constraints.md`.

---

## Infrastructure Errors (pattern-tracked, no conclusion yet)

| Date | Error | Context |
|---|---|---|
| 2026-04-23 | 529 sustained 10+ min | Possible Anthropic platform outage mid-morning |
| 2026-04-27 | build_hub.py | LLM call failed: APIConnectionError | (investigate) |
| 2026-05-04 | build_hub.py | LLM call failed: APIConnectionError | (investigate) |
| 2026-05-22 | fetch_feed.py | Sandbox DNS blocked all external sources; first run wrote a 0-item `hub-input.json`, then approved network rerun restored live counts |
| 2026-05-22 | fetch_feed.py | YouTube API returned per-minute 429s mid-run; fetch still produced capped 10 videos from successful earlier calls |

## 2026-05-22 — Template health-check command unavailable

**Error:** `python3 scripts/health_check.py` failed with `No such file or directory`.
**Cause:** This project does not include `scripts/health_check.py`, despite workspace/template task language asking for a project-specific health check.
**Fix:** Use available verification for refresh runs: `python3 -m py_compile execution/fetch_feed.py execution/build_hub.py execution/expand_lab.py`, JSON load/count checks for `data/hub-input.json` and `data/hub-output.json`, and link checks in `dashboards/latest.html`.
**Graduated to:** pending; likely a project governance scaffold gap rather than a pipeline bug.

## 2026-05-22 — `expand_lab.py --list` logs false unexpected exit

**Error:** `.venv/bin/python3 execution/expand_lab.py --list` printed exercises successfully but appended `expand_lab.py → exited_unexpectedly` to `knowledge/SESSION.md`.
**Cause:** The atexit handler treats any path where `_run_status["success"]` remains false as unexpected, and the `--list` branch exited before setting success.
**Fix:** Set `_run_status["success"] = True` before the successful `--list` exit.
**Graduated to:** no; local script status bookkeeping fix.
