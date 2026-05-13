# Audit Your Claude Code Plan & Document Current Usage

## A Practical Guide for GIS Practitioners & Power Users

---

## 1. Introduction & Context

### What's Happening and Why It Matters

Anthropic has quietly begun removing **Claude Code** from the $20/month Pro plan listing. While currently confirmed as an A/B test affecting approximately 2% of new signups, this signal carries significant weight: Anthropic may be repositioning Claude Code as a premium, higher-cost feature — potentially behind a more expensive tier like Claude Max ($100+/month) or an enterprise plan.

**For GIS practitioners and spatial analysts**, this isn't just a billing footnote. Claude Code's CLI (Command Line Interface) has become a genuine productivity multiplier for:

- Automating GDAL/OGR workflows
- Writing Python scripts for GeoPandas, Shapely, and Rasterio
- Generating and debugging QGIS plugins
- Processing large geospatial datasets with scripted pipelines
- Iterating rapidly on PostGIS queries

If Claude Code moves behind a paywall tier you aren't currently on, your **daily dev stack changes overnight** — and so does your cost model for recommending tools to others.

This exercise has two purposes:
1. **Practical self-audit** — Know exactly what you have before it changes
2. **Content creation** — Turn this moment of uncertainty into a ready-to-publish "Tool Critic" note for your audience

> **The best time to document your tooling baseline is before it changes, not after.**

---

## 2. Prerequisites

Before starting this exercise, confirm you have the following:

