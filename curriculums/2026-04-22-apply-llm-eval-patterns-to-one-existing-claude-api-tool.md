# Apply LLM Eval Patterns to One Existing Claude API Tool

## A Practical Curriculum for Adding Production-Grade Testing to Your Streamlit AI Apps

---

## 1. Introduction & Context

### What Is This?

You've built Claude API tools. They work — mostly. But "mostly" isn't good enough when you're building toward a production-grade AI workflow or writing credible Build pillar content about GIS AI tools. Right now, you're likely **vibing through bugs**: testing by eye, noticing failures in production, and having no quantitative baseline to measure improvements against.

This exercise fixes that. You'll add a **minimal eval layer** to one of your existing Claude API Streamlit tools — the kind of testing infrastructure that separates professional AI developers from people who just ship prompts and hope.

### Why Evals Are Different from Normal Testing

Standard web dev testing is deterministic: `assert output == expected`. AI outputs are probabilistic and semantic — "Paris" and "The capital of France is Paris" are both correct answers to the same question, but a string comparison would fail one of them.

**LLM evals** solve this by using a second LLM (a "judge") to score outputs against criteria rather than exact matches. This is the pattern sentdex covers in his AI testing video, and it's what companies like Anthropic, OpenAI, and every serious AI product team use internally.

### What You'll Build

```
Your Existing Tool
       │
       ▼
┌─────────────────────────────────┐
│         Eval Layer              │
│  • 5 test inputs                │
│  • 5 expected outputs           │
│  • LLM-as-judge scoring prompt  │
│  • Baseline score report        │
└─────────────────────────────────┘
       │
       ▼
  eval_results.json  (your baseline)
```

By the end, you'll have a **repeatable, quantitative baseline score** you can run before and after any prompt change.

---

## 2. Prerequisites

### Knowledge
- [ ] Basic Python (functions, dicts, loops)
- [ ] You've built at least one Streamlit app that calls the Claude API
- [ ] You understand what a system prompt and user message are in the Claude API
- [ ] You've watched (or are watching alongside) the [sentdex AI Testing video](https://www.youtube.com/watch?v=ji08ILsXQ7M)

### Environment
- [ ] Python 3.9+ installed
- [ ] An existing Claude API Streamlit project (any tool works — GIS query tool, document analyzer, etc.)
- [ ] `ANTHROPIC_API_KEY` set in your environment
- [ ] The following packages available (install if needed):

```bash
pip install anthropic streamlit python-dotenv
```

### Mental Checkpoint
Before starting, answer these questions about your chosen tool:
1. What does it take as **input**?
2. What does it return as **output**?
3. What would a **good** response look like vs. a **bad** one?

If you can answer those three questions, you're ready to write evals.

---

## 3. Step-by-Step Guide

### Step 0: Choose Your Tool and Understand Its Core Function

Pick the **simplest** Claude API tool you have. A GIS query tool, a document summarizer, a code explainer — anything with a clear input/output pattern.

For this tutorial, we'll use a **GIS Query Tool** as the example (replace with your actual tool's logic):

```python
# Your existing tool's core function probably looks something like this:
def query_gis_assistant(user_question: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="You are a GIS expert assistant. Answer questions about spatial data, coordinate systems, and geospatial analysis.",
        messages=[{"role": "user", "content": user_question}]
    )
    return response.content[0].text
```

**Write down your tool's equivalent function signature before moving on.**

---

### Step 1: Create the Eval File Structure

Create a new file in your project directory. Keep it separate from your main Streamlit app so it doesn't clutter production code:

```
your_project/
├── app.py                    # Your existing Streamlit app (unchanged)
├── eval_your_tool.py         # ← New file you're creating
├── eval_results.json         # ← Will be generated automatically
└── .env                      # Your API key
```

```bash
# In your project directory:
touch eval_your_tool.py
```

---

### Step 2: Define Your 5 Test Cases

This is the most important thinking work. Open `eval_your_tool.py` and define your test cases:

**The pattern for each test case:**
- `input`: Exactly what a user would type/submit
- `expected_behavior`: A plain English description of what a good response includes (NOT an exact string)
- `must_include`: Non-negotiable elements that must appear
- `must_avoid`: Things that would make the response wrong or dangerous

