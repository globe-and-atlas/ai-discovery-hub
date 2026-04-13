#!/usr/bin/env python3
"""
fetch_feed.py — AI Discovery Hub data fetcher
Pulls real content from YouTube, GitHub, and Reddit into hub-input.json.

Usage:
    python3 execution/fetch_feed.py
    python3 execution/fetch_feed.py --days 7 --max-videos 10
    python3 execution/fetch_feed.py --dry-run   # print counts, don't write

Sources:
    YouTube  → YOUTUBE_API_KEY or GOOGLE_API_KEY  (YouTube Data API v3)
    GitHub   → GITHUB_TOKEN                       (search/repositories)
    Reddit   → public .json endpoints, no auth needed
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build as yt_build

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── Config ────────────────────────────────────────────────────────────────────

YOUTUBE_CHANNELS = [
    # (channel_id, display_name)
    ("UCsBjURrPoezykLs9EqgamOA", "Fireship"),
    ("UCXUPKJO5MZQN11PqgIvyuvQ", "Andrej Karpathy"),
    ("UCbmNph6atAoGfqLoCL_duAg", "Two Minute Papers"),
    ("UCZHmQk67mSJgfCCTn7xBfew", "Yannic Kilcher"),
    ("UC9-y-6csu5WGm29I7JiwpnA", "Computerphile"),
    ("UCnUYZLuoy1rq1aVMwx4aTzw", "sentdex"),
    ("UCVls1GmFKf6WlTraIb_IaJg", "Dot CSV"),
    ("UCHnyfMqiRRG1u-2MsSQLbXA", "Veritasium"),
    # GIS/FME
    ("UCzsMS2DDlOJCBgR5jVR3-OQ", "Safe Software"),          # FME
    ("UCG-fzkzsubKoHMbOsTFfuqg", "QGIS"),
    ("UCEKRzZLJlLqFIHCZOIcVqSw", "Esri Events"),
]

YOUTUBE_SEARCH_QUERIES = [
    "Claude Code AI agent 2026",
    "LLM local inference Ollama 2026",
    "geospatial AI GIS machine learning",
    "AI coding assistant tutorial",
    "multi-agent AI workflow 2026",
    "FME Safe Software automation 2026",
    "QGIS AI plugin geospatial",
    "satellite imagery AI analysis 2026",
]

GITHUB_TOPICS = [
    "llm", "ai-agent", "mcp-server", "local-llm",
    "geospatial-ai", "claude", "langchain", "ollama",
    "fme", "geoai", "qgis", "geemap", "sentinel-hub", "spatial-data",
]

REDDIT_SUBREDDITS = [
    "MachineLearning",
    "LocalLLaMA",
    "artificial",
    "ClaudeAI",
    "singularity",
    "gis",
]

REDDIT_HEADERS = {
    "User-Agent": "ai-discovery-hub/1.0 (scraper; public data only)"
}

# ── YouTube ───────────────────────────────────────────────────────────────────

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

    print(f"  YouTube: {len(unique)} videos (capped at {max_videos})")
    return unique[:max_videos]


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


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real feed data for AI Discovery Hub")
    parser.add_argument("--days",       type=int, default=7,  help="Lookback window in days")
    parser.add_argument("--max-videos", type=int, default=10, help="Max YouTube videos")
    parser.add_argument("--max-repos",  type=int, default=15, help="Max GitHub repos")
    parser.add_argument("--max-posts",  type=int, default=10, help="Max Reddit posts")
    parser.add_argument("--dry-run",    action="store_true",  help="Print counts, skip write")
    args = parser.parse_args()

    print(f"Fetching feed — last {args.days} days...")

    videos  = fetch_youtube(args.days, args.max_videos)
    tools   = fetch_github(args.days, args.max_repos)
    signals = fetch_reddit(args.days, args.max_posts)

    output = {
        "scanned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": args.days,
        "videos":  videos,
        "tools":   tools,
        "signals": signals,
    }

    print(f"\nTotals: {len(videos)} videos · {len(tools)} repos · {len(signals)} signals")

    if args.dry_run:
        print("\n[dry-run] Sample output:")
        print(json.dumps(output, indent=2)[:800])
        return

    out_path = PROJECT_ROOT / "data" / "hub-input.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nWritten → {out_path}")
    print("Next: python3 execution/build_hub.py")


if __name__ == "__main__":
    main()
