#!/usr/bin/env python3
"""
expand_lab.py — Curriculum Generator for AI Discovery Hub
Takes a short exercise from the latest Lab (hub-output.json) and uses an LLM
to generate a comprehensive, step-by-step markdown tutorial.
"""

import atexit
import html as _html
import os
import sys
import json
import argparse
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import time
import anthropic

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

sys.path.insert(0, str(Path(__file__).parent))
import kb

_run_status = {"success": False, "notes": ""}

def _on_exit():
    if not _run_status["success"]:
        kb.log_session_event(PROJECT_ROOT, "expand_lab.py", "exited_unexpectedly", _run_status["notes"])

atexit.register(_on_exit)

def get_client():
    provider = os.getenv("HUB_PROVIDER", "anthropic")
    if provider == "anthropic":
        return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return genai.GenerativeModel(os.getenv("HUB_MODEL", "gemini-1.5-pro"))
    raise ValueError(f"Provider {provider} not implemented yet.")

def fetch_source_content(url: str, max_chars: int = 6000) -> str:
    """Fetch readable text from a source URL. Returns empty string on any failure."""
    if not url:
        return ""
    # GitHub repo root → fetch README via raw content API
    gh = re.match(r'https?://github\.com/([^/]+/[^/?#]+)/?$', url)
    if gh:
        repo = gh.group(1)
        for branch in ("main", "master"):
            raw = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
            try:
                req = urllib.request.Request(raw, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    return r.read().decode("utf-8", errors="replace")[:max_chars]
            except Exception:
                continue
        return ""
    # General URL: fetch HTML, strip tags
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            if "text" not in r.headers.get("Content-Type", ""):
                return ""
            raw = r.read().decode("utf-8", errors="replace")
        raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", raw)
        text = _html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception:
        return ""


def generate_curriculum(exercise: dict, artifact: dict) -> str:
    provider = os.getenv("HUB_PROVIDER", "anthropic")
    model_name = os.getenv("HUB_MODEL", "claude-3-5-sonnet-latest")
    
    source_url = artifact.get('url', '')
    print(f"  Fetching source content from {source_url or '(no URL)'}...")
    source_content = fetch_source_content(source_url)
    if source_content:
        print(f"  Fetched {len(source_content)} chars of source content.")
        source_block = f"""SOURCE CONTENT (fetched directly — treat as ground truth for commands, APIs, and flags):
{source_content}"""
        grounded_note = "Base all specific commands, flags, and API calls strictly on the SOURCE CONTENT above. If the source does not cover a step, say so explicitly rather than inventing details."
    else:
        print("  Could not fetch source — generating from metadata only.")
        source_block = "(Source content unavailable — could not fetch URL.)"
        grounded_note = "Source content could not be fetched. Where you are uncertain about specific commands or API signatures, mark them clearly with a ⚠️ UNVERIFIED comment so the reader knows to check official docs."

    prompt = f"""You are an expert AI curriculum designer writing directly for Daniel, a GIS/AI practitioner.
Your goal is to create a comprehensive, step-by-step hands-on tutorial grounded in the source material below.

EXERCISE GOAL:
Title: {exercise['title']}
Effort: {exercise['effort']}
Description: {exercise['desc']}

SOURCE ARTIFACT:
Title: {artifact.get('title', '')}
Type: {artifact.get('type', '')}
Source: {artifact.get('source', '')}
URL: {source_url}
Description: {artifact.get('desc', '')}
Why it matters: {artifact.get('relevance_why', '')}

{source_block}

INSTRUCTIONS:
{grounded_note}

Create a complete tutorial. It MUST include:
1. Introduction & Context: What this is and why it's worth your time.
2. Prerequisites: What you need before starting.
3. Step-by-Step Guide: Practical instructions. Include code snippets, CLI commands, or UI steps.
4. Validation: How you verify you completed the exercise successfully.
5. Next Steps: Where to go from here.

Output ONLY valid Markdown. Use formatting, headers, and code blocks appropriately."""

    print(f"  Calling {provider} ({model_name}) to generate curriculum...")

    if provider == "anthropic":
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        for attempt in range(1, 5):
            try:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except anthropic.APIStatusError as e:
                if e.status_code == 529 and attempt < 4:
                    wait = 15 * attempt
                    print(f"  API overloaded (529) — retrying in {wait}s (attempt {attempt}/4)...")
                    time.sleep(wait)
                else:
                    raise
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    else:
        raise ValueError(f"Provider {provider} not supported.")

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text).strip('-')

