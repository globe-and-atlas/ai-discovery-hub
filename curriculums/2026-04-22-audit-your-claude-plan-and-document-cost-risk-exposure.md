# Audit Your Claude Plan and Document Cost-Risk Exposure

## A Practical Guide to Pricing Risk Assessment for AI-Dependent Workflows

---

## 1. Introduction & Context

### What This Is

This exercise walks you through a structured audit of your current Claude subscription plan, maps your actual usage patterns against plan features, and produces a one-page **Cost-Risk Exposure Summary** — a professional document that quantifies what Anthropic's pricing shifts mean for your workflow.

### Why It Matters Right Now

In early 2025, Anthropic confirmed it is testing the removal of Claude Code from the **$20/month Pro plan** for approximately 2% of new users. While existing Pro and Max subscribers are currently unaffected, this signal is significant:

- **Pricing restructures rarely reverse.** Test removals almost always become permanent policy.
- **Claude Code is a CLI-first development tool.** If you rely on it for coding sessions, token-heavy tool use, or agentic tasks, losing Pro-tier access means either paying more or rebuilding your workflow.
- **Budget planning requires lead time.** Organizations and freelancers alike need weeks or months to absorb cost increases.

### What You'll Produce

By the end of this exercise, you'll have:

1. ✅ A screenshot-backed record of your current plan features
2. ✅ A feature dependency map of your Claude Code usage
3. ✅ A monthly cost projection under multiple pricing scenarios
4. ✅ A **one-page Risk Summary** ready to use as editorial raw material or a stakeholder briefing

> **Why this doubles as editorial material:** Documenting your own experience with a tool's pricing shift — with receipts — is the foundation of a credible "Tool Critic" piece. Personal, specific, and financially grounded analysis is far more compelling than generic hot takes.

---

## 2. Prerequisites

### Accounts & Access