```python
# eval_your_tool.py

TEST_CASES = [
    {
        "id": "TC001",
        "input": "What coordinate system should I use for mapping distances in the continental United States?",
        "expected_behavior": "Recommends a suitable projected coordinate system (like Albers Equal Area or UTM) with a clear reason why it's appropriate for distance calculations",
        "must_include": ["projected", "distance"],
        "must_avoid": ["WGS84 is fine for distances", "geographic coordinates work"],
        "category": "coordinate_systems"
    },
    {
        "id": "TC002",
        "input": "Explain what a shapefile is to someone who has never done GIS before",
        "expected_behavior": "Gives a clear, jargon-free explanation that includes what a shapefile stores and mentions it's actually multiple files",
        "must_include": ["spatial", "multiple files"],
        "must_avoid": ["assumes prior GIS knowledge", "overly technical without explanation"],
        "category": "fundamentals"
    },
    {
        "id": "TC003",
        "input": "My GeoDataFrame spatial join is returning empty results. What should I check first?",
        "expected_behavior": "Provides a systematic debugging approach, starting with CRS mismatch as the most common cause",
        "must_include": ["CRS", "coordinate reference system"],
        "must_avoid": ["vague suggestions", "suggests reinstalling Python"],
        "category": "debugging"
    },
    {
        "id": "TC004",
        "input": "What's the difference between raster and vector data?",
        "expected_behavior": "Clearly distinguishes both formats with concrete real-world examples of when each is used",
        "must_include": ["grid", "pixel", "polygon", "line", "point"],
        "must_avoid": ["confuses the two", "only defines one type"],
        "category": "fundamentals"
    },
    {
        "id": "TC005",
        "input": "asdfghjkl what is blarg coordinate",
        "expected_behavior": "Handles the nonsensical input gracefully — asks for clarification or explains it didn't understand, without making up an answer",
        "must_include": [],
        "must_avoid": ["invents a definition for 'blarg'", "confidently answers nonsense"],
        "category": "edge_case"
    }
]
```

> **🔑 Key Insight:** Write `expected_behavior` as if you're briefing a human grader. The LLM judge will use this description to score the response. Be specific about *what* makes a response good, not just that it should be "good."

**Adapting this for YOUR tool:**

| Tool Type | Good TC001 Input | Good Expected Behavior |
|-----------|-----------------|----------------------|
| Document Summarizer | "Summarize this 500-word legal agreement: [text]" | "Hits the 3 main clauses, uses plain English, under 100 words" |
| Code Explainer | "What does `list(map(lambda x: x*2, range(5)))` do?" | "Explains each component: lambda, map, range, list conversion" |
| SQL Generator | "Show me all users who signed up last month" | "Generates valid SQL with correct date filter syntax" |

---

### Step 3: Build the Tool Runner

Now wire in your actual tool function. This is where you connect the eval harness to your existing code:

```python
# eval_your_tool.py (continued)

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================
# PASTE YOUR ACTUAL TOOL FUNCTION HERE
# (Copy from your app.py and strip any Streamlit UI calls)
# ============================================================
def run_tool(user_input: str) -> str:
    """
    This is YOUR tool's core logic.
    Replace this with the actual function from your Streamlit app.
    """
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="""You are a GIS expert assistant. Help users understand 
        spatial data, coordinate systems, and geospatial analysis concepts.
        Be accurate, practical, and appropriately detailed.""",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    return response.content[0].text
```

---

### Step 4: Build the LLM-as-Judge Scorer

This is the eval pattern from the sentdex video in action. You're using `claude-haiku-4-5` (fast and cheap) to score responses from your main tool:

