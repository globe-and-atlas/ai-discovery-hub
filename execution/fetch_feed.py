#!/usr/bin/env python3
"""
fetch_feed.py — AI Discovery Hub data fetcher
Pulls real content from YouTube, GitHub, Reddit, GIS Stack Exchange,
and Dev.to into hub-input.json.

Usage:
    python3 execution/fetch_feed.py
    python3 execution/fetch_feed.py --days 7 --max-videos 10
    python3 execution/fetch_feed.py --dry-run   # print counts, don't write

Sources:
    YouTube          → YOUTUBE_API_KEY or GOOGLE_API_KEY  (YouTube Data API v3)
    GitHub           → GITHUB_TOKEN                       (search/repositories)
    Reddit           → public .json endpoints, no auth needed
    GIS Stack Exch.  → public API, no auth needed (300 req/day; set STACKAPPS_KEY for 10k)
    Dev.to           → public API, no auth needed
"""

import argparse
import atexit
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build as yt_build

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

sys.path.insert(0, str(Path(__file__).parent))
import kb

_run_status = {"success": False, "notes": ""}

def _on_exit():
    if not _run_status["success"]:
        kb.log_session_event(PROJECT_ROOT, "fetch_feed.py", "exited_unexpectedly", _run_status["notes"])

atexit.register(_on_exit)

# ── Config ────────────────────────────────────────────────────────────────────

YOUTUBE_CHANNELS = [
    # (channel_id, display_name)
    # AI / Dev
    ("UCsBjURrPoezykLs9EqgamOA", "Fireship"),
    ("UCXUPKJO5MZQN11PqgIvyuvQ", "Andrej Karpathy"),
    ("UCbmNph6atAoGfqLoCL_duAg", "Two Minute Papers"),
    ("UCZHmQk67mSJgfCCTn7xBfew", "Yannic Kilcher"),
    ("UC9-y-6csu5WGm29I7JiwpnA", "Computerphile"),
    ("UCnUYZLuoy1rq1aVMwx4aTzw", "sentdex"),
    ("UCVls1GmFKf6WlTraIb_IaJg", "Dot CSV"),
    ("UCHnyfMqiRRG1u-2MsSQLbXA", "Veritasium"),
    # GIS / FME / Esri
    ("UCzsMS2DDlOJCBgR5jVR3-OQ", "Safe Software"),
    ("UCG-fzkzsubKoHMbOsTFfuqg", "QGIS"),
    ("UCEKRzZLJlLqFIHCZOIcVqSw", "Esri Events"),
    ("UCgox_J_6tnLBVBcIFRqxFSQ", "Esri"),
    # Satellite / Remote Sensing / Imagery
    ("UCuFg2HFi_yImX_J6Cjg1Y0w", "Sentinel Hub"),
    ("UCgKDDMNpbiEMtJB6CZEhTZg", "Planet Labs"),
    ("UCKPZPBKkHcMqILhFEMHYbzw", "Maxar Technologies"),
    ("UC9QRSGanKSWMjpfNLNHO2Rg", "Google Earth"),
]

YOUTUBE_SEARCH_QUERIES = [
    "Claude Code AI agent 2026",
    "ChatGPT GPT-4o agent workflow 2026",
    "Gemini Google AI geospatial 2026",
    "LLM local inference Ollama 2026",
    "geospatial AI GIS machine learning 2026",
    "AI coding assistant tutorial 2026",
    "multi-agent AI workflow 2026",
    "FME Safe Software automation 2026",
    "Esri ArcGIS AI artificial intelligence 2026",
    "QGIS AI plugin geospatial 2026",
    "satellite imagery AI analysis 2026",
    "drone UAV AI imagery analysis 2026",
    "multispectral hyperspectral AI remote sensing 2026",
    "thermal imagery AI anomaly detection 2026",
    "Sentinel-2 machine learning classification 2026",
    "Google Earth Engine AI analysis 2026",
]

GITHUB_TOPICS = [
    # LLM / AI
    "llm", "ai-agent", "mcp-server", "local-llm", "claude", "openai", "gemini",
    "langchain", "ollama", "anthropic",
    # GIS / Geospatial
    "geospatial-ai", "geoai", "qgis", "geemap", "sentinel-hub", "spatial-data",
    "arcgis", "esri", "fme", "remote-sensing",
    # Imagery
    "satellite-imagery", "multispectral", "hyperspectral", "sar",
    "drone", "uav", "thermal-imaging", "change-detection",
]

