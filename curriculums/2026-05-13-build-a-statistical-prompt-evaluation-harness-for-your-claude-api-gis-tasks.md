# Build a Statistical Prompt Evaluation Harness for Your Claude API GIS Tasks

## A Rigorous, Evidence-Based Framework for Model Selection in GIS Automation

---

## 1. Introduction & Context

### What This Is

Most developers evaluating LLM prompts make the same mistake: they run a prompt a few times, average the scores, and declare a winner. This is statistically unsound. LLM outputs are **stochastic** — the same prompt can produce wildly different quality scores across runs due to temperature, sampling variance, and model non-determinism. Comparing averages without accounting for this variance is like comparing two coins by flipping each one three times.

This tutorial teaches you to build a **Statistical Prompt Evaluation Harness** — a Python script that:

1. Runs your real FME/GIS automation prompts against `claude-sonnet-4-5` and `claude-haiku-4-5`
2. Collects **20 independent samples** per prompt-model combination
3. Applies the **Mann-Whitney U test** (a non-parametric statistical test that makes no assumptions about score distributions) to determine whether performance differences are *real* or *noise*
4. Generates a publication-ready results table for your Tool Critic audience

### Why It Matters

In GIS automation workflows, model selection has real cost implications. `claude-haiku-4-5` is significantly cheaper than `claude-sonnet-4-5`. If you can't prove Sonnet is *statistically significantly better* on your specific GIS tasks, you're leaving money on the table by defaulting to the more expensive model — or worse, under-serving users by choosing cheapness over quality without evidence.

### What You'll Produce

- A Python script (`gis_eval_harness.py`) you can reuse and extend
- A CSV results file with all 20×2×3 = 120 scored runs
- A formatted Markdown/HTML table suitable for a Tool Critic blog post
- Statistical interpretation guidance for non-technical readers

---

## 2. Prerequisites

### Knowledge