```python
# eval_your_tool.py (continued)

def llm_judge_score(
    test_input: str,
    tool_response: str,
    expected_behavior: str,
    must_include: list,
    must_avoid: list
) -> dict:
    """
    Uses claude-haiku-4-5 as an LLM judge to score a tool response.
    Returns a score dict with numeric score and reasoning.
    """
    
    # Format must_include and must_avoid for the prompt
    must_include_str = "\n".join([f"  - {item}" for item in must_include]) if must_include else "  - (none specified)"
    must_avoid_str = "\n".join([f"  - {item}" for item in must_avoid]) if must_avoid else "  - (none specified)"
    
    judge_prompt = f"""You are an expert evaluator for an AI assistant. Score the following AI response.

## Original User Input
{test_input}

## AI Response to Evaluate  
{tool_response}

## Evaluation Criteria

**What a good response should do:**
{expected_behavior}

**The response MUST include (concepts, not exact words):**
{must_include_str}

**The response MUST NOT include or imply:**
{must_avoid_str}

## Your Task

Score this response on a scale of 1-5:
- **5**: Excellent. Meets all criteria, includes required elements, avoids prohibited elements, is clear and accurate.
- **4**: Good. Meets most criteria with minor gaps. Still useful and accurate.
- **3**: Acceptable. Partially meets criteria. Missing some required elements but not harmful.
- **2**: Poor. Significantly misses the mark. Missing key required elements or includes avoided elements.
- **1**: Fail. Completely wrong, harmful, confusing, or confidently answers nonsense.

Respond ONLY in this exact JSON format:
{{
  "score": <integer 1-5>,
  "reasoning": "<2-3 sentences explaining the score>",
  "missing_elements": ["<any must_include items that were absent>"],
  "violations": ["<any must_avoid items that appeared>"]
}}"""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[
            {"role": "user", "content": judge_prompt}
        ]
    )
    
    # Parse the JSON response
    import json
    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        # If parsing fails, return a structured error
        return {
            "score": 0,
            "reasoning": f"Judge failed to return valid JSON. Raw response: {response.content[0].text[:200]}",
            "missing_elements": [],
            "violations": ["JUDGE_PARSE_ERROR"]
        }
```

> **💡 Why Haiku for the judge?** It's ~20x cheaper than Opus and plenty capable for scoring tasks. You're not asking it to do complex reasoning — just evaluate against clear criteria. Save the expensive models for your actual tool.

---

### Step 5: Build the Eval Runner and Report Generator

```python
# eval_your_tool.py (continued)

import json
import time
from datetime import datetime

def run_eval_suite(test_cases: list, verbose: bool = True) -> dict:
    """
    Runs the full eval suite and returns a results report.
    """
    results = []
    total_score = 0
    
    print(f"\n{'='*60}")
    print(f"  EVAL RUN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Tool: GIS Assistant (replace with your tool name)")
    print(f"  Test Cases: {len(test_cases)}")
    print(f"{'='*60}\n")
    
    for i, tc in enumerate(test_cases):
        print(f"[{i+1}/{len(test_cases)}] Running: {tc['id']} ({tc['category']})")
        print(f"  Input: {tc['input'][:80]}...")
        
        # Step 1: Get tool response
        try:
            tool_response = run_tool(tc["input"])
        except Exception as e:
            tool_response = f"ERROR: Tool failed with: {str(e)}"
        
        if verbose:
            print(f"  Response preview: {tool_response[:100]}...")
        
        # Step 2: Get judge score
        # Small delay to avoid rate limits
        time.sleep(0.5)
        
        judge_result = llm_judge_score(
            test_input=tc["input"],
            tool_response=tool_response,
            expected_behavior=tc["expected_behavior"],
            must_include=tc["must_include"],
            must_avoid=tc["must_avoid"]
        )
        
        score = judge_result.get("score", 0)
        total_score += score
        
        # Compile result
        result = {
            "test_id": tc["id"],
            "category": tc["category"],
            "input": tc["input"],
            "tool_response": tool_response,
            "expected_behavior": tc["expected_behavior"],
            "score": score,
            "max_score": 5,
            "reasoning": judge_result.get("reasoning", ""),
            "missing_elements": judge_result.get("missing_elements", []),
            "violations": judge_result.get("violations", []),
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)
        
        # Print score with visual indicator
        score_bar = "█" * score + "░" * (5 - score)
        print(f"  Score: [{score_bar}] {score}/5")
        print(f"  Reason: {judge_result.get('reasoning', 'N/A')[:100]}")
        print()
    
    # Calculate summary stats
    avg_score = total_score / len(test_cases)
    max_possible = len(test_cases) * 5
    percentage = (total_score / max_possible) * 100
    
    # Score by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r["score"])
    
    category_averages = {
        cat: round(sum(scores)/len(scores), 2) 
        for cat, scores in categories.items()
    }
    
    # Build final report
    report = {
        "run_metadata": {
            "timestamp": datetime.now().isoformat(),
            "tool_name": "GIS Assistant",  # Update this
            "tool_model": "claude-opus-4-5",
            "judge_model": "claude-haiku-4-5",
            "num_test_cases": len(test_cases)
        },
        "summary": {
            "total_score": total_score,
            "max_possible_score": max_possible,
            "average_score": round(avg_score, 2),
            "percentage": round(percentage, 1),
            "grade": get_grade(percentage)
        },
        "category_breakdown": category_averages,
        "individual_results": results
    }
    
    return report


def get_grade(percentage: float) -> str:
    if percentage >= 90: return "A - Production Ready"
    if percentage >= 80: return "B - Good, Minor Issues"
    if percentage >= 70: return "C - Acceptable, Needs Work"
    if percentage >= 60: return "D - Significant Issues"
    return "F - Major Problems"


def save_results(report: dict, filename: str = "eval_results.json"):
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Results saved to {filename}")


def print_final_report(report: dict):
    summary = report["summary"]
    print(f"\n{'='*60}")
    print(f"  EVAL COMPLETE")
    print(f"{'='*60}")
    print(f"  Total Score:  {summary['total_score']}/{summary['max_possible_score']}")
    print(f"  Average:      {summary['average_score']}/5")
    print(f"  Percentage:   {summary['percentage']}%")
    print(f"  Grade:        {summary['grade']}")
    print(f"\n  Category Breakdown:")
    for cat, avg in report["category_breakdown"].items():
        bar = "█" * round(avg) + "░" * (5 - round(avg))
        print(f"    {cat:<20} [{bar}] {avg}/5")
    print(f"{'='*60}\n")
```

