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