| Topic | Level Required | Resource if Needed |
|---|---|---|
| Python 3.x | Intermediate | [Python.org tutorial](https://docs.python.org/3/tutorial/) |
| Claude API basics | Beginner | [Anthropic quickstart](https://docs.anthropic.com/en/docs/quickstart) |
| FME/GIS concepts | Basic familiarity | Your existing domain knowledge |
| Statistical intuition | None required | This tutorial explains everything |

### Environment

```bash
# Python 3.9+ required
python --version

# Required packages
pip install anthropic scipy pandas numpy rich python-dotenv
```

### API Access

```bash
# Create a .env file in your project directory
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

You'll need an Anthropic API key with access to both:
- `claude-sonnet-4-5` (or the latest Sonnet variant available to you)
- `claude-haiku-4-5` (or the latest Haiku variant available to you)

> **Cost estimate:** This harness makes ~120 API calls (20 runs × 2 models × 3 prompts). At typical Haiku/Sonnet pricing for short GIS prompts, expect $0.50–$3.00 total. Run once, get lasting insights.

### Your Three GIS Prompts

Before starting, identify the **three FME/GIS automation prompts** you use most often. Examples:
- Coordinate transformation instruction generation
- FME workspace documentation requests
- Spatial query optimization suggestions
- CRS mismatch diagnosis prompts

We'll use placeholder prompts in this tutorial that you'll replace with your real ones.

---

## 3. Step-by-Step Guide

### Step 1: Project Structure Setup

Create your project directory:

```bash
mkdir gis-eval-harness
cd gis-eval-harness
touch gis_eval_harness.py
touch prompts_config.py
touch scorer.py
touch results_publisher.py
touch .env
```

Your final structure will look like:

```
gis-eval-harness/
├── .env                    # API keys (never commit this)
├── gis_eval_harness.py     # Main orchestration script
├── prompts_config.py       # Your three GIS prompts
├── scorer.py               # Response quality scoring logic
├── results_publisher.py    # Table generation and statistics
├── results/
│   ├── raw_scores.csv      # All 120 runs
│   └── summary_table.md    # Blog-ready output
└── README.md
```

```bash
mkdir results
```

---

### Step 2: Define Your Three GIS Prompts

Edit `prompts_config.py`. Replace the example prompts with your actual top-three FME/GIS automation prompts:

```python
# prompts_config.py
"""
Your three FME/GIS automation prompts under evaluation.

HOW TO CHOOSE YOUR THREE PROMPTS:
- Pick prompts you use repeatedly in production
- Choose prompts where output quality genuinely varies
- Include at least one "hard" prompt (complex reasoning)
  and one "easy" prompt (straightforward extraction)
"""

PROMPTS = {
    "prompt_1_crs_diagnosis": {
        "name": "CRS Mismatch Diagnosis",
        "description": "Diagnose coordinate reference system conflicts between datasets",
        "system": (
            "You are an expert GIS analyst specializing in FME (Feature Manipulation Engine) "
            "workflows. You provide precise, actionable technical guidance. When diagnosing "
            "spatial data issues, always specify: (1) the root cause, (2) the affected "
            "transformers, and (3) step-by-step remediation."
        ),
        "user": (
            "I have two datasets I'm trying to join in FME:\n"
            "- Dataset A: Municipal boundaries from city GIS portal (unknown CRS, "
            "coordinates look like 6-digit numbers e.g. 485234.5, 5456789.2)\n"
            "- Dataset B: Census polygons in WGS84 (EPSG:4326)\n\n"
            "The SpatialRelator transformer returns zero matches even though visually "
            "the features should overlap. What is the most likely cause and how do I "
            "fix it in FME Workbench?"
        ),
        # What a high-quality response must include (used by scorer.py)
        "quality_criteria": [
            "identifies projected vs geographic CRS conflict",
            "mentions EPSG codes or CRS detection approach",
            "names specific FME transformer (CoordinateSystemSetter or Reprojector)",
            "provides step-by-step workflow",
            "addresses the SpatialRelator configuration"
        ]
    },

    "prompt_2_workspace_docs": {
        "name": "FME Workspace Documentation",
        "description": "Generate documentation for a described FME workspace",
        "system": (
            "You are a technical writer specializing in FME documentation. "
            "Generate clear, structured documentation that a new GIS analyst could "
            "follow. Include purpose, data flow, transformer descriptions, and "
            "any data quality considerations."
        ),
        "user": (
            "Document the following FME workspace pipeline:\n\n"
            "Input: PostgreSQL/PostGIS table 'parcels' (geometry: MultiPolygon, "
            "attributes: parcel_id, owner_name, assessed_value, zoning_code)\n\n"
            "Transformers in order:\n"
            "1. Tester: Filter where zoning_code IN ('R1','R2','R3')\n"
            "2. AreaCalculator: Calculate polygon area in square meters\n"
            "3. AttributeCreator: Create 'value_per_sqm' = assessed_value / area\n"
            "4. StatisticsCalculator: Group by zoning_code, calculate mean/median "
            "of value_per_sqm\n"
            "5. JSONFormatter: Output as GeoJSON\n\n"
            "Output: File geodatabase + summary JSON\n\n"
            "Generate complete workspace documentation."
        ),
        "quality_criteria": [
            "includes workspace purpose/overview section",
            "documents each transformer with input/output description",
            "mentions potential data quality issues (null values, division by zero)",
            "describes output format and schema",
            "includes usage notes or prerequisites"
        ]
    },

    "prompt_3_spatial_query": {
        "name": "PostGIS Query Optimization",
        "description": "Optimize a slow spatial query in PostGIS",
        "system": (
            "You are a PostGIS and PostgreSQL performance expert. Analyze spatial "
            "queries for performance issues and provide optimized rewrites with "
            "explanations. Always consider: spatial indexes, geometry simplification, "
            "bounding box pre-filtering, and query plan implications."
        ),
        "user": (
            "This PostGIS query takes 45 seconds on a table with 2.3 million parcels:\n\n"
            "```sql\n"
            "SELECT p.parcel_id, p.owner_name, f.flood_zone_code\n"
            "FROM parcels p\n"
            "CROSS JOIN flood_zones f\n"
            "WHERE ST_Within(p.geometry, f.geometry)\n"
            "  AND f.flood_zone_code IN ('AE', 'VE', 'AO')\n"
            "ORDER BY p.parcel_id;\n"
            "```\n\n"
            "Table sizes: parcels (2.3M rows), flood_zones (45,000 rows)\n"
            "Indexes: parcels has GiST index on geometry, flood_zones has no spatial index\n\n"
            "Identify all performance problems and provide an optimized version."
        ),
        "quality_criteria": [
            "identifies CROSS JOIN as catastrophic (N×M problem)",
            "recommends ST_Intersects over ST_Within for index use OR explains difference",
            "recommends GiST index on flood_zones.geometry",
            "suggests filtering flood_zones before spatial join",
            "provides rewritten query, not just advice"
        ]
    }
}

# Experiment configuration
EXPERIMENT_CONFIG = {
    "models": [
        "claude-sonnet-4-5",
        "claude-haiku-4-5"
    ],
    "runs_per_combination": 20,  # Statistical power requires ≥20 samples
    "max_tokens": 1500,
    "temperature": 1.0,  # Use default temperature to capture natural variance
}
```

> **Customization note:** The `quality_criteria` lists are what your scorer will check for. Make them specific and measurable — not "good explanation" but "names the specific transformer causing the issue."

---

### Step 3: Build the Response Scorer

The scorer is the most important component. It converts a free-text LLM response into a numerical score (0–100) based on your criteria. Edit `scorer.py`:

```python
# scorer.py
"""
Scores LLM responses against quality criteria.

SCORING PHILOSOPHY:
We use keyword/phrase matching as a proxy for quality. This is imperfect but
reproducible and consistent — which is what statistical testing requires.
For production use, consider replacing this with an LLM-as-judge approach
(using a separate Claude call to score responses).
"""

import re
from typing import List, Dict, Tuple
import anthropic


def score_response_keyword(response_text: str, criteria: List[str]) -> Tuple[float, Dict]:
    """
    Score a response using keyword matching against quality criteria.
    
    Returns:
        - score: float 0-100
        - breakdown: dict showing which criteria were met
    """
    score_per_criterion = 100.0 / len(criteria)
    breakdown = {}
    total_score = 0.0
    
    response_lower = response_text.lower()
    
    for criterion in criteria:
        # Extract key terms from the criterion description
        key_terms = _extract_key_terms(criterion)
        
        # Check if the response addresses this criterion
        criterion_met = _check_criterion(response_lower, key_terms)
        
        breakdown[criterion] = {
            "met": criterion_met,
            "key_terms_checked": key_terms,
            "points": score_per_criterion if criterion_met else 0
        }
        
        if criterion_met:
            total_score += score_per_criterion
    
    return round(total_score, 2), breakdown


def score_response_llm_judge(
    client: anthropic.Anthropic,
    response_text: str,
    original_prompt: str,
    criteria: List[str],
    judge_model: str = "claude-haiku-4-5"  # Use cheap model as judge
) -> Tuple[float, Dict]:
    """
    Score a response using an LLM as judge.
    More accurate than keyword matching but costs additional API calls.
    
    Use this for your final publication results for higher validity.
    """
    criteria_formatted = "\n".join([f"{i+1}. {c}" for i, c in enumerate(criteria)])
    
    judge_prompt = f"""You are evaluating an AI assistant's response to a GIS/FME technical question.

ORIGINAL QUESTION:
{original_prompt}

AI RESPONSE TO EVALUATE:
{response_text}

EVALUATION CRITERIA (each worth equal points, total = 100):
{criteria_formatted}

For each criterion, output ONLY a JSON object with this exact structure:
{{
  "scores": [
    {{"criterion": "criterion text", "met": true/false, "reasoning": "one sentence"}}
  ],
  "total_score": <number 0-100>
}}

Be strict: "met" = true only if the response clearly and specifically addresses the criterion."""

    try:
        message = client.messages.create(
            model=judge_model,
            max_tokens=500,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        
        import json
        response_content = message.content[0].text
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            breakdown = {item["criterion"]: {"met": item["met"], "reasoning": item["reasoning"]} 
                        for item in result["scores"]}
            return float(result["total_score"]), breakdown
    except Exception as e:
        print(f"  [Judge fallback] LLM judge failed ({e}), using keyword scoring")
    
    # Fallback to keyword scoring
    return score_response_keyword(response_text, criteria)


def _extract_key_terms(criterion: str) -> List[str]:
    """Extract searchable terms from a criterion description."""
    # Remove common words and extract technical terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                  'for', 'of', 'with', 'by', 'from', 'is', 'are', 'that', 'this',
                  'includes', 'mentions', 'provides', 'identifies', 'describes',
                  'recommends', 'suggests', 'names', 'specific', 'step', 'steps'}
    
    words = re.findall(r'\b[a-z_]+\b', criterion.lower())
    key_terms = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Also keep multi-word technical phrases
    technical_phrases = re.findall(r'[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*', criterion)
    
    return key_terms + [p.lower() for p in technical_phrases]


def _check_criterion(response_lower: str, key_terms: List[str]) -> bool:
    """
    Check if a response addresses a criterion based on key terms.
    Requires at least 60% of key terms to be present.
    """
    if not key_terms:
        return False
    
    matches = sum(1 for term in key_terms if term in response_lower)
    match_ratio = matches / len(key_terms)
    
    return match_ratio >= 0.6


def validate_scorer(sample_responses: List[str], criteria: List[str]) -> None:
    """
    Quick sanity check: print scores for a few sample responses.
    Call this during development to verify your scorer is working as expected.
    """
    print("\n=== SCORER VALIDATION ===")
    for i, response in enumerate(sample_responses):
        score, breakdown = score_response_keyword(response, criteria)
        print(f"\nSample {i+1} Score: {score:.1f}/100")
        for criterion, result in breakdown.items():
            status = "✓" if result["met"] else "✗"
            print(f"  {status} {criterion[:60]}...")
```

---

### Step 4: Build the Main Evaluation Harness

This is the core orchestration script. Edit `gis_eval_harness.py`:

```python
# gis_eval_harness.py
"""
Statistical Prompt Evaluation Harness for GIS/FME Claude API Tasks

Runs N trials per (prompt × model) combination and stores all scores
for statistical analysis.

Usage:
    python gis_eval_harness.py                    # Full run (120 API calls)
    python gis_eval_harness.py --dry-run          # Test with 2 runs per combo
    python gis_eval_harness.py --scoring llm      # Use LLM judge (more accurate)
    python gis_eval_harness.py --prompt-id prompt_1_crs_diagnosis  # Single prompt
"""

import os
import sys
import time
import json
import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich import print as rprint

from prompts_config import PROMPTS, EXPERIMENT_CONFIG
from scorer import score_response_keyword, score_response_llm_judge

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

load_dotenv()
console = Console()

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


@dataclass
class TrialResult:
    """Single trial result for one (prompt × model × run) combination."""
    prompt_id: str
    prompt_name: str
    model: str
    run_number: int
    score: float
    response_length: int
    latency_seconds: float
    criteria_breakdown: str  # JSON string
    timestamp: str
    error: Optional[str] = None


# ─────────────────────────────────────────────
# Core Evaluation Functions
# ─────────────────────────────────────────────

def run_single_trial(
    client: anthropic.Anthropic,
    prompt_id: str,
    prompt_config: Dict,
    model: str,
    run_number: int,
    scoring_method: str = "keyword"
) -> TrialResult:
    """
    Execute a single trial: call API, get response, score it.
    
    Args:
        client: Anthropic client
        prompt_id: Key from PROMPTS dict
        prompt_config: The prompt configuration dict
        model: Model identifier string
        run_number: Which run this is (1-N)
        scoring_method: "keyword" or "llm"
    
    Returns:
        TrialResult with score and metadata
    """
    start_time = time.time()
    
    try:
        # Make the API call
        message = client.messages.create(
            model=model,
            max_tokens=EXPERIMENT_CONFIG["max_tokens"],
            temperature=EXPERIMENT_CONFIG.get("temperature", 1.0),
            system=prompt_config["system"],
            messages=[
                {"role": "user", "content": prompt_config["user"]}
            ]
        )
        
        latency = time.time() - start_time
        response_text = message.content[0].text
        
        # Score the response
        if scoring_method == "llm":
            score, breakdown = score_response_llm_judge(
                client=client,
                response_text=response_text,
                original_prompt=prompt_config["user"],
                criteria=prompt_config["quality_criteria"]
            )
        else:
            score, breakdown = score_response_keyword(
                response_text=response_text,
                criteria=prompt_config["quality_criteria"]
            )
        
        return TrialResult(
            prompt_id=prompt_id,
            prompt_name=prompt_config["name"],
            model=model,
            run_number=run_number,
            score=score,
            response_length=len(response_text),
            latency_seconds=round(latency, 3),
            criteria_breakdown=json.dumps(breakdown),
            timestamp=datetime.now().isoformat(),
            error=None
        )
        
    except anthropic.RateLimitError:
        console.print(f"  [yellow]Rate limit hit, waiting 30s...[/yellow]")
        time.sleep(30)
        return run_single_trial(client, prompt_id, prompt_config, model, run_number, scoring_method)
        
    except Exception as e:
        latency = time.time() - start_time
        return TrialResult(
            prompt_id=prompt_id,
            prompt_name=prompt_config["name"],
            model=model,
            run_number=run_number,
            score=0.0,
            response_length=0,
            latency_seconds=round(latency, 3),
            criteria_breakdown="{}",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )


def run_all_trials(
    client: anthropic.Anthropic,
    prompt_ids: Optional[List[str]] = None,
    n_runs: Optional[int] = None,
    scoring_method: str = "keyword",
    delay_between_calls: float = 0.5
) -> List[TrialResult]:
    """
    Run the complete evaluation matrix.
    
    Total calls = len(prompts) × len(models) × n_runs
    
    Args:
        client: Anthropic client
        prompt_ids: Which prompts to evaluate (None = all)
        n_runs: Override for runs per combination
        scoring_method: "keyword" or "llm"
        delay_between_calls: Seconds to wait between API calls (rate limiting)
    
    Returns:
        List of all TrialResults
    """
    prompts_to_run = {k: v for k, v in PROMPTS.items() 
                      if prompt_ids is None or k in prompt_ids}
    models = EXPERIMENT_CONFIG["models"]
    runs = n_runs or EXPERIMENT_CONFIG["runs_per_combination"]
    
    total_calls = len(prompts_to_run) * len(models) * runs
    
    console.print(f"\n[bold cyan]═══ GIS Prompt Evaluation Harness ═══[/bold cyan]")
    console.print(f"Prompts:  {len(prompts_to_run)} ({', '.join(prompts_to_run.keys())})")
    console.print(f"Models:   {len(models)} ({', '.join(models)})")
    console.print(f"Runs:     {runs} per combination")
    console.print(f"Total:    [bold]{total_calls} API calls[/bold]")
    console.print(f"Scoring:  {scoring_method}")
    console.print(f"Delay:    {delay_between_calls}s between calls\n")
    
    all_results: List[TrialResult] = []
    call_count = 0
    
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        for prompt_id, prompt_config in prompts_to_run.items():
            prompt_task = progress.add_task(
                f"[cyan]{prompt_config['name']}[/cyan]", 
                total=len(models) * runs
            )
            
            for model in models:
                for run_num in range(1, runs + 1):
                    progress.update(
                        prompt_task, 
                        description=f"[cyan]{prompt_config['name']}[/cyan] | "
                                   f"[yellow]{model.split('-')[1]}[/yellow] | "
                                   f"run {run_num}/{runs}"
                    )
                    
                    result = run_single_trial(
                        client=client,
                        prompt_id=prompt_id,
                        prompt_config=prompt_config,
                        model=model,
                        run_number=run_num,
                        scoring_method=scoring_method
                    )
                    
                    all_results.append(result)
                    call_count += 1
                    
                    # Show individual result
                    status = "[red]ERR[/red]" if result.error else f"[green]{result.score:.0f}[/green]"
                    progress.print(
                        f"  {'✓' if not result.error else '✗'} "
                        f"{prompt_id[:20]:<22} | "
                        f"{model.split('-')[1]:>6} | "
                        f"run {run_num:>2} | "
                        f"score={status} | "
                        f"{result.latency_seconds:.1f}s"
                    )
                    
                    progress.update(prompt_task, advance=1)
                    
                    if call_count < total_calls:
                        time.sleep(delay_between_calls)
    
    return all_results


# ─────────────────────────────────────────────
# Data Persistence
# ─────────────────────────────────────────────

def save_results_csv(results: List[TrialResult], filepath: Path) -> None:
    """Save all trial results to CSV for reproducibility."""
    if not results:
        return
    
    fieldnames = list(asdict(results[0]).keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([asdict(r) for r in results])
    
    console.print(f"\n[green]✓[/green] Raw results saved to: [bold]{filepath}[/bold]")


def load_results_csv(filepath: Path) -> List[TrialResult]:
    """Load previously saved results (for re-running analysis without new API calls)."""
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(TrialResult(
                prompt_id=row['prompt_id'],
                prompt_name=row['prompt_name'],
                model=row['model'],
                run_number=int(row['run_number']),
                score=float(row['score']),
                response_length=int(row['response_length']),
                latency_seconds=float(row['latency_seconds']),
                criteria_breakdown=row['criteria_breakdown'],
                timestamp=row['timestamp'],
                error=row['error'] if row['error'] else None
            ))
    return results


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="GIS Prompt Statistical Evaluation Harness")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Run only 2 trials per combination (cost-saving test)")
    parser.add_argument("--scoring", choices=["keyword", "llm"], default="keyword",
                        help="Scoring method: keyword matching or LLM judge")
    parser.add_argument("--prompt-id", type=str, default=None,
                        help="Run only one specific prompt ID")
    parser.add_argument("--load-csv", type=str, default=None,
                        help="Load existing CSV instead of making new API calls")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Seconds between API calls (default: 0.5)")
    args = parser.parse_args()
    
    # Initialize client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not found in environment[/red]")
        sys.exit(1)
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Determine output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = RESULTS_DIR / f"raw_scores_{timestamp}.csv"
    
    # Load or collect results
    if args.load_csv:
        console.print(f"\n[cyan]Loading existing results from {args.load_csv}[/cyan]")
        results = load_results_csv(Path(args.load_csv))
    else:
        n_runs = 2 if args.dry_run else None
        prompt_ids = [args.prompt_id] if args.prompt_id else None
        
        if args.dry_run:
            console.print("\n[yellow]DRY RUN MODE: 2 runs per combination[/yellow]")
        
        results = run_all_trials(
            client=client,
            prompt_ids=prompt_ids,
            n_runs=n_runs,
            scoring_method=args.scoring,
            delay_between_calls=args.delay
        )
        
        save_results_csv(results, csv_path)
    
    # Import here to avoid circular imports in development
    from results_publisher import analyze_and_publish
    analyze_and_publish(results, RESULTS_DIR, timestamp)
    
    console.print("\n[bold green]✓ Evaluation complete![/bold green]")
    console.print(f"  Results: {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
```

---

### Step 5: Build the Statistical Analysis & Publisher

This is where the Mann-Whitney U test happens. Edit `results_publisher.py`:

```python
# results_publisher.py
"""
Statistical analysis and publication-ready table generator.

THE MANN-WHITNEY U TEST — WHY IT'S RIGHT HERE:
================================================
We cannot assume LLM quality scores are normally distributed. They're often:
- Bimodal (either the model gets it or it doesn't)  
- Bounded (0-100 ceiling/floor effects)
- Skewed (most responses score well, outliers pull the tail)

The Mann-Whitney U test is non-parametric — it ranks ALL scores from both
groups together and tests whether one group's ranks are systematically higher.
It requires no distribution assumptions and is robust to outliers.

Null hypothesis (H₀): The two models' score distributions are identical.
If p < 0.05, we reject H₀ → the difference is statistically significant.
Effect size (r): |z| / √N, where r > 0.3 = medium, r > 0.5 = large effect.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats
from rich.console import Console
from rich.table import Table

from gis_eval_harness import TrialResult
from prompts_config import EXPERIMENT_CONFIG

console = Console()

SIGNIFICANCE_THRESHOLD = 0.05


# ─────────────────────────────────────────────
# Statistical Analysis
# ─────────────────────────────────────────────

def extract_scores_by_group(results: List[TrialResult]) -> Dict[str, Dict[str,