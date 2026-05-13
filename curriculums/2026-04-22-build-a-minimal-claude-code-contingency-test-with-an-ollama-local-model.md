# Build a Minimal Claude Code Contingency Test with an Ollama Local Model

## A Practical Guide to Hedging Against Claude Pro Pricing Changes for GIS Scripting

---

## 1. Introduction & Context

### What This Is

Anthropic recently signaled that **Claude Code is being repositioned as a premium upsell above the $20/month tier** — currently affecting ~2% of new prosumer signups, but the trajectory is clear. If you rely on Claude Code CLI for FME (Feature Manipulation Engine) automation scripts and GIS workflows, you need a concrete contingency plan *before* pricing changes force a reactive decision.

This tutorial walks you through:
1. Installing **Ollama** — a local LLM inference runtime that runs entirely on your machine
2. Pulling a capable coding model (DeepSeek Coder or equivalent)
3. Running one of your existing FME automation scripts through the local model using the **same prompt structure** you'd use with Claude Code
4. Systematically documenting **latency, code quality delta, and token cost** differences

### Why This Matters

| Factor | Claude Code (Cloud) | Ollama (Local) |
|--------|-------------------|----------------|
| Cost | $20–$?/month + potential upsell | Hardware only (one-time) |
| Privacy | Data leaves your machine | Fully air-gapped |
| Latency | Depends on API/network | Depends on your GPU |
| Quality | State-of-the-art | Very good, improving fast |
| Availability | Subject to pricing tiers | Always available |

This exercise generates **concrete, personal data** — not marketing claims — about whether a local model can realistically cover your GIS scripting needs. That data is also the foundation for a compelling **Tool Critic post** comparing Claude Code vs. local inference for GIS/FME tasks.

---

## 2. Prerequisites

### Hardware
- [ ] A machine with at least **8GB RAM** (16GB recommended)
- [ ] **GPU optional but strongly recommended**: NVIDIA GPU with 6GB+ VRAM for reasonable speed; Apple Silicon Macs (M1/M2/M3) work excellently via Metal
- [ ] **20–30GB free disk space** for model weights