---

### Step 6: Wire It All Together with a Main Block

```python
# eval_your_tool.py (continued — add at the bottom)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LLM evals on your Claude API tool")
    parser.add_argument("--verbose", action="store_true", help="Show full responses during run")
    parser.add_argument("--output", default="eval_results.json", help="Output file for results")
    args = parser.parse_args()
    
    # Run the eval suite
    report = run_eval_suite(TEST_CASES, verbose=args.verbose)
    
    # Print the summary
    print_final_report(report)
    
    # Save results
    save_results(report, args.output)
    
    print(f"\n🎯 BASELINE SCORE RECORDED: {report['summary']['percentage']}%")
    print(f"📁 Full results in: {args.output}")
    print(f"\nThis is your baseline. Run again after prompt changes to measure improvement.")
```

---

### Step 7: The Complete File at a Glance

Your complete `eval_your_tool.py` should have these sections in order:

```
eval_your_tool.py
├── Imports (anthropic, json, time, datetime, os, dotenv)
├── TEST_CASES list (your 5 test cases)
├── client = anthropic.Anthropic(...)
├── run_tool() function (your actual tool logic)
├── llm_judge_score() function
├── run_eval_suite() function
├── get_grade() helper
├── save_results() helper
├── print_final_report() helper
└── if __name__ == "__main__" block
```

---

### Step 8: Run Your First Eval

```bash
# Basic run
python eval_your_tool.py

# Verbose run (see full responses)
python eval_your_tool.py --verbose

# Custom output file
python eval_your_tool.py --output baseline_v1.json
```

**Expected output looks like this:**

```
============================================================
  EVAL RUN: 2024-01-15 14:32:01
  Tool: GIS Assistant
  Test Cases: 5
============================================================

[1/5] Running: TC001 (coordinate_systems)
  Input: What coordinate system should I use for mapping dista...
  Response preview: For mapping distances in the continental United States...
  Score: [████░] 4/5
  Reason: Response correctly recommends Albers Equal Area projection...

[2/5] Running: TC002 (fundamentals)
  Input: Explain what a shapefile is to someone who has never ...
  Score: [█████] 5/5
  Reason: Excellent explanation covering all required elements...

[3/5] Running: TC003 (debugging)
  ...

============================================================
  EVAL COMPLETE
============================================================
  Total Score:  19/25
  Average:      3.8/5
  Percentage:   76.0%
  Grade:        C - Acceptable, Needs Work

  Category Breakdown:
    coordinate_systems   [████░] 4/5
    fundamentals         [█████] 5/5
    debugging            [███░░] 3/5
    edge_case            [██░░░] 2/5
============================================================

🎯 BASELINE SCORE RECORDED: 76.0%
📁 Full results in: eval_results.json
```