- [ ] An active Claude account (Pro, Max, or Team tier) at [claude.ai](https://claude.ai)
- [ ] Access to [claude.com/pricing](https://claude.com/pricing) (no login required to view)
- [ ] Billing history access in your Claude account settings

### Tools You'll Need

- [ ] A screenshot tool (OS built-in is fine: `Cmd+Shift+4` on Mac, `Win+Shift+S` on Windows)
- [ ] A text editor or document tool (Markdown editor, Notion, Google Docs, or plain `.md` file)
- [ ] A spreadsheet (Google Sheets, Excel, or even a Markdown table)
- [ ] Optional: A terminal where you've used Claude Code CLI

### Knowledge Prerequisites

- [ ] Basic understanding of what Claude Code does (CLI-based AI coding assistant)
- [ ] Rough awareness of your monthly Claude usage habits
- [ ] No coding expertise required — this is a documentation and analysis exercise

### Time Required

> **Estimated effort: 45–90 minutes** (low effort, high return)

---

## 3. Step-by-Step Guide

---

### Step 1: Screenshot and Archive Your Current Plan

**Goal:** Create a timestamped record of what your plan currently includes. This protects you if features are quietly removed.

#### 1a. Capture the Public Pricing Page

1. Open [claude.com/pricing](https://claude.com/pricing) in your browser
2. Take a **full-page screenshot** (not just the visible viewport)

   ```
   # Mac (full page in browser):
   Open DevTools → Cmd+Shift+P → type "screenshot" → "Capture full size screenshot"

   # Firefox:
   Right-click page → "Take Screenshot" → "Save full page"

   # Chrome Extension option:
   GoFullPage extension → single click for full-page capture
   ```

3. Name the file with today's date:
   ```
   claude_pricing_page_YYYY-MM-DD.png
   ```

4. Note the **exact features listed** for each tier in a quick table:

```markdown
## Pricing Page Capture — [DATE]

| Feature                  | Pro ($20) | Max ($100) | Team |
|--------------------------|-----------|------------|------|
| Claude Code access       | ???       | ✅         | ✅   |
| Monthly token limit      |           |            |      |
| Tool use / function call |           |            |      |
| Priority access          |           |            |      |
| API access included      |           |            |      |
| Claude.ai web interface  |           |            |      |
```

> ⚠️ **Critical:** Fill this table in from the actual page you see today. The Pro column is the one to watch most carefully.

#### 1b. Capture Your Account's Billing Page

1. Log in to [claude.ai](https://claude.ai)
2. Navigate to: **Settings → Billing** (or **Settings → Plans**)
3. Screenshot:
   - Your current plan name and price
   - Your billing cycle date
   - Any usage meters or limits shown
4. Name it: `claude_my_plan_YYYY-MM-DD.png`

---

### Step 2: Map Your Claude Code Feature Dependencies

**Goal:** Identify exactly which Claude Code capabilities your workflow depends on, so you can assess substitutability and cost impact.

#### 2a. Run a CLI Usage Audit

If you've used Claude Code in the terminal, check your shell history:

```bash
# Bash
grep -i "claude" ~/.bash_history | sort | uniq -c | sort -rn | head -30

# Zsh
grep -i "claude" ~/.zsh_history | sort | uniq -c | sort -rn | head -30

# Fish
grep -i "claude" ~/.local/share/fish/fish_history | head -40
```

Also check for Claude Code config files:

```bash
# Look for Claude Code configuration
ls ~/.claude*
cat ~/.claude/config.json 2>/dev/null || echo "No config found"

# Check for any project-level Claude config
find ~/projects -name ".claude*" -maxdepth 3 2>/dev/null
```

#### 2b. Fill Out Your Dependency Map

Copy and complete this template in your document:

```markdown
## My Claude Code Dependency Map — [DATE]

### Session Usage Patterns
- Average CLI sessions per week: ___
- Typical session length (minutes): ___
- Longest single session I can recall: ___

### Primary Use Cases (rank by frequency)
- [ ] Code generation (new features, boilerplate)
- [ ] Code review and refactoring
- [ ] Debugging and error analysis
- [ ] Documentation generation
- [ ] Test writing
- [ ] Architecture/design discussion
- [ ] Data analysis or scripting
- [ ] Other: _______________

### Token-Heavy Workflows
List the tasks that consume the most tokens (large file reads,
long context sessions, multi-file projects):

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Tool Use Dependencies
Does your workflow rely on Claude Code's tool/function calling?
- [ ] File system reads (reading entire codebases)
- [ ] Web search integration
- [ ] Code execution / sandboxed runs
- [ ] Multi-step agentic tasks
- [ ] Shell command execution
- [ ] Other: _______________

### Integration Points
Where does Claude Code touch the rest of your stack?
- [ ] Git workflow (commit messages, PR descriptions)
- [ ] CI/CD pipeline
- [ ] Local dev environment only
- [ ] Shared team environment
- [ ] Scripted/automated (non-interactive)
```

---

### Step 3: Calculate Your Cost Scenarios

**Goal:** Produce hard numbers for what this pricing shift costs you.

#### 3a. Establish Your Baseline

```markdown
## Current Cost Baseline

Current plan: Claude Pro
Current monthly cost: $20.00
Billing date: [DAY] of each month
Payment method: [Card ending in ____]
```

#### 3b. Build Your Scenario Table

Use this spreadsheet-style table (copy into Google Sheets or a `.csv`):

```markdown
## Cost Scenario Analysis

| Scenario | Plan Required | Monthly Cost | Annual Cost | Delta vs. Today |
|----------|--------------|--------------|-------------|-----------------|
| Status quo (Pro, Claude Code stays) | Pro | $20 | $240 | $0 |
| Claude Code moves to Max only | Max | $100 | $1,200 | +$80/mo (+$960/yr) |
| Claude Code moves to Team tier | Team (per seat) | $30/seat | $360 | +$10/mo (+$120/yr) |
| Claude Code via API only (no plan) | API pay-per-use | Variable | Variable | Unknown |
| Switch to competitor (Cursor, Copilot) | Cursor Pro | $20 | $240 | $0 (migration cost) |
| Switch to Copilot Individual | GitHub Copilot | $10 | $120 | -$10/mo (-$120/yr) |
```

> **Fill in current prices from the pricing page you just screenshotted.** Prices above are illustrative — verify actuals.

#### 3c. Estimate Your API-Only Cost (if applicable)

If Claude Code moves to API-only access, estimate your token consumption:

```markdown
## API Cost Estimation (if applicable)

### Input tokens per month estimate:
- Average tokens per prompt: ~___
- Prompts per session: ~___
- Sessions per week: ~___
- Weeks per month: 4.3
- Monthly input tokens: ___ × ___ × ___ × 4.3 = ___

### Output tokens per month estimate:
- Average response length (tokens): ~___
- Responses per month: ___
- Monthly output tokens: ___

### Claude 3.5 Sonnet API Pricing (verify current rates):
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

### Monthly API Cost Estimate:
Input cost:  (___ input tokens / 1,000,000)  × $3.00  = $___
Output cost: (___ output tokens / 1,000,000) × $15.00 = $___
Total estimated API cost: $___/month
```

---

### Step 4: Assess Substitution Options

**Goal:** Know your alternatives before you need them.

```markdown
## Substitution Analysis

### Option 1: Upgrade to Claude Max
- Cost increase: +$80/month
- Feature gain: [list from pricing page]
- Migration effort: Zero (same tool)
- Risk: Anthropic raises Max pricing too
- Verdict: [YOUR ASSESSMENT]

### Option 2: Cursor IDE
- Cost: $20/month (Pro) or free tier
- What it replicates: In-editor AI coding, multi-file context
- What it misses: Terminal-native workflow, Claude's specific reasoning
- Migration effort: Medium (IDE change, habit shift)
- Verdict: [YOUR ASSESSMENT]

### Option 3: GitHub Copilot
- Cost: $10/month individual
- What it replicates: Code completion, chat
- What it misses: Long-context sessions, agentic tool use
- Migration effort: Low (VS Code extension)
- Verdict: [YOUR ASSESSMENT]

### Option 4: Direct API + Custom Scripts
- Cost: Variable (see calculation above)
- What it replicates: Full Claude access, customizable
- What it misses: Convenience of Claude Code UX
- Migration effort: High (build your own tooling)
- Verdict: [YOUR ASSESSMENT]

### Option 5: Aider (open source CLI)
- Cost: Free (bring your own API key)
- What it replicates: CLI-based AI coding
- What it misses: Claude Code's specific feature set
- Migration effort: Medium
- Verdict: [YOUR ASSESSMENT]
```

---

### Step 5: Write Your One-Page Risk Summary

**Goal:** Produce a clean, shareable document that captures everything above in executive-summary format.

Copy this template and fill it in:

```markdown
---
# Claude Code Cost-Risk Exposure Summary
**Prepared by:** [Your Name]
**Date:** [DATE]
**Document type:** Personal risk assessment / editorial raw material

---

## The Signal
Anthropic confirmed (via Reddit r/ClaudeAI, [DATE]) that Claude Code
is being tested for removal from the $20/month Pro plan for ~2% of
new users. Existing subscribers are unaffected *for now*.

**Source:** https://www.reddit.com/r/ClaudeAI/comments/1srzhd7/

---

## My Current Exposure

| Item | Detail |
|------|--------|
| Current plan | Claude Pro — $20/month |
| Claude Code usage | [X sessions/week, primary coding tool] |
| Key workflows at risk | [list your top 3 from Step 2] |
| Monthly token estimate | ~[X]M tokens input / [X]M tokens output |

---

## Financial Impact Scenarios

| Scenario | Monthly Impact | Annual Impact |
|----------|---------------|---------------|
| No change (best case) | $0 | $0 |
| Upgrade to Max required | +$80/mo | +$960/yr |
| API-only fallback | ~$___/mo | ~$___/yr |
| Switch to Cursor Pro | $0 delta | $0 (migration cost: ~[X hrs]) |

**Worst-case scenario:** $[___]/year additional cost, or [X] hours
of migration work to rebuild workflow on an alternative.

---

## Risk Assessment

**Likelihood of pricing change:** High
*Rationale: Controlled tests of feature removal rarely reverse.
The 2% test is a pre-announcement, not an experiment.*

**Timeline:** Unknown, but likely within 1–2 billing cycles for
new users; existing users may have 3–6 months.

**Workflow disruption level:** [Low / Medium / High]
*Rationale: [1–2 sentences on how central Claude Code is to
your daily development work]*

---

## Recommended Actions

**Immediate (this week):**
- [x] Screenshot current plan features (done — see attachments)
- [ ] Set a calendar alert for next billing cycle to recheck plan page
- [ ] Download/export any Claude conversation history worth keeping

**Short-term (next 30 days):**
- [ ] Test one alternative tool for [your top use case]
- [ ] Calculate actual API token usage if API-only becomes necessary
- [ ] Evaluate whether Max plan features justify cost for your workflow

**If pricing changes:**
- Primary pivot: [Your preferred alternative]
- Secondary pivot: [Backup option]
- Hard limit: Will not pay more than $[___]/month for AI coding tools

---

## Editorial Angles (for Tool Critic piece)

*Raw material — unpolished observations:*

1. **The quiet deprecation pattern:** No email, no announcement —
   a Reddit PSA. What does this say about Anthropic's relationship
   with power users?

2. **The $20 → $100 jump:** There's no middle tier. This is a
   deliberate pricing gap, not an accident.

3. **"Existing subscribers unaffected for now"** — the "for now"
   is doing a lot of work in that sentence.

4. **Claude Code as a loss leader:** Was it always meant to graduate
   to a higher tier once adoption was established?

5. **Personal data point:** I use Claude Code [X times/week] for
   [specific workflows]. At $100/month, my ROI calculation is [___].

---

## Attachments
- [ ] `claude_pricing_page_YYYY-MM-DD.png`
- [ ] `claude_my_plan_YYYY-MM-DD.png`
- [ ] Cost scenario spreadsheet

---
*This document was created as part of a proactive pricing risk
audit. Update monthly until Anthropic makes a public announcement.*
```

---

### Step 6: Set Up a Monitoring Trigger

**Goal:** Don't get caught off-guard. Automate awareness.

#### Option A: Simple Calendar Reminder

```
Create a recurring monthly calendar event:
Title: "Check Claude Pricing Page + Plan Features"
Date: [Your billing date - 5 days]
Notes: Visit claude.com/pricing and compare to archived screenshot.
       Check r/ClaudeAI for announcements.
```

#### Option B: RSS/Reddit Monitoring

Set up a feed for r/ClaudeAI announcements:

```
RSS feed for r/ClaudeAI:
https://www.reddit.com/r/ClaudeAI/.rss

Add this to your RSS reader (Feedly, NetNewsWire, etc.)
Filter for keywords: "pricing", "Claude Code", "Pro plan", "billing"
```

#### Option C: Wayback Machine Baseline

```bash
# Submit the pricing page to the Wayback Machine for archival
curl -s "https://web.archive.org/save/https://claude.com/pricing"

# Note the archived URL returned — save it in your risk document
# Example: https://web.archive.org/web/20250101000000/https://claude.com/pricing
```

---

## 4. Validation

### How to Know You've Completed This Successfully

Work through this checklist:

```markdown
## Completion Checklist

### Documentation Artifacts
- [ ] Full-page screenshot of claude.com/pricing saved with date in filename
- [ ] Screenshot of your account billing/plan page saved with date in filename
- [ ] Feature comparison table filled in from actual pricing page
- [ ] Dependency map completed with honest usage estimates

### Financial Analysis
- [ ] At least 3 cost scenarios calculated with real numbers
- [ ] API cost estimate completed (even if rough)
- [ ] At least 2 alternative tools assessed with real pricing

### Risk Summary
- [ ] One-page summary document completed (all sections filled)
- [ ] Editorial angles section has at least 3 specific observations
- [ ] Recommended actions are specific, not generic
- [ ] Document is saved somewhere you'll find it in 3 months

### Monitoring
- [ ] At least one monitoring trigger is set up
  (calendar alert, RSS feed, or Wayback Machine archive)

### Gut Check
- [ ] Could you hand this document to a colleague and have them
      understand your exposure in under 5 minutes?
- [ ] Do the numbers in the document reflect reality, not wishful thinking?
- [ ] Have you been honest about how much you actually use Claude Code?
```

### Quality Bar for the Risk Summary

Your one-page summary is complete when it answers these questions without requiring the reader to ask follow-up questions:

1. **What happened?** (The pricing signal)
2. **What do I currently use?** (Dependency map)
3. **What does it cost me if things change?** (Scenarios with numbers)
4. **What are my options?** (Substitution analysis)
5. **What am I going to do about it?** (Actions)

---

## 5. Next Steps

### Immediate Follow-Ups

**Turn This Into Editorial Content**

Your risk summary is the skeleton of a "Tool Critic" piece. The next step is to add voice and argument:

```markdown
## From Risk Summary → Tool Critic Piece

Your risk document has the facts. Now add:

1. **A provocative headline:**
   Draft 3 options, e.g.:
   - "Anthropic Is Testing Whether You'll Pay 5x More for Claude Code"
   - "The $20 AI Developer Dream Is Ending"
   - "Claude Code's Quiet Graduation to the Premium Tier"

2. **Your personal stake (the lede):**
   Start with the moment you noticed something changed.
   Specific > generic. "$80/month" > "a significant price increase."

3. **The broader pattern:**
   Is this unique to Anthropic? Compare to GitHub Copilot's launch,
   OpenAI's GPT-4 gating, or Cursor's pricing tiers.

4. **A clear verdict:**
   Is this fair? Predatory? Inevitable? What would make it acceptable?
```

### Deeper Skill-Building

**Learn to Do This for Every Tool in Your Stack**

This pricing audit methodology applies to any SaaS tool:

```markdown
## Apply to Your Full Stack

Repeat Steps 1–5 for:
- [ ] GitHub Copilot (if you use it)
- [ ] Cursor / Windsurf / other AI IDEs
- [ ] OpenAI API usage
- [ ] Any other AI tools with usage-based or tier-based pricing

Create a "Stack Risk Dashboard" — a single spreadsheet with
one row per tool showing current cost, worst-case cost, and
your migration option.
```

**Learn Token Economics**

Understanding token pricing makes you a better AI tool buyer:

- Read Anthropic's [model pricing page](https://anthropic.com/pricing)
- Learn to estimate token counts: ~1 token ≈ 4 characters in English
- Use the [Anthropic Tokenizer](https://lunary.ai/anthropic-tokenizer) to measure real prompts

### Build a "Pricing Hygiene" Practice

```markdown
## Monthly Pricing Hygiene Routine (15 minutes/month)

1. Check your billing statement — did anything change?
2. Visit pricing pages for your top 3 AI tools
3. Compare to last month's screenshot
4. Check r/ClaudeAI, r/cursor, Hacker News for pricing news
5. Update your Stack Risk Dashboard
6. If anything changed: update your risk document

Time investment: 15 minutes/month
Protection: Weeks of advance warning before budget surprises
```

### Resources for Ongoing Monitoring

| Resource | What to Watch For |
|----------|------------------|
| [r/ClaudeAI](https://reddit.com/r/ClaudeAI) | Pricing changes, feature announcements |
| [Anthropic's blog](https://anthropic.com/news) | Official announcements |
| [Hacker News](https://news.ycombinator.com) | Search "Anthropic pricing" |
| [claude.com/pricing](https://claude.com/pricing) | Monthly screenshot comparison |
| Your email inbox | Filter for "Anthropic" billing notifications |

---

## Summary

You've just completed a discipline that most developers skip until it's too late: **proactive vendor risk assessment**. The artifact you've created — a dated, screenshot-backed, financially grounded risk summary — is both a personal planning tool and the foundation of credible public analysis.

The skill generalizes. Every AI tool in your stack is a pricing decision that someone else controls. The developers who navigate these changes best aren't the ones who react fastest — they're the ones who saw it coming and already knew their options.

> **Keep this document.** In six months, it will either confirm you planned well or explain exactly what you should have done differently. Either way, it's more useful than anything you could have written after the fact.

---

*Last exercise update: 2025 | Source signal: r/ClaudeAI — Claude Code removed from Pro plan test*