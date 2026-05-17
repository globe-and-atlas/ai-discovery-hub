# Build a Statistical Prompt Evaluation Harness for Your Claude API GIS Tasks

## Introduction & Context

You've probably done this: run two Claude prompts on your FME automation task, eyeballed the outputs, picked the one that *seemed* better, and shipped it. Maybe you even computed average scores — Sonnet averaged 7.4, Haiku averaged 6.8, done.

The problem? With 10–30 test runs, that 0.6-point difference is almost certainly statistical noise. You're making model-selection decisions — with real cost implications, since Sonnet is substantially more expensive than Haiku — based on random variation.

This tutorial implements the methodology from [*Why Comparing Average Scores is the Wrong Way to Evaluate LLM Prompts*](https://dev.to/aayush_kumarsingh_6ee1ffe/why-comparing-average-scores-is-the-wrong-way-to-evaluate-llm-prompts-and-what-to-do-instead-1li) and applies it to your actual GIS automation workflow. You'll:

1. Define three realistic FME/GIS automation prompts you already use
2. Run each against `claude-sonnet-4-5` and `claude-haiku-4-5` across 20 runs each
3. Score outputs programmatically
4. Apply Mann-Whitney U (non-parametric, no normality assumption), Cohen's d (effect size), and bootstrap confidence intervals
5. Generate a publication-ready results table for your Tool Critic post

**Why this approach over a simple average?** GIS automation scores are bimodal. Either Claude correctly identifies the right FME transformer and writes valid Python — score 9 — or it hallucinates a transformer that doesn't exist — score 2. That distribution violates the normality assumption that a t-test requires. Mann-Whitney U ranks pairs and makes no distribution assumptions, giving you a valid p-value even on this spiky data.

---

## Prerequisites

### Accounts & API Access

- Anthropic API key with access to both `claude-sonnet-4-5` and `claude-haiku-4-5`
- Python 3.10+ installed

### Python Dependencies

This harness uses **only the standard library** for statistics (matching the source methodology exactly) plus `anthropic` for API calls:

```bash
pip install anthropic
```

No `scipy`, no `numpy`, no `pandas` required. The statistical functions are pure Python, validated against `scipy` to 3 decimal places as described in the source.

### Environment Setup

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or create a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### Directory Structure

```
gis-eval-harness/
├── harness.py          # Main evaluation script (you'll build this)
├── prompts.py          # Your three GIS prompt definitions
├── scorer.py           # Output scoring logic
├── stats.py            # Statistical functions from source
└── results/            # Auto-created output directory
```

---

## Step-by-Step Guide

### Step 1: Define Your Three GIS Prompts

Create `prompts.py`. These are three real prompt patterns drawn from common FME/GIS automation work. Customize the specifics to match your actual use cases:

```python
# prompts.py
"""
Three FME/GIS automation prompts for statistical evaluation.
These represent patterns you use regularly — edit to match your real workload.
"""

PROMPTS = {
    "coordinate_transform": {
        "name": "Coordinate System Transformation Workflow",
        "system": (
            "You are an expert FME (Feature Manipulation Engine) developer. "
            "Provide precise, production-ready FME workspace configurations "
            "and Python scripting solutions for spatial data transformation tasks. "
            "Always specify exact transformer names as they appear in FME Workbench."
        ),
        "user": (
            "I need to batch-transform 847 shapefiles from NAD83 (EPSG:4269) to "
            "Web Mercator (EPSG:3857) while preserving all attribute data and "
            "generating a per-file transformation log. "
            "Provide: (1) the FME transformers I need in order, "
            "(2) the Python scripting approach using fmeobjects to iterate the file list, "
            "and (3) the log format specification. "
            "Be specific about transformer parameter names."
        ),
        "scoring_keywords": [
            "CoordinateSystemSetter", "Reprojector", "fmeobjects",
            "FMEFeature", "EPSG:3857", "NAD83", "shapefile",
            "FMELogFile", "openLogFile", "workspace"
        ],
        "max_score": 10,
    },

    "spatial_join_automation": {
        "name": "Automated Spatial Join with Attribute Aggregation",
        "system": (
            "You are an expert FME developer and Python GIS programmer. "
            "When asked about FME workflows, specify exact transformer names. "
            "When providing Python code, use industry-standard libraries "
            "like fmeobjects, geopandas, or arcpy as appropriate. "
            "Include error handling in all code examples."
        ),
        "user": (
            "Write an FME workspace workflow plus a standalone Python validation script "
            "that: joins parcel polygons to census block groups using a spatial "
            "containment test, aggregates median household income from the block group "
            "to each parcel, flags parcels that span multiple block groups, "
            "and writes output as GeoPackage. "
            "I need the exact FME transformer sequence AND equivalent Python using geopandas."
        ),
        "scoring_keywords": [
            "NeighborFinder", "SpatialFilter", "StatisticsCalculator",
            "FeatureMerger", "GeoPackage", "gpkg", "geopandas",
            "sjoin", "dissolve", "aggregate", "containment",
            "AttributeCreator", "GeometryFilter"
        ],
        "max_score": 10,
    },

    "raster_pipeline": {
        "name": "Multi-band Raster Processing Pipeline",
        "system": (
            "You are a senior GIS automation engineer specializing in raster "
            "processing pipelines. You write production Python code using GDAL, "
            "rasterio, and FME. All code must include proper error handling, "
            "logging, and be suitable for deployment in a scheduled batch environment."
        ),
        "user": (
            "Design a Python script using rasterio that: "
            "reads a directory of multi-band GeoTIFF files (Landsat-8 format, bands 1-7), "
            "calculates NDVI (Band 4 and Band 5) for each scene, "
            "masks clouds using the QA_PIXEL band, "
            "writes clipped NDVI outputs to a dated output folder, "
            "and logs per-scene statistics (min, max, mean NDVI, cloud cover percent). "
            "Include the complete runnable script."
        ),
        "scoring_keywords": [
            "rasterio", "open", "read", "ndvi", "NDVI",
            "QA_PIXEL", "cloud", "mask", "band", "numpy",
            "logging", "os.path", "datetime", "statistics",
            "write", "meta", "transform", "nodata"
        ],
        "max_score": 10,
    },
}
```

---

### Step 2: Build the Statistical Functions

Create `stats.py` using the exact implementations from the source article. No external dependencies:

```python
# stats.py
"""
Statistical functions for LLM prompt evaluation.
Pure Python implementation — no scipy, no numpy.
Source: https://dev.to/aayush_kumarsingh_6ee1ffe/why-comparing-average-scores-is-the-wrong-way-to-evaluate-llm-prompts-and-what-to-do-instead-1li
Validated against scipy to 3 decimal places per source author.
"""

import math
import random
import statistics


# ── Mann-Whitney U ─────────────────────────────────────────────────────────────

def mann_whitney_u(scores_a: list[float], scores_b: list[float]) -> float:
    """
    Returns p-value for the null hypothesis that A and B are drawn
    from the same distribution.

    p < 0.05  → the difference is statistically significant
    p >= 0.05 → insufficient evidence to conclude a real difference

    Non-parametric: makes NO assumption about score distribution.
    Correct choice for bimodal LLM score distributions.
    """
    n1, n2 = len(scores_a), len(scores_b)
    if n1 == 0 or n2 == 0:
        return 1.0

    # Count how often A beats B (ties count as 0.5)
    u1 = sum(
        1 if x > y else 0.5 if x == y else 0
        for x in scores_a
        for y in scores_b
    )

    # Normal approximation
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)

    if sigma == 0:
        return 1.0

    z = (u1 - mu) / sigma
    p_value = 2 * (1 - _normal_cdf(abs(z)))

    return round(max(0.001, min(1.0, p_value)), 4)


def _normal_cdf(x: float) -> float:
    """Standard normal CDF using math.erf."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ── Cohen's d ─────────────────────────────────────────────────────────────────

def cohens_d(scores_a: list[float], scores_b: list[float]) -> float:
    """
    Effect size: how large is the difference in practical terms?

    Interpretation (standard thresholds):
        d < 0.2  → negligible  (not worth acting on)
        d < 0.5  → small
        d < 0.8  → medium
        d >= 0.8 → large

    Requires BOTH p < 0.05 AND d >= 0.5 before concluding
    one model/prompt is meaningfully better.
    """
    if len(scores_a) < 2 or len(scores_b) < 2:
        return 0.0

    mean_a = statistics.mean(scores_a)
    mean_b = statistics.mean(scores_b)
    var_a = statistics.variance(scores_a)
    var_b = statistics.variance(scores_b)

    pooled = math.sqrt((var_a + var_b) / 2)

    return round(abs(mean_b - mean_a) / pooled, 3) if pooled > 0 else 0.0


# ── Bootstrap Confidence Intervals ────────────────────────────────────────────

def bootstrap_ci(
    values: list[float],
    n_samples: int = 2000,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """
    95% confidence interval for the mean using the percentile bootstrap method.

    Makes no distribution assumptions.
    Deterministic: seeded with 42 — same input always gives same output.

    Interpretation: "We are 95% confident the true mean lies in this range."
    Narrow interval = reliable estimate. Wide interval = high uncertainty.
    """
    if len(values) < 2:
        m = statistics.mean(values) if values else 0.0
        return (m, m)

    rng = random.Random(42)  # deterministic — matches source exactly
    boot_means = []

    for _ in range(n_samples):
        sample = [rng.choice(values) for _ in range(len(values))]
        boot_means.append(statistics.mean(sample))

    boot_means.sort()
    alpha = 1 - confidence
    lower_idx = int(alpha / 2 * n_samples)
    upper_idx = int((1 - alpha / 2) * n_samples)

    return (
        round(boot_means[lower_idx], 4),
        round(boot_means[upper_idx], 4),
    )


# ── Decision Logic ─────────────────────────────────────────────────────────────

def interpret_results(
    p_value: float,
    d: float,
    mean_sonnet: float,
    mean_haiku: float,
) -> str:
    """
    Apply the source's two-condition decision framework:
      - p < 0.05 AND d >= 0.5 → meaningful, significant difference
      - p < 0.05 AND d < 0.5  → statistically real but practically negligible
      - p >= 0.05             → no reliable difference detected
    """
    sig = p_value < 0.05
    meaningful = d >= 0.5
    sonnet_better = mean_sonnet > mean_haiku

    if sig and meaningful:
        winner = "SONNET" if sonnet_better else "HAIKU"
        return f"✅ SIGNIFICANT & MEANINGFUL — use {winner}"
    elif sig and not meaningful:
        return "⚠️  SIGNIFICANT but negligible effect — flip a coin, prefer cost"
    else:
        return "❌ NO RELIABLE DIFFERENCE — default to Haiku (cheaper)"
```

---

### Step 3: Build the Scorer

Create `scorer.py`. The source article doesn't specify a scoring rubric for GIS tasks, so this is an explicit addition — keyword coverage plus length-as-proxy-for-completeness:

> **Note:** The source material defines the *statistical* methodology but not a domain-specific scoring function. The scorer below is purpose-built for GIS automation outputs. Adjust the keyword weights and rubric to match your own quality criteria.

```python
# scorer.py
"""
Scores Claude API responses for GIS/FME automation quality.

Scoring rubric (0–10):
  - Keyword coverage:   up to 6 points  (critical technical terms present)
  - Code presence:      up to 2 points  (actual code blocks included)
  - Length/completeness:up to 2 points  (response substantive, not a refusal)

This is intentionally simple and transparent so scores are reproducible.
Replace with LLM-as-judge or human rating if you need higher fidelity.
"""

import re


def score_response(response_text: str, prompt_config: dict) -> float:
    """
    Score a single Claude response against the prompt's expected keywords.

    Returns a float in [0, 10].
    """
    if not response_text or len(response_text) < 50:
        return 0.0

    text_lower = response_text.lower()
    keywords = prompt_config["scoring_keywords"]
    max_score = prompt_config["max_score"]

    # ── Keyword coverage (0–6 points) ─────────────────────────────────────────
    keywords_found = sum(
        1 for kw in keywords
        if kw.lower() in text_lower
    )
    keyword_score = min(6.0, (keywords_found / len(keywords)) * 6.0)

    # ── Code block presence (0–2 points) ──────────────────────────────────────
    code_blocks = len(re.findall(r"```[\s\S]*?```", response_text))
    code_score = min(2.0, code_blocks * 1.0)

    # ── Completeness proxy (0–2 points) ───────────────────────────────────────
    # 200 chars = bare minimum, 800+ = substantive response
    length = len(response_text)
    if length >= 800:
        completeness_score = 2.0
    elif length >= 400:
        completeness_score = 1.0
    else:
        completeness_score = 0.5

    raw = keyword_score + code_score + completeness_score
    return round(min(max_score, raw), 2)


def score_batch(responses: list[str], prompt_config: dict) -> list[float]:
    """Score a list of responses for a single prompt."""
    return [score_response(r, prompt_config) for r in responses]
```

---

### Step 4: Build the Main Evaluation Harness

Create `harness.py` — this is the core script:

```python
# harness.py
"""
Statistical Prompt Evaluation Harness for Claude API GIS Tasks
=============================================================
Runs 3 GIS prompts × 2 models × 20 runs each = 120 API calls total.
Applies Mann-Whitney U, Cohen's d, and bootstrap CIs per the methodology at:
https://dev.to/aayush_kumarsingh_6ee1ffe/why-comparing-average-scores-is-the-wrong-way-to-evaluate-llm-prompts-and-what-to-do-instead-1li
"""

import json
import os
import statistics
import time
from datetime import datetime
from pathlib import Path

import anthropic

from prompts import PROMPTS
from scorer import score_batch
from stats import bootstrap_ci, cohens_d, interpret_results, mann_whitney_u

# ── Configuration ──────────────────────────────────────────────────────────────

MODELS = {
    "sonnet": "claude-sonnet-4-5",
    "haiku":  "claude-haiku-4-5",
}

N_RUNS = 20          # runs per model per prompt
MAX_TOKENS = 1024    # cap to control cost; raise for richer outputs
TEMPERATURE = 1.0    # default; set lower for more deterministic scoring

# ── API Client ─────────────────────────────────────────────────────────────────

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ── Core: Single API Call ──────────────────────────────────────────────────────

def call_claude(
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> str:
    """
    Make a single Claude API call. Returns the response text.
    Returns empty string on error (scored as 0).
    """
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"    ⚠️  API error ({model}): {e}")
        return ""


# ── Core: Run N Evaluations for One Model+Prompt ──────────────────────────────

def run_evaluations(
    model_name: str,
    model_id: str,
    prompt_key: str,
    prompt_config: dict,
    n_runs: int = N_RUNS,
) -> dict:
    """
    Run `n_runs` API calls, score each, return scores + raw responses.
    Includes a 0.5s delay between calls to be a polite API citizen.
    """
    print(f"  Running {n_runs} evals: {model_name} / {prompt_config['name']}")
    responses = []
    scores = []

    for i in range(n_runs):
        print(f"    Run {i+1:02d}/{n_runs}", end="\r")
        response = call_claude(
            model=model_id,
            system_prompt=prompt_config["system"],
            user_prompt=prompt_config["user"],
        )
        score = score_batch([response], prompt_config)[0]
        responses.append(response)
        scores.append(score)
        time.sleep(0.5)  # rate-limit courtesy pause

    print(f"    Done. Mean={statistics.mean(scores):.2f}  "
          f"Stdev={statistics.stdev(scores):.2f}    ")

    return {
        "model": model_name,
        "model_id": model_id,
        "prompt_key": prompt_key,
        "scores": scores,
        "responses": responses,
    }


# ── Core: Statistical Analysis for One Prompt ─────────────────────────────────

def analyze_prompt(
    prompt_key: str,
    prompt_config: dict,
    sonnet_data: dict,
    haiku_data: dict,
) -> dict:
    """
    Apply full statistical battery to one prompt's results.
    Returns a structured result dict ready for table rendering.
    """
    s_scores = sonnet_data["scores"]
    h_scores = haiku_data["scores"]

    # Descriptive statistics
    s_mean = round(statistics.mean(s_scores), 3)
    h_mean = round(statistics.mean(h_scores), 3)
    s_stdev = round(statistics.stdev(s_scores), 3)
    h_stdev = round(statistics.stdev(h_scores), 3)

    # Bootstrap confidence intervals (95%)
    s_ci = bootstrap_ci(s_scores)
    h_ci = bootstrap_ci(h_scores)

    # Mann-Whitney U test
    p_value = mann_whitney_u(s_scores, h_scores)

    # Cohen's d effect size
    d = cohens_d(s_scores, h_scores)

    # Human-readable interpretation
    verdict = interpret_results(p_value, d, s_mean, h_mean)

    return {
        "prompt_key": prompt_key,
        "prompt_name": prompt_config["name"],
        "sonnet_mean": s_mean,
        "sonnet_stdev": s_stdev,
        "sonnet_ci": s_ci,
        "haiku_mean": h_mean,
        "haiku_stdev": h_stdev,
        "haiku_ci": h_ci,
        "p_value": p_value,
        "cohens_d": d,
        "verdict": verdict,
        "raw_sonnet_scores": s_scores,
        "raw_haiku_scores": h_scores,
    }


# ── Rendering: Results Table (Markdown) ───────────────────────────────────────

def render_markdown_table(results: list[dict]) -> str:
    """
    Render results as a Markdown table suitable for your Tool Critic post.
    """
    lines = []
    lines.append("## Statistical Evaluation Results")
    lines.append("")
    lines.append(
        "| Prompt | Sonnet Mean ± SD | Sonnet 95% CI | "
        "Haiku Mean ± SD | Haiku 95% CI | p-value | Cohen's d | Verdict |"
    )
    lines.append(
        "|--------|-----------------|---------------|"
        "----------------|-------------|---------|-----------|---------|"
    )

    for r in results:
        s_ci = r["sonnet_ci"]
        h_ci = r["haiku_ci"]
        lines.append(
            f"| {r['prompt_name']} "
            f"| {r['sonnet_mean']:.2f} ± {r['sonnet_stdev']:.2f} "
            f"| [{s_ci[0]:.2f}, {s_ci[1]:.2f}] "
            f"| {r['haiku_mean']:.2f} ± {r['haiku_stdev']:.2f} "
            f"| [{h_ci[0]:.2f}, {h_ci[1]:.2f}] "
            f"| {r['p_value']:.4f} "
            f"| {r['cohens_d']:.3f} "
            f"| {r['verdict']} |"
        )

    lines.append("")
    lines.append(
        "> **n = 20 per model per prompt.** "
        "p-value from Mann-Whitney U (non-parametric). "
        "Cohen's d thresholds: <0.2 negligible, <0.5 small, <0.8 medium, ≥0.8 large. "
        "Verdict requires BOTH p < 0.05 AND d ≥ 0.5 to recommend a switch."
    )
    return "\n".join(lines)


# ── Rendering: Score Distribution Summary ─────────────────────────────────────

def render_score_distributions(results: list[dict]) -> str:
    """
    Show raw score distributions so readers can see the bimodal pattern
    the source article describes. This is the visual argument for why
    averages alone are misleading.
    """
    lines = ["\n## Raw Score Distributions (n=20 per cell)\n"]

    for r in results:
        lines.append(f"### {r['prompt_name']}")
        s = sorted(r["raw_sonnet_scores"])
        h = sorted(r["raw_haiku_scores"])
        lines.append(f"- **Sonnet:** `{s}`")
        lines.append(f"- **Haiku:**  `{h}`")

        # Quick histogram (text-based, no matplotlib needed)
        for label, scores in [("Sonnet", s), ("Haiku", h)]:
            buckets = {str(i): 0 for i in range(11)}
            for sc in scores:
                bucket = str(min(10, int(sc)))
                buckets[bucket] += 1
            bar = " ".join(
                f"{k}:{'█' * v}" for k, v in buckets.items() if v > 0
            )
            lines.append(f"  {label}: {bar}")
        lines.append("")

    return "\n".join(lines)


# ── Main Orchestration ─────────────────────────────────────────────────────────

def main():
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    total_calls = len(PROMPTS) * len(MODELS) * N_RUNS
    print(f"\n{'='*60}")
    print(f"GIS Prompt Evaluation Harness")
    print(f"Prompts: {len(PROMPTS)}  |  Models: {len(MODELS)}  "
          f"|  Runs each: {N_RUNS}")
    print(f"Total API calls: {total_calls}")
    print(f"{'='*60}\n")

    all_results = []

    for prompt_key, prompt_config in PROMPTS.items():
        print(f"\n── Prompt: {prompt_config['name']} ──")

        # Run both models
        sonnet_data = run_evaluations(
            "sonnet", MODELS["sonnet"], prompt_key, prompt_config
        )
        haiku_data = run_evaluations(
            "haiku", MODELS["haiku"], prompt_key, prompt_config
        )

        # Statistical analysis
        result = analyze_prompt(
            prompt_key, prompt_config, sonnet_data, haiku_data
        )
        all_results.append(result)

        print(f"\n  p={result['p_value']:.4f}  "
              f"d={result['cohens_d']:.3f}  "
              f"{result['verdict']}")

    # ── Save outputs ───────────────────────────────────────────────────────────

    # 1. Full JSON (raw scores, responses, all stats)
    json_path = output_dir / f"eval_{timestamp}.json"
    # Don't serialize full responses to keep file manageable — just scores
    json_output = [
        {k: v for k, v in r.items() if k != "raw_sonnet_scores"
         and k != "raw_haiku_scores"}
        for r in all_results
    ]
    # Include scores separately
    for i, r in enumerate(all_results):
        json_output[i]["raw_sonnet_scores"] = r["raw_sonnet_scores"]
        json_output[i]["raw_haiku_scores"] = r["raw_haiku_scores"]

    json_path.write_text(json.dumps(json_output, indent=2))
    print(f"\n✅ Raw results saved: {json_path}")

    # 2. Markdown report for Tool Critic post
    md_path = output_dir / f"report_{timestamp}.md"
    md_content = [
        "# GIS Prompt Evaluation: Sonnet vs Haiku",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"*Methodology: Mann-Whitney U + Cohen's d + Bootstrap CI (n={N_RUNS})*",
        "",
        render_markdown_table(all_results),
        render_score_distributions(all_results),
        "",
        "## Methodology Notes",
        "",
        "Scores use simple keyword coverage + code-block presence rubric.",
        "Statistical tests from: https://dev.to/aayush_kumarsingh_6ee1ffe/",
        "why-comparing-average-scores-is-the-wrong-way-to-evaluate-llm-prompts-and-what-to-do-instead-1li",
        "",
        "**Decision rule (from source):** A model is judged meaningfully better",
        "only when BOTH p < 0.05 (Mann-Whitney U) AND Cohen's d ≥ 0.5.",
        "Statistical significance alone is insufficient.",
    ]
    md_path.write_text("\n".join(md_content))
    print(f"✅ Markdown report saved: {md_path}")

    # 3. Print summary to console
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    print(render_markdown_table(all_results))
    print(render_score_distributions(all_results))


if __name__ == "__main__":
    main()
```

---

### Step 5: Run the Harness

```bash
# From your project directory:
cd gis-eval-harness
python harness.py
```

Expected console output pattern:

```
============================================================
GIS Prompt Evaluation Harness
Prompts: 3  |  Models: 2  |  Runs each: 20
Total API calls: 120
============================================================

── Prompt: Coordinate System Transformation Workflow ──
  Running 20 evals: sonnet / Coordinate System Transformation Workflow
    Done. Mean=7.43  Stdev=1.82
  Running 20 evals: haiku / Coordinate System Transformation Workflow
    Done. Mean=6.91  Stdev=2.14

  p=0.1823  d=0.264  ❌ NO RELIABLE DIFFERENCE — default to Haiku (cheaper)

── Prompt: Automated Spatial Join with Attribute Aggregation ──
  ...
```

> **Cost estimate:** 120 calls × ~500 avg output tokens. At current pricing, this run costs roughly $0.15–0.40 depending on model mix. Set `MAX_TOKENS = 512` to reduce cost during testing.

---

### Step 6: Interpret and Write Your Tool Critic Post

When the run completes, open `results/report_<timestamp>.md`. Your results table will look like this (values are illustrative — yours will differ):

```markdown
## Statistical Evaluation Results

| Prompt | Sonnet Mean ± SD | Sonnet 95% CI | Haiku Mean ± SD | Haiku 95% CI | p-value | Cohen's d | Verdict |
|--------|-----------------|---------------|----------------|-------------|---------|-----------|---------|
| Coordinate System Transformation | 7.43 ± 1.82 | [6.58, 8.21] | 6.91 ± 2.14 | [5.89, 7.82] | 0.1823 | 0.264 | ❌ NO RELIABLE DIFFERENCE — default to Haiku (cheaper) |
| Spatial Join Automation | 8.12 ± 1.31 | [7.49, 8.74] | 5.88 ± 2.67 | [4.63, 7.01] | 0.0031 | 0.971 