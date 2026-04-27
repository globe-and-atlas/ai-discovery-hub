# API Constraints — AI Discovery Hub

---

## Anthropic API

- **Model in use:** `claude-sonnet-4-6` (set via `HUB_MODEL` in `.env`)
- **529 OverloadedError:** Transient rate limit or platform outage. Retry with backoff: 15s → 30s → 45s → fail. If sustained >5 min, it's likely a platform outage — wait and retry later.
- **Parallel requests:** Running multiple API calls simultaneously from the same key triggers 529s quickly. Run `expand_lab.py` calls sequentially, not in parallel background processes.
- **max_tokens:** `build_hub.py` uses 7000; `expand_lab.py` uses 8192. Do not reduce below 4000 — LLM truncates JSON output.

## GitHub API

- **Auth:** `GITHUB_TOKEN` in `.env`. Uses Fine-Grained PAT or Classic PAT with `public_repo` scope.
- **401 Unauthorized:** Token expired or missing. Generate new at github.com/settings/tokens.
- **dotenv loads first occurrence only.** If `.env` has duplicate `GITHUB_TOKEN` lines, only the first is used. Always check for duplicates after appending new tokens.
- **Rate limit (unauthenticated):** 60 req/hr. Authenticated: 5000 req/hr. Always provide token.
- **Search endpoint:** `GET /search/repositories` — used for topic searches. Returns at most 1000 results. Hub uses `per_page=5` per topic.

## YouTube Data API v3

- **Key:** `YOUTUBE_API_KEY` or falls back to `GOOGLE_API_KEY` in `.env`.
- **Quota:** 10,000 units/day. `search.list` costs 100 units per call. Hub runs ~27 searches (11 channels × 1 + 16 keyword queries) = ~2700 units per fetch. Safe within daily quota.
- **Channel search cap:** `maxResults=3` per channel, `maxResults=2` per keyword query.
- **Duration fetch:** Batched in groups of 50 via `videos.list` (contentDetails). Costs 1 unit per call.

## Reddit (public .json)

- **No auth required.** Uses public `.json` endpoints (`/r/{sub}/hot.json`).
- **Rate limit:** Be polite — 0.5s sleep between subreddit requests.
- **User-Agent required:** Set to `ai-discovery-hub/1.0` — Reddit blocks default Python user agents.
- **Score filter:** Posts with score < 50 are filtered out to reduce noise.