REDDIT_SUBREDDITS = [
    "MachineLearning",
    "LocalLLaMA",
    "artificial",
    "ClaudeAI",
    "ChatGPT",
    "Bard",
    "singularity",
    "gis",
    "remotesensing",
    "geospatial",
]

REDDIT_HEADERS = {
    "User-Agent": "ai-discovery-hub/1.0 (scraper; public data only)"
}

# GIS Stack Exchange — questions at the AI/GIS intersection
# Site: gis.stackexchange.com  (site=gis in API)
STACKEXCHANGE_TAG_SETS = [
    "machine-learning",
    "artificial-intelligence",
    "python",
    "qgis+python",
    "fme-desktop",
    "remote-sensing",
    "satellite-imagery",
]

# Dev.to — practitioner tutorials tagged for the AI/GIS stack
DEVTO_TAGS = [
    "gis",
    "machinelearning",
    "artificialintelligence",
    "python",
    "satellite",
    "geospatial",
]

# ── YouTube ───────────────────────────────────────────────────────────────────

def _parse_duration(iso: str) -> str:
    """Convert ISO 8601 duration (PT4M13S) → human string (4:13 / 1:02:03)."""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or "")
    if not m:
        return ""
    h, mn, s = (int(x) if x else 0 for x in m.groups())
    if h:
        return f"{h}:{mn:02d}:{s:02d}"
    return f"{mn}:{s:02d}"

def _fetch_durations(yt, video_ids: list) -> dict:
    """Batch-fetch contentDetails durations for up to 50 IDs at a time."""
    durations = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        try:
            resp = yt.videos().list(part="contentDetails", id=",".join(batch)).execute()
            for item in resp.get("items", []):
                durations[item["id"]] = _parse_duration(item["contentDetails"]["duration"])
        except Exception as e:
            print(f"  [WARN] Duration fetch: {e}")
    return durations

def fetch_youtube(days: int, max_videos: int) -> list[dict]:
    api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("  [WARN] No YOUTUBE_API_KEY / GOOGLE_API_KEY — skipping YouTube")
        return []

    yt = yt_build("youtube", "v3", developerKey=api_key)
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    videos = []

    # Channel uploads
    for channel_id, channel_name in YOUTUBE_CHANNELS:
        try:
            resp = yt.search().list(
                part="snippet",
                channelId=channel_id,
                publishedAfter=since,
                maxResults=3,
                order="date",
                type="video",
            ).execute()
            for item in resp.get("items", []):
                vid_id = item["id"]["videoId"]
                snippet = item["snippet"]
                videos.append({
                    "title": snippet["title"],
                    "channel": channel_name,
                    "date": snippet["publishedAt"][:10],
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                    "summary": snippet.get("description", "")[:200],
                })
        except Exception as e:
            print(f"  [WARN] YouTube channel {channel_name}: {e}")
        time.sleep(0.1)

    # Keyword search
    for query in YOUTUBE_SEARCH_QUERIES:
        try:
            resp = yt.search().list(
                part="snippet",
                q=query,
                publishedAfter=since,
                maxResults=2,
                order="relevance",
                type="video",
            ).execute()
            for item in resp.get("items", []):
                vid_id = item["id"]["videoId"]
                snippet = item["snippet"]
                url = f"https://www.youtube.com/watch?v={vid_id}"
                if any(v["url"] == url for v in videos):
                    continue
                videos.append({
                    "title": snippet["title"],
                    "channel": snippet.get("channelTitle", ""),
                    "date": snippet["publishedAt"][:10],
                    "url": url,
                    "summary": snippet.get("description", "")[:200],
                })
        except Exception as e:
            print(f"  [WARN] YouTube search '{query}': {e}")
        time.sleep(0.1)

    # Dedupe by URL, sort by date desc, trim
    seen = set()
    unique = []
    for v in sorted(videos, key=lambda x: x["date"], reverse=True):
        if v["url"] not in seen:
            seen.add(v["url"])
            unique.append(v)

    capped = unique[:max_videos]

    # Batch-fetch durations
    vid_ids = [v["url"].split("v=")[-1] for v in capped]
    durations = _fetch_durations(yt, vid_ids)
    for v in capped:
        v["duration"] = durations.get(v["url"].split("v=")[-1], "")

    print(f"  YouTube: {len(capped)} videos (capped at {max_videos})")
    return capped