def main():
    parser = argparse.ArgumentParser(description="Expand a Lab exercise into a full curriculum.")
    parser.add_argument("--item", type=int, help="The 1-indexed number of the exercise to expand.")
    parser.add_argument("--list", action="store_true", help="List all available exercises in the current hub output.")
    args = parser.parse_args()

    output_path = PROJECT_ROOT / "data" / "hub-output.json"
    if not output_path.exists():
        print(f"Error: {output_path} not found. Please run python3 execution/build_hub.py first.")
        sys.exit(1)

    with open(output_path, "r") as f:
        data = json.load(f)

    exercises = data.get("exercises", [])
    artifacts = data.get("artifacts", [])

    if not exercises:
        print("No exercises found in hub-output.json.")
        sys.exit(0)

    if args.list or not args.item:
        print("Available Lab Exercises:")
        for i, ex in enumerate(exercises, start=1):
            print(f"  [{i}] {ex['title']} ({ex['effort']} effort)")
            print(f"      - {ex['desc']}")
        print("\nUse --item <number> to generate a curriculum.")
        sys.exit(0)

    if args.item < 1 or args.item > len(exercises):
        print(f"Error: Invalid item number {args.item}. Must be between 1 and {len(exercises)}.")
        sys.exit(1)

    exercise = exercises[args.item - 1]
    
    # Find matching artifact
    source_title = exercise.get("source_artifact", "")
    matching_artifact = next((a for a in artifacts if a.get("title") == source_title), {})

    print(f"Expanding Exercise [{args.item}]: {exercise['title']}")
    _run_status["notes"] = f"item {args.item}: {exercise['title'][:60]}"

    try:
        curriculum_md = generate_curriculum(exercise, matching_artifact)
    except Exception as e:
        kb.log_error(PROJECT_ROOT, "expand_lab.py", f"Curriculum gen failed (item {args.item}): {type(e).__name__}", str(e)[:120])
        kb.log_session_event(PROJECT_ROOT, "expand_lab.py", "failed", str(e)[:80])
        raise
    
    # Save the output
    curriculums_dir = PROJECT_ROOT / "curriculums"
    curriculums_dir.mkdir(exist_ok=True)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(exercise['title'])
    filename = f"{today_str}-{slug}.md"
    file_path = curriculums_dir / filename
    
    file_path.write_text(curriculum_md, encoding="utf-8")
    print(f"\n✅ Curriculum generated successfully!")
    print(f"Saved to: {file_path}")

    # Write curriculum path back into hub-output.json so build_hub.py can find it
    # regardless of title changes on future regenerations.
    hub_output_path = PROJECT_ROOT / "data" / "hub-output.json"
    hub_data = json.loads(hub_output_path.read_text(encoding="utf-8"))
    if args.item - 1 < len(hub_data.get("exercises", [])):
        hub_data["exercises"][args.item - 1]["curriculum_path"] = f"curricula/{slug}.html"
        hub_output_path.write_text(json.dumps(hub_data, indent=2), encoding="utf-8")
        print(f"Linked → hub-output.json exercises[{args.item - 1}].curriculum_path")

    _run_status["success"] = True
    kb.log_session_event(
        PROJECT_ROOT, "expand_lab.py", "completed",
        f"item {args.item}: {exercise['title'][:60]}"
    )

if __name__ == "__main__":
    main()