### Accounts & Access
- [ ] An active Claude account (free, Pro, or higher tier) at [claude.ai](https://claude.ai)
- [ ] Access to [claude.com/pricing](https://claude.com/pricing)
- [ ] A text editor or notes app (Notion, Obsidian, VS Code, or plain `.md` file)

### Tools
- [ ] A screenshot tool:
  - **macOS**: `Cmd + Shift + 4` (area) or `Cmd + Shift + 3` (full screen)
  - **Windows**: `Win + Shift + S` (Snipping Tool) or `PrtScn`
  - **Linux**: `gnome-screenshot`, `flameshot`, or `scrot`
- [ ] Optional but recommended: Claude Code CLI installed locally

### Check if Claude Code CLI is installed:
```bash
# Run this in your terminal
claude --version
```

```bash
# Expected output (if installed):
claude 0.2.x  # version number will vary

# If not installed:
# command not found: claude
```

### Knowledge Level
- Basic familiarity with SaaS subscription tiers
- Comfortable with terminal/command line (for the CLI verification steps)
- No coding expertise required for the core audit task

---

## 3. Step-by-Step Guide

---

### Step 1: Capture Your Current Plan Status (5 minutes)

#### 1a. Visit the Pricing Page

Navigate to: **https://claude.com/pricing**

Take a screenshot of the **full pricing comparison table**. Save it as:
```
claude-pricing-audit-YYYY-MM-DD.png
```

> **Why this matters:** This page is actively being A/B tested. Your screenshot is a timestamped record of what Anthropic is showing you specifically — a data point, not just a reference image.

#### 1b. Check Your Active Subscription

1. Log into [claude.ai](https://claude.ai)
2. Click your **profile avatar** (bottom-left corner)
3. Navigate to **Settings → Account** or **Billing**
4. Screenshot the page showing your current plan name, billing cycle, and renewal date

Save as:
```
claude-account-plan-YYYY-MM-DD.png
```

#### 1c. Document What You See in a Structured Note

Open your text editor and create a new file: `claude-audit-YYYY-MM-DD.md`

Paste and fill in this template:

```markdown
# Claude Plan Audit
**Date:** YYYY-MM-DD
**Audited by:** [Your name]

## Current Subscription
- Plan tier: [Free / Pro / Max / Team / Enterprise]
- Monthly cost: $[X]/month
- Billing cycle: [Monthly / Annual]
- Next renewal: [Date]

## Claude Code — What the Pricing Page Shows
- Is Claude Code listed under my current plan? [Yes / No / Not clearly stated]
- What tier does the pricing page show Claude Code under? [Pro / Max / Team / Not listed]
- Any asterisks, footnotes, or caveats visible? [Yes/No — describe if yes]

## Claude Code — What I Actually Have Access To
- Can I access Claude Code from the claude.ai web interface? [Yes / No]
- Is Claude Code CLI working on my machine? [Yes / No / Not installed]

## Raw Notes
[Any other observations — UI changes, missing features, confusing language]
```

---

### Step 2: Verify CLI Access (5 minutes)

Even if the pricing page doesn't list Claude Code clearly, your **existing access may be unaffected** (per Anthropic's confirmation that the A/B test targets new signups, not existing subscribers).

Run these CLI checks:

```bash
# Check version and confirm installation
claude --version

# Confirm authentication status
claude auth status
```

```bash
# Expected output if authenticated:
# Logged in as: your@email.com
# Plan: Pro (or whatever your plan is)
```

```bash
# Run a minimal test to confirm Claude Code is functional
# Navigate to any project directory first
cd ~/your-gis-project

# Start Claude Code
claude
```

Once inside Claude Code, run a quick smoke test with a GIS-relevant prompt:

```
> Write a one-line Python command using GDAL to list all layers in a GeoPackage file.
```

**Expected response** — Claude Code should return something like:

```python
python -c "from osgeo import ogr; ds = ogr.Open('your_file.gpkg'); [print(ds.GetLayerByIndex(i).GetName()) for i in range(ds.GetLayerCount())]"
```

If this works: **your CLI access is confirmed active**, regardless of what the pricing page says.

Screenshot or copy-paste this terminal session and save it as evidence:
```
claude-cli-access-verified-YYYY-MM-DD.txt
```

---

### Step 3: Write Your Tool Critic Note (15–20 minutes)

This is the content creation payoff. You're writing a **200-word "Tool Critic" note** — a short, opinionated, practitioner-focused piece for your *Globe & Atlas* audience.

#### What is a Tool Critic Note?

A Tool Critic note is **not** a full review. It's a rapid, honest take on a specific tool change or signal — written for someone who trusts your judgment and wants the 30-second version of "should I care about this?"

#### The Formula

Use this structure (each section ≈ 40–50 words):

```
1. THE SIGNAL     — What just happened, factually
2. THE CONTEXT    — Why it matters for GIS practitioners specifically
3. THE RISK       — What you might lose if this change goes permanent
4. THE MOVE       — What you should do right now
5. THE VERDICT    — Your honest one-sentence recommendation
```

#### Starter Draft Template

```markdown
---
title: "Tool Critic: Claude Code's Uncertain Future on the Pro Plan"
category: Tool Critic
date: YYYY-MM-DD
author: [Your name]
word_count: ~200
---

**THE SIGNAL**
Anthropic has quietly removed Claude Code from the $20 Pro plan
listing — confirmed as an A/B test on new signups (~2% of users),
not a retroactive change. But A/B tests that stick become policy.

**THE CONTEXT**
For GIS practitioners scripting GDAL workflows, building QGIS plugins,
or automating spatial data pipelines, Claude Code CLI isn't a novelty —
it's a daily driver. Losing it from the $20 tier would mean paying $100+/month
(Claude Max) to maintain the same workflow.

**THE RISK**
Budget-conscious practitioners — freelancers, academics, small consultancies —
would face a hard choice: absorb a 5x price increase, switch to alternatives
(GitHub Copilot, Cursor, Aider), or lose CLI-level AI assistance entirely.

**THE MOVE**
Log into claude.com/pricing today. Screenshot your plan. Confirm CLI access
still works. If you're a Pro subscriber, your access is currently protected —
but document your baseline now, before the rules change.

**THE VERDICT**
Claude Code remains the best AI pair-programmer for spatial Python workflows,
but Anthropic just reminded us: no feature is safe at the $20 tier.
Watch this space closely.
```

#### Polish Checklist Before Publishing

- [ ] Word count is 180–220 words
- [ ] At least one specific GIS use case mentioned
- [ ] A clear, actionable recommendation in "The Move" section
- [ ] No vendor cheerleading — honest about the uncertainty
- [ ] Date is current (this signal ages quickly)

---

### Step 4: Organize Your Audit Package (5 minutes)

Create a folder to keep everything together:

```bash
mkdir -p ~/tool-audits/claude-code-YYYY-MM-DD
```

Move your files into it:

```bash
mv claude-pricing-audit-YYYY-MM-DD.png ~/tool-audits/claude-code-YYYY-MM-DD/
mv claude-account-plan-YYYY-MM-DD.png ~/tool-audits/claude-code-YYYY-MM-DD/
mv claude-audit-YYYY-MM-DD.md ~/tool-audits/claude-code-YYYY-MM-DD/
mv claude-cli-access-verified-YYYY-MM-DD.txt ~/tool-audits/claude-code-YYYY-MM-DD/
```

Your folder should look like this:

```
claude-code-YYYY-MM-DD/
├── claude-pricing-audit-YYYY-MM-DD.png     ← Pricing page screenshot
├── claude-account-plan-YYYY-MM-DD.png      ← Your account/billing screenshot
├── claude-audit-YYYY-MM-DD.md              ← Structured audit notes
├── claude-cli-access-verified-YYYY-MM-DD.txt ← CLI smoke test output
└── tool-critic-note-YYYY-MM-DD.md          ← Ready-to-publish content
```

---

## 4. Validation

### How to Know You've Completed This Exercise Successfully

Work through this checklist:

#### Documentation ✅
- [ ] **Pricing page screenshot saved** — timestamped, shows the current plan comparison table
- [ ] **Account billing screenshot saved** — shows your exact plan tier and renewal date
- [ ] **Structured audit note completed** — all fields filled in, no blank lines left
- [ ] **CLI smoke test documented** — either confirms working access or documents failure

#### Content ✅
- [ ] **Tool Critic note is 180–220 words** (use your editor's word count)
- [ ] **Follows the 5-section formula** (Signal / Context / Risk / Move / Verdict)
- [ ] **Mentions at least one concrete GIS use case**
- [ ] **Contains a clear, actionable recommendation**
- [ ] **You would actually publish this** — it passes your own editorial bar

#### Mindset Check ✅
Ask yourself: *"If Claude Code disappeared from the Pro tier tomorrow, would I know exactly what I'm losing and what my alternatives are?"*

If the answer is **yes** after completing this exercise — you've done it right.

---

### Quick Self-Test

Answer these questions from memory after completing the exercise:

```
1. What is your exact plan tier and monthly cost?
   Answer: ________________

2. Is Claude Code currently listed on your plan's pricing page feature list?
   Answer: ________________

3. Does your CLI work right now, regardless of the pricing page?
   Answer: ________________

4. What is the one action you recommended in your Tool Critic note?
   Answer: ________________
```

If you can answer all four without looking — your audit is solid.

---

## 5. Next Steps

### Immediate (This Week)

**Set a calendar reminder** for 30 days from today to re-audit the pricing page. A/B tests that affect even 2% of users are often harbingers of broader rollouts. Catching the change early gives you time to act, not react.

```
Reminder title: "Re-audit Claude Code pricing — is A/B test now policy?"
Date: [Today + 30 days]
```

**Share your Tool Critic note.** This is ready-to-publish content. Post it to Globe & Atlas, LinkedIn, or your practitioner community. Your audience is facing the same uncertainty — your documented perspective has real value.

---

### Short Term (Next 30 Days)

**Explore your fallback options.** If Claude Code moves to a higher tier, you'll want a tested alternative in your back pocket — not something you're learning under pressure. Consider a one-hour trial of:

| Tool | Best For | GIS Relevance |
|---|---|---|
| **Cursor** | IDE-integrated AI coding | Strong Python/GeoPandas support |
| **Aider** | CLI-based AI pair programming | Direct Claude Code alternative |
| **GitHub Copilot** | In-editor autocomplete | QGIS plugin development |
| **Continue.dev** | VS Code/JetBrains plugin | Open-source, local model option |

**Audit your Claude Code usage patterns.** Before the pricing changes, document *how often* and *for what tasks* you actually use Claude Code CLI. This quantified usage makes the "is it worth $100/month?" decision rational, not emotional.

---

### Long Term (Ongoing)

**Build a "Tool Signal" habit.** This exercise isn't a one-time event — it's a template. Pricing changes, feature deprecations, and API policy shifts are a permanent feature of the AI tooling landscape. A quarterly tool audit (30 minutes, same format) keeps you ahead of disruption.

**Contribute back to the community.** When Anthropic does clarify their pricing (official announcement, not just Reddit PSA), publish a follow-up Tool Critic note. The "before and after" pair becomes a genuinely useful resource for GIS practitioners making tooling decisions.

---

### Further Reading & Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code) — Official CLI docs
- [Anthropic Pricing Page](https://claude.com/pricing) — Bookmark and revisit monthly
- [r/ClaudeAI](https://reddit.com/r/ClaudeAI) — Community signal detection for pricing/feature changes
- [GDAL Python Cookbook](https://pcjericks.github.io/py-gdalogr-cookbook/) — Reference for GIS automation use cases where Claude Code adds the most value

---

> **Remember:** The goal of this audit isn't anxiety — it's agency. When you know exactly what you have, what it costs, and what your alternatives are, pricing changes become decisions you make, not disruptions that happen to you.