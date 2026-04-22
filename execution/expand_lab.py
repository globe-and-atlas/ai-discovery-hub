#!/usr/bin/env python3
"""
expand_lab.py — Curriculum Generator for AI Discovery Hub
Takes a short exercise from the latest Lab (hub-output.json) and uses an LLM
to generate a comprehensive, step-by-step markdown tutorial.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import anthropic

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def get_client():
    provider = os.getenv("HUB_PROVIDER", "anthropic")
    if provider == "anthropic":
        return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return genai.GenerativeModel(os.getenv("HUB_MODEL", "gemini-1.5-pro"))
    raise ValueError(f"Provider {provider} not implemented yet.")

def generate_curriculum(exercise: dict, artifact: dict) -> str:
    provider = os.getenv("HUB_PROVIDER", "anthropic")
    model_name = os.getenv("HUB_MODEL", "claude-3-5-sonnet-latest")
    
    prompt = f"""You are an expert AI curriculum designer. Your goal is to create a comprehensive, step-by-step learning tutorial and practical exercise based on the following context.

EXERCISE GOAL:
Title: {exercise['title']}
Effort: {exercise['effort']}
Description: {exercise['desc']}

SOURCE ARTIFACT CONTEXT:
Title: {artifact.get('title', '')}
Type: {artifact.get('type', '')}
Source: {artifact.get('source', '')}
URL: {artifact.get('url', '')}
Description: {artifact.get('desc', '')}
Why it matters: {artifact.get('relevance_why', '')}

INSTRUCTIONS:
Create a complete, hands-on learning curriculum. The curriculum MUST include:
1. Introduction & Context: What this is and why it's worth learning.
2. Prerequisites: What the learner needs before starting.
3. Step-by-Step Guide: Detailed, practical instructions to achieve the exercise goal. Include code snippets, CLI commands, or UI steps as appropriate.
4. Validation: How the learner can verify they completed the exercise successfully.
5. Next Steps: Where to go from here.

Output ONLY valid Markdown. Use formatting, headers, and code blocks appropriately."""

    print(f"Calling {provider} ({model_name}) to generate curriculum...")
    
    if provider == "anthropic":
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model_name,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
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
    
    curriculum_md = generate_curriculum(exercise, matching_artifact)
    
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

if __name__ == "__main__":
    main()