# ── GitHub ────────────────────────────────────────────────────────────────────

def fetch_github(days: int, max_repos: int) -> list[dict]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    repos = []
    seen_ids = set()

    for topic in GITHUB_TOPICS:
        query = f"topic:{topic} pushed:>{since} stars:>10"
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": 5},
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            for repo in resp.json().get("items", []):
                if repo["id"] in seen_ids:
                    continue
                seen_ids.add(repo["id"])
                repos.append({
                    "name": repo["full_name"],
                    "description": (repo.get("description") or "")[:200],
                    "stars": repo["stargazers_count"],
                    "url": repo["html_url"],
                    "date": repo["pushed_at"][:10],
                    "topics": repo.get("topics", [])[:5],
                    "language": repo.get("language") or "",
                })
        except Exception as e:
            print(f"  [WARN] GitHub topic '{topic}': {e}")
        time.sleep(0.1)

    repos.sort(key=lambda x: x["stars"], reverse=True)
    print(f"  GitHub: {len(repos)} repos (capped at {max_repos})")
    return repos[:max_repos]


# ── Reddit ─────────────────────────────────────────────────────────────────────

def fetch_reddit(days: int, max_posts: int) -> list[dict]:
    """Scrapes Reddit's public .json endpoints — no API key required."""
    cutoff = time.time() - days * 86400
    signals = []

    for sub_name in REDDIT_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub_name}/hot.json?limit=25"
        try:
            resp = requests.get(url, headers=REDDIT_HEADERS, timeout=10)
            resp.raise_for_status()
            posts = resp.json().get("data", {}).get("children", [])
            for child in posts:
                post = child.get("data", {})
                if post.get("created_utc", 0) < cutoff:
                    continue
                if post.get("score", 0) < 50:
                    continue
                # Skip stickied mod posts
                if post.get("stickied"):
                    continue
                permalink = post.get("permalink", "")
                signals.append({
                    "title": post.get("title", "")[:120],
                    "url": f"https://www.reddit.com{permalink}",
                    "source": f"r/{sub_name}",
                    "date": datetime.fromtimestamp(post["created_utc"]).strftime("%Y-%m-%d"),
                    "score": post.get("score", 0),
                    "comments": post.get("num_comments", 0),
                    "summary": (post.get("selftext") or post.get("url") or "")[:200],
                })
        except Exception as e:
            print(f"  [WARN] Reddit r/{sub_name}: {e}")
        time.sleep(0.5)  # be polite

    signals.sort(key=lambda x: x["score"], reverse=True)
    print(f"  Reddit: {len(signals)} signals (capped at {max_posts})")
    return signals[:max_posts]


# ── GIS Stack Exchange ────────────────────────────────────────────────────────