---

### Step 9: Read and Understand Your eval_results.json

Open your results file and look at the individual results:

```json
{
  "run_metadata": {
    "timestamp": "2024-01-15T14:32:45",
    "tool_name": "GIS Assistant",
    "tool_model": "claude-opus-4-5",
    "judge_model": "claude-haiku-4-5",
    "num_test_cases": 5
  },
  "summary": {
    "total_score": 19,
    "max_possible_score": 25,
    "average_score": 3.8,
    "percentage": 76.0,
    "grade": "C - Acceptable, Needs Work"
  },
  "category_breakdown": {
    "coordinate_systems": 4.0,
    "fundamentals": 5.0,
    "debugging": 3.0,
    "edge_case": 2.0
  }
}
```

**How to read your scores:**

| Score | What It Means | Action |
|-------|--------------|--------|
| 4.5-5.0/5 | Your prompts are solid for this category | Monitor, don't touch |
| 3.5-4.4/5 | Good baseline, room for improvement | Note for next sprint |
| 2.5-3.4/5 | Meaningful gaps | Improve your system prompt here |
| 1.0-2.4/5 | Significant problem | Fix this before shipping |

---

## 4. Validation

### ✅ Checklist: Did You Actually Complete This?

Run through each item:

- [ ] **File exists**: `eval_your_tool.py` is in your project directory
- [ ] **All 5 test cases defined**: `len(TEST_CASES) == 5`
- [ ] **Tool function connected**: `run_tool()` calls your actual Claude API logic, not a placeholder
- [ ] **Judge uses Haiku**: `model="claude-haiku-4-5"` in `llm_judge_score()`
- [ ] **Results file generated**: `eval_results.json` exists after running
- [ ] **Baseline recorded**: You know your percentage score (write it down!)
- [ ] **Score makes sense**: Each score has reasoning that you can read and agree/disagree with

### 🔍 Verify the Judge Is Working Correctly

Run this quick sanity check — manually inspect 2 of your 5 results:

```python
# Quick sanity check script
import json

with open("eval_results.json") as f:
    results = json.load(f)

for r in results["individual_results"][:2]:
    print(f"\nTest: {r['test_id']}")
    print(f"Score: {r['score']}/5")
    print(f"Reasoning: {r['reasoning']}")
    print(f"Response excerpt: {r['tool_response'][:200]}")
    print("---")
    print("Does this score make sense to YOU? (yes/no)")
    input()
```

If the judge's reasoning aligns with your own judgment on 3+ out of 5 cases, the eval is working. If it's systematically off (always too harsh or too lenient), adjust your judge prompt criteria.

### 📊 What Your Baseline Score Means

Record this in your notes or a project README:

```markdown
## Eval Baseline - [Date]
- Tool: [Your Tool Name]
- Score: [X.X]/5 ([XX]%)
- Grade: [Your Grade]
- Weakest Category: [Category]
- Run Command: `python eval_your_tool.py --output baseline_v1.json`
```

---

## 5. Next Steps

### Immediate (This Week)

**1. Improve Your Weakest Category**

Look at your lowest-scoring test case. Read the judge's reasoning. Now update your system prompt to address the gap. Then re-run:

```bash
python eval_your_tool.py --output after_prompt_fix_v2.json
```

Did your score go up? That's **evidence-based prompt engineering**.

**2. Add a Regression Check**

Add this simple script so you can compare runs:

