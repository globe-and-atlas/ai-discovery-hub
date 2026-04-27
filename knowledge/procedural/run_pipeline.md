# Run Pipeline — AI Discovery Hub

## Full Weekly Refresh (fetch new data + regenerate content)

```bash
cd /Users/danielbally/Git/ai-discovery-hub

# 1. Fetch all sources (YouTube, GitHub, Reddit)
python3 execution/fetch_feed.py

# 2. Generate hub content via LLM + render dashboard
python3 execution/build_hub.py

# 3. Generate curricula for all lab exercises (sequentially — parallel causes 529s)
python3 execution/expand_lab.py --list  # confirm exercise count
for i in 1 2 3 4; do python3 execution/expand_lab.py --item $i; done

# 4. Re-render dashboard with curriculum links (no LLM call)
python3 execution/build_hub.py --render-only

# 5. Open result
open dashboards/latest.html
```

## Re-render Only (no new data, no LLM call)

Use after: generating curricula, changing dashboard CSS/HTML, debugging layout.

```bash
python3 execution/build_hub.py --render-only
open dashboards/latest.html
```

## Expand a Single Lab Exercise

```bash
python3 execution/expand_lab.py --list          # list available exercises
python3 execution/expand_lab.py --item N        # generate curriculum for item N
python3 execution/build_hub.py --render-only    # re-render to link tutorial
```

## Key Rules

- **Never run expand_lab.py calls in parallel.** Parallel Anthropic API calls from the same key trigger 529 overload errors. Always sequential.
- **Always run `--render-only` after generating curricula.** Skipping this means lab cards show the CLI command instead of the tutorial link.
- **After a full `build_hub.py` run, always regenerate curricula.** The LLM rewrites exercise titles each run. `expand_lab.py` writes `curriculum_path` into `hub-output.json` — this is what keeps links stable. Without running expand_lab after each build, links break.
- **GitHub token:** Expires. If GitHub returns 0 repos, check for 401 in fetch output. Regenerate at github.com/settings/tokens (`public_repo` scope sufficient).
- **dotenv duplicate keys:** If you append a new token to `.env`, check for duplicate key entries. Dotenv uses the FIRST occurrence.

## Output Locations

| Artifact | Location |
|---|---|
| Raw feed data | `data/hub-input.json` |
| LLM-processed hub content | `data/hub-output.json` |
| Dashboard HTML | `dashboards/AI-Discovery-Hub-YYYY-MM-DD.html` |
| Latest dashboard | `dashboards/latest.html` |
| Curriculum markdown | `curriculums/YYYY-MM-DD-{slug}.md` |
| Curriculum HTML pages | `dashboards/curricula/{slug}.html` |