def fetch_stack_exchange(days: int, max_questions: int) -> list[dict]:
    """Fetch recent high-signal questions from gis.stackexchange.com."""
    cutoff = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    api_key = os.getenv("STACKAPPS_KEY")  # optional — raises rate limit from 300 to 10k/day
    seen_ids: set = set()
    questions = []

    for tags in STACKEXCHANGE_TAG_SETS:
        params = {
            "site": "gis",
            "tagged": tags,
            "sort": "votes",
            "order": "desc",
            "fromdate": cutoff,
            "pagesize": 10,
            "filter": "withbody",
        }
        if api_key:
            params["key"] = api_key
        try:
            resp = requests.get(
                "https://api.stackexchange.com/2.3/questions",
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
            for q in resp.json().get("items", []):
                qid = q["question_id"]
                if qid in seen_ids:
                    continue
                seen_ids.add(qid)
                questions.append({
                    "title": q["title"],
                    "url": q["link"],
                    "score": q.get("score", 0),
                    "answers": q.get("answer_count", 0),
                    "date": datetime.fromtimestamp(q["creation_date"]).strftime("%Y-%m-%d"),
                    "tags": q.get("tags", [])[:6],
                    "summary": re.sub(r"<[^>]+>", "", q.get("body", ""))[:200].strip(),
                })
        except Exception as e:
            print(f"  [WARN] Stack Exchange tags '{tags}': {e}")
        time.sleep(0.2)

    questions.sort(key=lambda x: x["score"], reverse=True)
    print(f"  GIS Stack Exchange: {len(questions)} questions (capped at {max_questions})")
    return questions[:max_questions]


# ── Dev.to ────────────────────────────────────────────────────────────────────

def fetch_devto(days: int, max_articles: int) -> list[dict]:
    """Fetch recent practitioner articles from Dev.to filtered by tag."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    seen_ids: set = set()
    articles = []

    for tag in DEVTO_TAGS:
        try:
            resp = requests.get(
                "https://dev.to/api/articles",
                params={"tag": tag, "top": days, "per_page": 10},
                headers={"User-Agent": "ai-discovery-hub/1.0"},
                timeout=10,
            )
            resp.raise_for_status()
            for a in resp.json():
                aid = a.get("id")
                if aid in seen_ids:
                    continue
                published = a.get("published_at", "")
                if published:
                    pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    if pub_dt < cutoff:
                        continue
                seen_ids.add(aid)
                articles.append({
                    "title": a.get("title", "")[:120],
                    "url": a.get("url", ""),
                    "reactions": a.get("positive_reactions_count", 0),
                    "comments": a.get("comments_count", 0),
                    "date": published[:10] if published else "",
                    "tags": a.get("tag_list", [])[:5],
                    "summary": (a.get("description") or "")[:200],
                })
        except Exception as e:
            print(f"  [WARN] Dev.to tag '{tag}': {e}")
        time.sleep(0.2)

    articles.sort(key=lambda x: x["reactions"], reverse=True)
    print(f"  Dev.to: {len(articles)} articles (capped at {max_articles})")
    return articles[:max_articles]


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real feed data for AI Discovery Hub")
    parser.add_argument("--days",       type=int, default=7,  help="Lookback window in days")
    parser.add_argument("--max-videos", type=int, default=10, help="Max YouTube videos")
    parser.add_argument("--max-repos",  type=int, default=15, help="Max GitHub repos")
    parser.add_argument("--max-posts",      type=int, default=10, help="Max Reddit posts")
    parser.add_argument("--max-questions",  type=int, default=15, help="Max GIS Stack Exchange questions")
    parser.add_argument("--max-articles",   type=int, default=10, help="Max Dev.to articles")
    parser.add_argument("--dry-run",        action="store_true",  help="Print counts, skip write")
    args = parser.parse_args()

    print(f"Fetching feed — last {args.days} days...")

    try:
        videos    = fetch_youtube(args.days, args.max_videos)
        tools     = fetch_github(args.days, args.max_repos)
        signals   = fetch_reddit(args.days, args.max_posts)
        questions = fetch_stack_exchange(args.days, args.max_questions)
        tutorials = fetch_devto(args.days, args.max_articles)
    except Exception as e:
        kb.log_error(PROJECT_ROOT, "fetch_feed.py", f"Feed fetch failed: {type(e).__name__}", str(e)[:120])
        kb.log_session_event(PROJECT_ROOT, "fetch_feed.py", "failed", str(e)[:80])
        raise

    output = {
        "scanned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": args.days,
        "videos":    videos,
        "tools":     tools,
        "signals":   signals,
        "questions": questions,
        "tutorials": tutorials,
    }

    print(f"\nTotals: {len(videos)} videos · {len(tools)} repos · {len(signals)} signals · {len(questions)} questions · {len(tutorials)} tutorials")

    if args.dry_run:
        print("\n[dry-run] Sample output:")
        print(json.dumps(output, indent=2)[:800])
        return

    out_path = PROJECT_ROOT / "data" / "hub-input.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nWritten → {out_path}")
    print("Next: python3 execution/build_hub.py")

    _run_status["success"] = True
    kb.log_session_event(
        PROJECT_ROOT, "fetch_feed.py", "completed",
        f"{len(videos)} videos · {len(tools)} repos · {len(signals)} signals · {len(questions)} questions · {len(tutorials)} tutorials"
    )


if __name__ == "__main__":
    main()