```python
# compare_runs.py
import json
import sys

def compare(file1: str, file2: str):
    with open(file1) as f: r1 = json.load(f)
    with open(file2) as f: r2 = json.load(f)
    
    score1 = r1["summary"]["percentage"]
    score2 = r2["summary"]["percentage"]
    delta = score2 - score1
    
    print(f"Before: {score1}% ({file1})")
    print(f"After:  {score2}% ({file2})")
    print(f"Delta:  {'+' if delta >= 0 else ''}{delta:.1f}%")
    
    # Category comparison
    print("\nCategory Changes:")
    for cat in r1["category_breakdown"]:
        if cat in r2["category_breakdown"]:
            d = r2["category_breakdown"][cat] - r1["category_breakdown"][cat]
            print(f"  {cat}: {d:+.1f}")

compare(sys.argv[1], sys.argv[2])
```

```bash
python compare_runs.py baseline_v1.json after_prompt_fix_v2.json
```

### Near-Term (Next 2 Weeks)

**3. Expand to 20 Test Cases**

Five test cases is your MVP. Twenty is where patterns emerge. Add:
- Edge cases (empty input, very long input, off-topic input)
- Adversarial cases (prompt injection attempts, contradictory requests)
- Domain-specific cases unique to your GIS tools

**4. Add a Second Dimension of Scoring**

Currently you're scoring **correctness**. Add **format compliance**:

```python
# Additional judge call for format
FORMAT_CRITERIA = {
    "appropriate_length": "Response is neither too terse nor padded",
    "no_hallucinated_code": "Any code examples are syntactically valid",
    "appropriate_confidence": "Claims uncertainty when appropriate"
}
```

**5. Integrate Into Your Git Workflow**

```bash
# Add to .gitignore (keep eval results local, or commit selectively)
eval_results_*.json

# But DO commit:
# - eval_your_tool.py
# - baseline_v1.json (your committed baseline)
```

### Long-Term (Your Build Pillar Post)

This exercise is the foundation of a direct Build pillar post:

**"How I Added Evals to My GIS AI Tools"**

Your post structure, based on what you just built:

```
1. The problem: I was shipping prompts without measuring anything
2. What evals are (and aren't): Not unit tests — semantic scoring
3. The LLM-as-judge pattern: Why Haiku scores Opus responses
4. My 5 test cases: What I chose and why
5. My baseline score: [Your actual number]%
6. What the score revealed: [Your actual weak category]
7. The prompt fix: What I changed
8. The improvement: Before/after delta
9. Where I'm taking this: 20 test cases, CI integration
```

**That's a post that no one else can write** — it has your real numbers, your real tool, your real discoveries.

---

### Reference: Quick-Start Template

If you want to skip the tutorial and adapt the full file directly, here's the minimal working template:

```python
# MINIMAL EVAL TEMPLATE
# Replace ALL_CAPS values with your specifics

import anthropic, json, os, time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TEST_CASES = [
    {"id": "TC001", "input": "YOUR INPUT 1", "expected_behavior": "WHAT GOOD LOOKS LIKE", "must_include": [], "must_avoid": [], "category": "CATEGORY"},
    # ... 4 more
]

def run_tool(user_input):
    # YOUR TOOL LOGIC HERE
    pass

def score_and_run():
    scores = []
    for tc in TEST_CASES:
        response = run_tool(tc["input"])
        judge = client.messages.create(
            model="claude-haiku-4-5", max_tokens=256,
            messages=[{"role": "user", "content": f"Score 1-5:\nInput: {tc['input']}\nResponse: {response}\nCriteria: {tc['expected_behavior']}\nReturn JSON: {{\"score\": N, \"reason\": \"...\"}}"}]
        )
        result = json.loads(judge.content[0].text)
        scores.append(result["score"])
        print(f"{tc['id']}: {result['score']}/5 — {result['reason'][:80]}")
        time.sleep(0.5)
    
    avg = sum(scores)/len(scores)
    print(f"\nBASELINE: {avg:.1f}/5 ({avg/5*100:.0f}%)")
    json.dump({"scores": scores, "average": avg, "date": datetime.now().isoformat()}, open("baseline.json","w"))

if __name__ == "__main__":
    score_and_run()
```

---

> **Remember:** The point of a baseline isn't to feel good or bad about your current score. It's to have a number you can improve against. A 60% baseline that becomes 85% after two prompt iterations is a compelling story — both for your own growth and for your Build pillar content. Start messy, measure honestly, iterate deliberately.