### Software
- [ ] OS: Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+)
- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] An existing FME Python automation script (even a simple one — we'll use a placeholder if needed)
- [ ] Claude Code CLI installed and working (for the baseline comparison)

### Knowledge
- [ ] Basic comfort with terminal/command line
- [ ] Familiarity with your existing FME automation workflow
- [ ] Basic Python scripting

### Accounts / Access
- [ ] No API keys needed for Ollama (that's the point!)
- [ ] Your current Anthropic subscription credentials (for baseline testing)

---

## 3. Step-by-Step Guide

### Phase 1: Install Ollama

#### Step 1.1 — Download and Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download the installer from [https://ollama.com/download](https://ollama.com/download) and run the `.exe`.

**Verify installation:**
```bash
ollama --version
# Expected output: ollama version 0.x.x
```

#### Step 1.2 — Start the Ollama Service

On macOS/Linux, Ollama runs as a background service after install. Verify it's running:

```bash
# Check if Ollama is responding
curl http://localhost:11434/api/tags
# Should return JSON with available models (empty at first)
```

If not running:
```bash
ollama serve
# Run this in a separate terminal and leave it open
```

---

### Phase 2: Pull a Capable Coding Model

#### Step 2.1 — Choose Your Model

Based on your hardware, choose one of the following:

| Model | Size | Min VRAM | Quality | Command |
|-------|------|----------|---------|---------|
| `deepseek-coder:6.7b` | ~4GB | 6GB | Good | Best for limited hardware |
| `deepseek-coder:33b` | ~20GB | 20GB | Excellent | High-end GPU only |
| `codellama:13b` | ~8GB | 8GB VRAM | Good | Solid fallback |
| `qwen2.5-coder:7b` | ~5GB | 6GB | Very Good | Strong all-rounder |
| `qwen2.5-coder:14b` | ~9GB | 10GB | Excellent | Recommended if possible |

> **Recommendation for most setups:** Start with `qwen2.5-coder:7b` — it punches above its weight class for structured code generation tasks.

#### Step 2.2 — Pull the Model

```bash
# Recommended starting point
ollama pull qwen2.5-coder:7b

# If you have a powerful GPU (20GB+ VRAM)
ollama pull deepseek-coder:33b

# Lightweight fallback
ollama pull deepseek-coder:6.7b
```

> **Note on Kimi k2.6:** As of this writing, Kimi models may not be available directly via Ollama's registry. Check `ollama search kimi` — if unavailable, `qwen2.5-coder:7b` is the best equivalent.

```bash
# Check available models after download
ollama list
```

Expected output:
```
NAME                    ID              SIZE    MODIFIED
qwen2.5-coder:7b        a8b0c5157701    4.7 GB  2 minutes ago
```

---

### Phase 3: Prepare Your Test Prompt

This is the **critical step** — you must use the **same prompt structure** with both Claude Code and Ollama for a valid comparison.

#### Step 3.1 — Create a Standardized Test Prompt File

Create a file called `fme_test_prompt.txt`:

```
You are an expert FME (Feature Manipulation Engine) developer and Python GIS automation specialist.

TASK: Write a Python script that automates the following FME workflow:

1. Run an FME workspace located at: C:/Workspaces/process_parcels.fmw
2. Pass the following published parameters:
   - SOURCE_GEODATABASE: C:/Data/parcels.gdb
   - OUTPUT_FOLDER: C:/Output/
   - FILTER_FIELD: STATUS
   - FILTER_VALUE: ACTIVE
3. Log the result (success/failure) with timestamp to: C:/Logs/fme_run.log
4. If the workspace fails, send an alert email to: gis-team@example.com
5. Return exit code 0 on success, 1 on failure

REQUIREMENTS:
- Use the fmeobjects Python API where appropriate
- Handle exceptions gracefully
- Include docstrings and inline comments
- The script should be runnable from command line with optional argument overrides
- Follow PEP 8 style conventions

OUTPUT: Provide only the complete, runnable Python script with no additional explanation outside of code comments.
```

> **Why standardize the prompt?** Using the same prompt isolates the **model as the variable** — everything else stays constant. This is what makes your comparison data credible.

#### Step 3.2 — Create a Timing Wrapper Script

Create `benchmark_runner.py`:

```python
#!/usr/bin/env python3
"""
FME Automation Script Benchmark Runner
Compares Claude Code vs Ollama local inference for GIS scripting tasks.
"""

import time
import json
import datetime
import subprocess
import sys
from pathlib import Path

import requests  # pip install requests


# ─── Configuration ────────────────────────────────────────────────────────────

OLLAMA_BASE_URL = "http://localhost:11434"
PROMPT_FILE = "fme_test_prompt.txt"
OUTPUT_DIR = Path("benchmark_results")
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME = "qwen2.5-coder:7b"  # Change to your pulled model


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_prompt(filepath: str) -> str:
    """Load the test prompt from file."""
    with open(filepath, "r") as f:
        return f.read().strip()


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate: ~4 characters per token for English/code.
    Not perfectly accurate but sufficient for cost comparison.
    """
    return len(text) // 4


def save_result(label: str, result: dict) -> Path:
    """Save benchmark result to JSON file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"{label}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  ✓ Result saved to: {filename}")
    return filename


# ─── Ollama Runner ────────────────────────────────────────────────────────────

def run_ollama(prompt: str, model: str = MODEL_NAME) -> dict:
    """
    Send prompt to local Ollama instance and capture response + metrics.
    """
    print(f"\n{'='*60}")
    print(f"  Running: Ollama ({model})")
    print(f"{'='*60}")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,      # Low temp for deterministic code
            "num_predict": 2048,     # Max output tokens
        }
    }

    start_time = time.perf_counter()

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=300  # 5 minute timeout for slow hardware
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.ConnectionError:
        print("  ✗ ERROR: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("  ✗ ERROR: Request timed out after 5 minutes.")
        sys.exit(1)

    end_time = time.perf_counter()
    elapsed = end_time - start_time

    generated_text = data.get("response", "")
    prompt_tokens = data.get("prompt_eval_count", estimate_tokens(prompt))
    completion_tokens = data.get("eval_count", estimate_tokens(generated_text))

    result = {
        "provider": "ollama_local",
        "model": model,
        "timestamp": datetime.datetime.now().isoformat(),
        "latency_seconds": round(elapsed, 2),
        "tokens_per_second": round(completion_tokens / elapsed, 1) if elapsed > 0 else 0,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated_cost_usd": 0.00,  # Local = $0 marginal cost
        "generated_code": generated_text,
        "raw_response_keys": list(data.keys()),
    }

    print(f"  ✓ Completed in {elapsed:.1f}s")
    print(f"  ✓ Speed: {result['tokens_per_second']} tokens/sec")
    print(f"  ✓ Tokens: {result['total_tokens']} total")
    print(f"  ✓ Cost: $0.00 (local)")

    return result


# ─── Claude Runner (Manual Capture Mode) ──────────────────────────────────────

def capture_claude_result(prompt: str) -> dict:
    """
    Claude Code CLI doesn't expose a simple benchmarkable API,
    so this function guides you through a manual timed capture.

    For Claude API users, replace this with direct API calls.
    """
    print(f"\n{'='*60}")
    print(f"  Running: Claude Code (Manual Capture)")
    print(f"{'='*60}")
    print("""
  INSTRUCTIONS:
  1. Open a NEW terminal window
  2. Run your Claude Code command with the prompt
  3. When complete, note the time and paste the output below
  4. Return here and press Enter when ready
    """)

    # Write prompt to clipboard hint
    prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
    print(f"  PROMPT PREVIEW:\n  {prompt_preview}\n")

    input("  Press Enter when you have Claude Code's output ready...")

    # Capture timing manually
    print("\n  Enter the wall-clock time Claude Code took (in seconds):")
    try:
        latency = float(input("  Latency (seconds): "))
    except ValueError:
        latency = 0.0

    print("\n  Paste Claude Code's generated code below.")
    print("  Type '###END###' on its own line when done:\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "###END###":
            break
        lines.append(line)

    generated_text = "\n".join(lines)

    # Rough Claude pricing (as of 2024): claude-3-5-sonnet
    # Input: $3/M tokens, Output: $15/M tokens
    prompt_tokens = estimate_tokens(prompt)
    completion_tokens = estimate_tokens(generated_text)
    cost = (prompt_tokens / 1_000_000 * 3.00) + (completion_tokens / 1_000_000 * 15.00)

    result = {
        "provider": "claude_code",
        "model": "claude-3-5-sonnet (assumed)",
        "timestamp": datetime.datetime.now().isoformat(),
        "latency_seconds": latency,
        "tokens_per_second": round(completion_tokens / latency, 1) if latency > 0 else 0,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated_cost_usd": round(cost, 6),
        "generated_code": generated_text,
        "note": "Manual capture - latency is approximate wall-clock time"
    }

    print(f"\n  ✓ Captured Claude result")
    print(f"  ✓ Estimated cost: ${cost:.6f}")

    return result


# ─── Code Quality Evaluator ───────────────────────────────────────────────────

def evaluate_code_quality(code: str, label: str) -> dict:
    """
    Run basic automated quality checks on generated code.
    Returns a quality score dict.
    """
    print(f"\n  Evaluating code quality for: {label}")

    checks = {
        "has_imports": "import" in code,
        "has_docstring": '"""' in code or "'''" in code,
        "has_main_guard": 'if __name__' in code,
        "has_exception_handling": "try:" in code or "except" in code,
        "has_logging": "logging" in code or "log" in code.lower(),
        "has_fme_reference": "fme" in code.lower() or "fmeobjects" in code.lower(),
        "has_argparse": "argparse" in code,
        "has_comments": "#" in code,
        "has_type_hints": "->" in code or ": str" in code or ": int" in code,
        "line_count": len(code.splitlines()),
        "non_empty": len(code.strip()) > 100,
    }

    # Calculate score (out of boolean checks only)
    boolean_checks = {k: v for k, v in checks.items()
                     if isinstance(v, bool)}
    score = sum(boolean_checks.values())
    max_score = len(boolean_checks)
    percentage = round((score / max_score) * 100, 1)

    checks["quality_score"] = f"{score}/{max_score} ({percentage}%)"
    checks["score_numeric"] = percentage

    for check, value in boolean_checks.items():
        status = "✓" if value else "✗"
        print(f"    {status} {check}: {value}")

    print(f"\n  Quality Score: {checks['quality_score']}")
    print(f"  Lines of code: {checks['line_count']}")

    return checks


# ─── Comparison Report ────────────────────────────────────────────────────────

def generate_comparison_report(ollama_result: dict, claude_result: dict,
                                ollama_quality: dict, claude_quality: dict) -> str:
    """Generate a markdown comparison report."""

    latency_diff = claude_result['latency_seconds'] - ollama_result['latency_seconds']
    quality_diff = ollama_quality['score_numeric'] - claude_quality['score_numeric']

    report = f"""# Claude Code vs Ollama Local: FME Scripting Benchmark
Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Test Configuration
- **Prompt:** Standardized FME Python automation task
- **Claude Model:** {claude_result['model']}
- **Local Model:** {ollama_result['model']}

## Performance Comparison

| Metric | Claude Code | Ollama Local | Delta |
|--------|-------------|--------------|-------|
| Latency (seconds) | {claude_result['latency_seconds']:.1f}s | {ollama_result['latency_seconds']:.1f}s | {latency_diff:+.1f}s |
| Speed (tokens/sec) | {claude_result['tokens_per_second']} | {ollama_result['tokens_per_second']} | — |
| Total Tokens | {claude_result['total_tokens']} | {ollama_result['total_tokens']} | — |
| Estimated Cost (this run) | ${claude_result['estimated_cost_usd']:.6f} | $0.000000 | — |
| Quality Score | {claude_quality['quality_score']} | {ollama_quality['quality_score']} | {quality_diff:+.1f}% |

## Cost Projection

| Usage Level | Claude Code (API) | Ollama Local |
|-------------|-------------------|--------------|
| 10 runs/day | ${claude_result['estimated_cost_usd'] * 10 * 30:.2f}/month | $0.00/month |
| 50 runs/day | ${claude_result['estimated_cost_usd'] * 50 * 30:.2f}/month | $0.00/month |
| Subscription ($20/mo) | Capped at $20/mo | Hardware amortized |

## Code Quality Breakdown

### Claude Code Checks
{chr(10).join(f"- {'✓' if v else '✗'} {k}" for k, v in claude_quality.items() if isinstance(v, bool))}

### Ollama Local Checks
{chr(10).join(f"- {'✓' if v else '✗'} {k}" for k, v in ollama_quality.items() if isinstance(v, bool))}

## Observations
- **Latency Winner:** {"Claude Code" if claude_result['latency_seconds'] < ollama_result['latency_seconds'] else "Ollama Local"}
- **Cost Winner:** Ollama Local (always $0 marginal cost)
- **Quality Winner:** {"Claude Code" if claude_quality['score_numeric'] > ollama_quality['score_numeric'] else "Ollama Local" if ollama_quality['score_numeric'] > claude_quality['score_numeric'] else "Tie"}

## Recommendation
{generate_recommendation(ollama_result, claude_result, ollama_quality, claude_quality)}

---
*Generated by benchmark_runner.py — for Tool Critic post on Claude Code vs Local Inference for GIS*
"""
    return report


def generate_recommendation(ollama_result, claude_result, ollama_quality, claude_quality):
    """Generate a text recommendation based on benchmark data."""
    quality_gap = claude_quality['score_numeric'] - ollama_quality['score_numeric']

    if quality_gap > 20:
        return ("Claude Code maintains a significant quality advantage (>{:.0f}% gap). "
                "Consider keeping Claude Code for complex scripting tasks while using "
                "Ollama for simpler, templated work.".format(quality_gap))
    elif quality_gap > 0:
        return ("Claude Code has a marginal quality edge ({:.0f}% gap) but the cost "
                "savings of local inference are substantial. For most FME automation "
                "tasks, the local model is viable as a primary tool.".format(quality_gap))
    else:
        return ("Local inference is competitive or superior for this task type. "
                "The {} model is a credible Claude Code replacement for FME "
                "scripting workflows.".format(ollama_result['model']))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  FME AUTOMATION BENCHMARK: Claude Code vs Ollama Local")
    print("="*60)

    # Load prompt
    prompt = load_prompt(PROMPT_FILE)
    print(f"\n  Prompt loaded: {len(prompt)} characters (~{estimate_tokens(prompt)} tokens)")

    # Run Ollama
    ollama_result = run_ollama(prompt, MODEL_NAME)
    ollama_quality = evaluate_code_quality(
        ollama_result["generated_code"], "Ollama"
    )
    ollama_result["quality"] = ollama_quality
    save_result("ollama", ollama_result)

    # Run Claude (manual capture)
    print("\n  Now we'll capture your Claude Code result for comparison.")
    choice = input("  Run Claude Code comparison now? (y/n): ").strip().lower()

    if choice == 'y':
        claude_result = capture_claude_result(prompt)
        claude_quality = evaluate_code_quality(
            claude_result["generated_code"], "Claude"
        )
        claude_result["quality"] = claude_quality
        save_result("claude", claude_result)

        # Generate report
        report = generate_comparison_report(
            ollama_result, claude_result,
            ollama_quality, claude_quality
        )

        report_path = OUTPUT_DIR / f"comparison_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, "w") as f:
            f.write(report)

        print(f"\n{'='*60}")
        print("  BENCHMARK COMPLETE")
        print(f"{'='*60}")
        print(f"\n  Report saved to: {report_path}")
        print("\n  Summary:")
        print(report)

    else:
        print("\n  Ollama-only run complete. Run again with Claude when ready.")
        print(f"  Results saved in: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
```

#### Step 3.3 — Install Python Dependencies

```bash
pip install requests
```

---

### Phase 4: Run the Benchmark

#### Step 4.1 — Verify Ollama Is Ready

```bash
# Test Ollama responds
curl http://localhost:11434/api/tags

# Quick model test (should return code immediately)
ollama run qwen2.5-coder:7b "Write a one-line Python hello world" --nowordwrap
```

#### Step 4.2 — Run the Benchmark Script

```bash
# From your project directory
python benchmark_runner.py
```

You'll see:
```
============================================================
  FME AUTOMATION BENCHMARK: Claude Code vs Ollama Local
============================================================

  Prompt loaded: 847 characters (~211 tokens)

============================================================
  Running: Ollama (qwen2.5-coder:7b)
============================================================
  ✓ Completed in 47.3s
  ✓ Speed: 31.2 tokens/sec
  ✓ Tokens: 1847 total
  ✓ Cost: $0.00 (local)
```

#### Step 4.3 — Run Your Claude Code Baseline

In a **separate terminal**, run your standard Claude Code command. Time it with the system clock or use:

```bash
# Time your Claude Code run manually
time claude "$(cat fme_test_prompt.txt)"

# Or if using the Anthropic Python SDK directly:
time python your_existing_claude_script.py
```

When prompted by the benchmark script, enter the timing and paste the output.

#### Step 4.4 — Alternative: Direct API Comparison (Optional)

If you want fully automated Claude API comparison (bypassing Claude Code CLI):

```python
# claude_api_runner.py — add to your benchmark setup
import anthropic
import time

def run_claude_api(prompt: str) -> dict:
    """Direct API call for automated benchmarking."""
    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
    
    start = time.perf_counter()
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )
    
    elapsed = time.perf_counter() - start
    
    return {
        "provider": "claude_api",
        "model": message.model,
        "latency_seconds": round(elapsed, 2),
        "prompt_tokens": message.usage.input_tokens,
        "completion_tokens": message.usage.output_tokens,
        "total_tokens": message.usage.input_tokens + message.usage.output_tokens,
        "estimated_cost_usd": round(
            (message.usage.input_tokens / 1_000_000 * 3.00) +
            (message.usage.output_tokens / 1_000_000 * 15.00), 6
        ),
        "generated_code": message.content[0].text,
    }
```

Install and run:
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
python claude_api_runner.py
```

---

### Phase 5: Document and Analyze Results

#### Step 5.1 — Review Generated Output Files

```
benchmark_results/
├── ollama_20241215_143022.json
├── claude_20241215_143522.json
└── comparison_report_20241215_143523.md
```

#### Step 5.2 — Manual Code Review Checklist

Open both generated Python files and score them on this rubric:

```markdown
## Code Review Rubric (score 1-5 each)

### Correctness
- [ ] Does the script correctly invoke fmeobjects API?        /5
- [ ] Are the published parameters passed correctly?          /5
- [ ] Is the logging implementation complete and correct?     /5
- [ ] Is email alerting implemented (even if placeholder)?    /5

### Code Quality
- [ ] Exception handling is comprehensive                     /5
- [ ] Docstrings are meaningful (not boilerplate)             /5
- [ ] Command-line argument overrides work as specified        /5
- [ ] Exit codes are correctly implemented                    /5

### GIS/FME Domain Knowledge
- [ ] Uses fmeobjects correctly (not just subprocess calls)   /5
- [ ] Handles FME-specific error types appropriately          /5

### Total: __ / 50
```

#### Step 5.3 — Record Your Findings

Create `my_benchmark_notes.md`:

```markdown
# My Claude Code vs Ollama Benchmark Notes
Date: [DATE]
Machine: [YOUR SPECS - CPU, GPU, RAM]

## Results Summary

| Metric | Claude Code | Ollama (qwen2.5-coder:7b) |
|--------|-------------|---------------------------|
| Latency | ___s | ___s |
| Tokens/sec | ___ | ___ |
| Code quality (auto) | ___% | ___% |
| Code quality (manual) | ___/50 | ___/50 |
| Cost per run | $___  | $0.00 |

## What Ollama Got Right
- [Note specific good outputs]

## What Ollama Got Wrong or Missed
- [Note gaps, errors, hallucinations]

## Domain-Specific Observations
- [FME API usage accuracy]
- [GIS-specific knowledge quality]

## Verdict for My Workflow
- [ ] Local model is viable as primary tool
- [ ] Local model works as fallback/draft tool
- [ ] Claude Code is clearly superior for this use case

## Monthly Cost Projection
At my usage level (___runs/day):
- Claude Code: $___/month
- Ollama: $0/month marginal (hardware: $0 if already owned)
```

---

## 4. Validation

### ✅ Checklist: Did You Complete This Exercise?

**Setup Validation:**
```bash
# All of these should succeed
ollama --version           # Should show version number
ollama list                # Should show your pulled model
curl http://localhost:11434/api/tags   # Should return JSON
```

**Benchmark Validation:**
```bash
# Check that output files exist
ls -la benchmark_results/
# Should show at least one ollama_*.json file

# Verify JSON is valid and contains the code
python -c "
import json, glob
files = glob.glob('benchmark_results/ollama_*.json')
with open(files[-1]) as f:
    data = json.load(f)
print('Latency:', data['latency_seconds'], 's')
print('Code length:', len(data['generated_code']), 'chars')
print('Quality score:', data['quality']['quality_score'])
"
```

**Content Validation:**
- [ ] You have at least one complete generated Python script from Ollama
- [ ] You have timing data for the Ollama run
- [ ] You have timing data for at least one Claude Code run (even if manually captured)
- [ ] You've scored both outputs on the manual code review rubric
- [ ] A comparison report `.md` file exists in `benchmark_results/`

**Meaningful Completion:**
- [ ] You can articulate ONE specific thing the local model did better than expected
- [ ] You can articulate ONE specific gap where Claude Code was clearly superior
- [ ] You have a concrete cost-per-run figure for the Claude API path
- [ ] You know your monthly break-even point

---

## 5. Next Steps

### Immediate (This Week)

**1. Expand Your Prompt Library**

Test 2–3 more FME prompt types to avoid single-test bias:
```bash
# Create additional test prompts
cp fme_test_prompt.txt fme_prompt_spatial_join.txt
cp fme_test_prompt.txt fme_prompt_data_validation.txt
# Edit each with different FME scenarios
```

**2. Test Model Alternatives**

```bash
# If qwen2.5-coder:7b was too slow
ollama pull deepseek-coder:6.7b

# If you want to push quality ceiling
ollama pull qwen2.5-coder:14b
ollama pull deepseek-coder-v2:16b
```

**3. Set Up a Simple CLI Wrapper**

```bash
# fme_local.sh — a drop-in for simple Claude Code tasks
#!/bin/bash
PROMPT="$1"
ollama run qwen2.5-coder:7b "$PROMPT" --nowordwrap
```

### Short-Term (This Month)

**4. Write the Tool Critic Post**

Your benchmark data is your content. Structure it as:
- "I ran the same FME prompt through Claude Code and a local Ollama model. Here's exactly what happened."
- Include raw numbers (don't editorialize yet — let data lead)
- Note specific code quality differences with actual code excerpts
- Calculate realistic monthly cost scenarios for GIS practitioners

**5. Integrate into Your Existing Workflow**

```python
# Add to your FME automation toolkit as a fallback selector
def get_ai_client(prefer_local=False, task_complexity="medium"):
    """Return appropriate AI client based on cost/quality tradeoff."""
    if prefer_local or task_complexity == "low":
        return OllamaClient(model="q