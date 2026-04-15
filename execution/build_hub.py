import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import google.generativeai as genai

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Model Backend Selection (Transparent)
DEFAULT_MODEL = os.getenv("HUB_MODEL", "claude-3-5-sonnet-latest")
DEFAULT_PROVIDER = os.getenv("HUB_PROVIDER", "anthropic")

def get_client():
    """Returns the appropriate LLM client based on environment config."""
    provider = os.getenv("HUB_PROVIDER", "anthropic")
    if provider == "anthropic":
        return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "gemini":
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return genai.GenerativeModel(os.getenv("HUB_MODEL", "gemini-1.5-pro"))
    raise ValueError(f"Provider {provider} not implemented yet.")

def generate_hub_content(data):
    """
    Consolidated prompt engine that sends mixed signal data to the LLM.
    Returns structured JSON for the dashboard.
    """
    provider = os.getenv("HUB_PROVIDER", "anthropic")
    model_name = os.getenv("HUB_MODEL", "claude-3-5-sonnet-latest")
    
    # Import unified prompt
    sys.path.insert(0, str(Path(__file__).parent))
    from prompts import build_hub_prompt
    
    prompt = build_hub_prompt(data)

    print(f"Calling {provider} ({model_name})...")
    
    if provider == "anthropic":
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model_name,
            max_tokens=7000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text
    elif provider == "gemini":
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        text = response.text
    else:
        raise ValueError(f"Provider {provider} not supported.")
    
    # Extract JSON
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)

def render_html(data, duration_map=None):
    """
    Renders the AI Discovery Hub dashboard with two sections:
    - Primary: personally relevant items (direct stack + adjacent)
    - Secondary: AI world at large (awareness only, compact list)
    """
    today = datetime.now().strftime("%B %d, %Y")
    duration_map = duration_map or {}

    artifacts  = data.get('artifacts', [])
    personal   = [a for a in artifacts if a.get('relevance') == 'personal']
    world      = [a for a in artifacts if a.get('relevance') != 'personal']
    n_personal = len(personal)
    n_world    = len(world)
    n_adopt    = sum(1 for a in personal if 'Adopt'  in a['tier'])
    n_watch    = sum(1 for a in personal if 'Watch'  in a['tier'])
    n_radar    = sum(1 for a in personal if 'Radar'  in a['tier'])
    n_adjacent = sum(1 for a in personal if a.get('relevance_why','').lower().startswith('adjacent'))
    n_gis      = sum(1 for a in personal if 'GIS'    in a.get('lens',''))
    n_video    = sum(1 for a in personal if a.get('type') == 'video')
    n_repo     = sum(1 for a in personal if a.get('type') == 'repo')
    n_signal   = sum(1 for a in personal if a.get('type') == 'signal')

    def pct(n, total=None):
        t = total if total is not None else n_personal
        return f"{int(n/t*100)}%" if t else "0%"

    themes_html = "".join([
        f'<span class="tpill tp-{t.get("type","curr")}"><span class="tpill-dot"></span>{t["label"]}</span>'
        for t in data.get('themes', [])
    ])

    bars_html = (
        f'<div class="sig"><div class="sig-icon">🎥</div><div class="sig-lbl">Videos</div>'
        f'<div class="sig-bar-bg"><div class="sig-bar" style="width:{pct(n_video)};background:var(--blue);"></div></div>'
        f'<div class="sig-ct">{n_video}</div></div>'
        f'<div class="sig"><div class="sig-icon">📦</div><div class="sig-lbl">Repos</div>'
        f'<div class="sig-bar-bg"><div class="sig-bar" style="width:{pct(n_repo)};background:var(--purple);"></div></div>'
        f'<div class="sig-ct">{n_repo}</div></div>'
        f'<div class="sig"><div class="sig-icon">📰</div><div class="sig-lbl">Signals</div>'
        f'<div class="sig-bar-bg"><div class="sig-bar" style="width:{pct(n_signal)};background:var(--teal);"></div></div>'
        f'<div class="sig-ct">{n_signal}</div></div>'
        f'<div class="sig"><div class="sig-icon">🔀</div><div class="sig-lbl">Adjacent</div>'
        f'<div class="sig-bar-bg"><div class="sig-bar" style="width:{pct(n_adjacent)};background:var(--orange);"></div></div>'
        f'<div class="sig-ct">{n_adjacent}</div></div>'
        f'<div class="sig"><div class="sig-icon">🗺</div><div class="sig-lbl">GIS picks</div>'
        f'<div class="sig-bar-bg"><div class="sig-bar" style="width:{pct(n_gis)};background:var(--green);"></div></div>'
        f'<div class="sig-ct">{n_gis}</div></div>'
    )

    ms_classes = {'new': 'ms-new', 'watch': 'ms-watch', 'arch': 'ms-arch', 'tool': 'ms-tool', 'infra': 'ms-infra', 'design': 'ms-watch'}
    tracker_html = "".join([
        f'<div class="model-row">'
        f'<div><div class="model-name">{m["name"]}</div><div class="model-co">{m["company"]} · {m["date"]}</div></div>'
        f'<span class="model-status {ms_classes.get(m["status"], "ms-watch")}">{m["status"].upper()}</span>'
        f'</div>'
        for m in data.get('model_tracker', [])
    ])

    effort_cls = {'low': 'e-low', 'med': 'e-med', 'high': 'e-high'}
    lab_html = "".join([
        f'<div class="apply-card">'
        f'<div class="apply-head"><div class="apply-title">{ex["title"]}</div>'
        f'<span class="effort {effort_cls.get(ex["effort"], "e-med")}">{ex["effort"].title()} effort</span></div>'
        f'<div class="apply-desc">{ex["desc"]}</div>'
        f'</div>'
        for ex in data.get('exercises', [])
    ])

    world_rows_html = "".join([
        f'<a class="world-row" href="{a["url"]}" target="_blank" rel="noopener noreferrer">'
        f'<span class="world-icon">{a.get("icon","📦")}</span>'
        f'<span class="world-title">{a["title"]}</span>'
        f'<span class="world-src">{a["source"]} · {a["date"]}</span>'
        f'<span class="world-desc">{a["desc"]}</span>'
        f'</a>'
        for a in world
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Discovery Hub — {today}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #080b12; --bg2: #0e1220; --bg3: #151c2e; --bg4: #1d2540;
    --border: #252e4a; --border2: #36416a; --text: #e6eaf4;
    --text2: #8e9ab8; --text3: #58678e; --blue: #5b8af7;
    --purple: #7c5cfc; --green: #34d89a; --orange: #f97c3c;
    --pink: #f05d9a; --yellow: #f5c842; --teal: #38c9d4; --cyan: #4fd9f5;
    --font-sans: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); font-family:var(--font-sans); padding:26px 28px; line-height:1.5; }}
  .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:22px; padding-bottom:20px; border-bottom:1px solid var(--border); }}
  .h-title {{ font-size:24px; font-weight:900; letter-spacing:-.5px; background:linear-gradient(120deg,#fff 0%,#8e9ab8 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
  .h-sub {{ font-size:12px; color:var(--text3); font-family:var(--font-mono); margin-top:3px; }}
  .stat-row {{ display:grid; grid-template-columns:repeat(6,1fr); gap:10px; margin-bottom:14px; }}
  .sc {{ background:var(--bg2); border:1px solid var(--border); border-radius:11px; padding:13px 14px; text-align:center; transition:.15s; cursor:pointer; }}
  .sc:hover {{ border-color:var(--border2); background:var(--bg3); }}
  .sc-num {{ font-size:28px; font-weight:900; line-height:1; margin-bottom:3px; }}
  .sc-lbl {{ font-size:10px; color:var(--text3); font-weight:500; }}
  .c-blue {{ color:var(--blue); }} .c-green {{ color:var(--green); }} .c-orange {{ color:var(--orange); }}
  .c-yellow {{ color:var(--yellow); }} .c-teal {{ color:var(--teal); }} .c-pink {{ color:var(--pink); }} .c-text3 {{ color:var(--text3); }}
  .section-header {{ display:flex; align-items:center; gap:10px; margin:20px 0 12px; }}
  .section-title {{ font-size:13px; font-weight:800; color:var(--text); }}
  .section-badge {{ font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px; font-family:var(--font-mono); }}
  .sb-personal {{ background:rgba(91,138,247,.12); color:var(--blue); border:1px solid rgba(91,138,247,.3); }}
  .sb-world {{ background:rgba(88,103,142,.12); color:var(--text3); border:1px solid rgba(88,103,142,.3); }}
  .section-line {{ flex:1; height:1px; background:var(--border); }}
  .controls {{ margin-bottom:16px; display:flex; flex-direction:column; gap:8px; }}
  .sort-row {{ display:flex; gap:8px; align-items:center; }}
  .filter-row {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }}
  .row-lbl {{ font-size:9px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; color:var(--text3); font-family:var(--font-mono); width:38px; flex-shrink:0; }}
  .sort-btn, .filter-btn {{ font-size:11px; font-weight:700; padding:4px 12px; border-radius:6px; border:1px solid var(--border); background:var(--bg2); color:var(--text3); cursor:pointer; transition:.2s; position:relative; }}
  .filter-btn[data-tip]:hover::after {{ content:attr(data-tip); position:absolute; bottom:calc(100% + 7px); left:50%; transform:translateX(-50%); background:var(--bg4); border:1px solid var(--border2); color:var(--text2); font-size:10.5px; font-weight:400; line-height:1.45; padding:7px 11px; border-radius:7px; white-space:nowrap; pointer-events:none; z-index:200; font-family:var(--font-sans); box-shadow:0 4px 16px rgba(0,0,0,.4); }}
  .sort-btn.active {{ border-color:var(--blue); color:var(--text); background:rgba(91,138,247,.1); }}
  .filter-btn.active {{ border-color:var(--text3); color:var(--text); background:rgba(255,255,255,.05); }}
  .filter-btn.f-home.active {{ border-color:var(--yellow); color:var(--yellow); background:rgba(245,200,66,.1); }}
  .filter-btn.f-curr.active {{ border-color:var(--blue); color:var(--blue); background:rgba(91,138,247,.1); }}
  .filter-btn.f-gis.active  {{ border-color:var(--green); color:var(--green); background:rgba(52,216,154,.1); }}
  .filter-btn.fb-adopt.active {{ border-color:var(--green); color:var(--green); background:rgba(52,216,154,.1); }}
  .filter-btn.fb-watch.active {{ border-color:var(--blue); color:var(--blue); background:rgba(91,138,247,.1); }}
  .filter-btn.fb-hype.active  {{ border-color:var(--pink); color:var(--pink); background:rgba(240,93,154,.1); }}
  .filter-btn.fb-found.active {{ border-color:var(--yellow); color:var(--yellow); background:rgba(245,200,66,.1); }}
  .filter-btn.fb-radar.active {{ border-color:var(--teal); color:var(--teal); background:rgba(56,201,212,.1); }}
  .hub-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:11px; }}
  .fycard {{ background:rgba(255,255,255,.033); border:1px solid rgba(255,255,255,.07); border-radius:10px; padding:13px; display:flex; flex-direction:column; text-decoration:none; color:inherit; transition:border-color .2s, transform .2s; }}
  .fycard:hover {{ border-color:rgba(245,200,66,.35); transform:translateY(-2px); }}
  .fycard.adjacent {{ border-color:rgba(249,124,60,.18); }}
  .fycard.adjacent:hover {{ border-color:rgba(249,124,60,.55); }}
  .fycard-icon {{ font-size:20px; margin-bottom:7px; }}
  .fycard-title {{ font-size:12.5px; font-weight:700; color:var(--text); margin-bottom:3px; line-height:1.3; }}
  .fycard-src {{ font-size:9.5px; color:var(--text3); font-family:var(--font-mono); margin-bottom:6px; display:flex; align-items:center; gap:6px; }}
  .vid-dur {{ background:rgba(56,201,212,.12); color:var(--teal); border-radius:4px; padding:1px 5px; font-size:9px; font-weight:700; flex-shrink:0; }}
  .fycard-desc {{ font-size:11px; color:var(--text2); line-height:1.5; margin-bottom:6px; flex-grow:1; }}
  .fycard-why {{ font-size:10px; color:var(--orange); font-style:italic; margin-bottom:8px; line-height:1.4; }}
  .tag-row {{ display:flex; flex-wrap:wrap; gap:5px; }}
  .tag {{ padding:2px 7px; border-radius:4px; font-size:9px; font-weight:700; }}
  .t-lens {{ background:rgba(255,255,255,0.05); color:var(--text3); }}
  .t-tier {{ border:1px solid transparent; }}
  .t-adopt {{ color:var(--green); border-color:rgba(52,216,154,.3); }}
  .t-watch {{ color:var(--blue); border-color:rgba(91,138,247,.3); }}
  .t-hype  {{ color:var(--pink); border-color:rgba(240,93,154,.3); }}
  .t-found {{ color:var(--yellow); border-color:rgba(245,200,66,.3); }}
  .t-radar {{ color:var(--teal); border-color:rgba(56,201,212,.3); }}
  .t-topic {{ background:rgba(124,92,252,.08); color:var(--purple); border:1px solid rgba(124,92,252,.2); }}
  .fycard.hidden {{ display:none; }}
  .world-list {{ display:flex; flex-direction:column; border:1px solid var(--border); border-radius:10px; overflow:hidden; }}
  .world-row {{ display:grid; grid-template-columns:24px 1fr 150px 2fr; gap:12px; align-items:center; padding:9px 14px; text-decoration:none; color:inherit; border-bottom:1px solid var(--border); transition:background .15s; }}
  .world-row:last-child {{ border-bottom:none; }}
  .world-row:hover {{ background:var(--bg2); }}
  .world-icon {{ font-size:13px; text-align:center; }}
  .world-title {{ font-size:11.5px; font-weight:600; color:var(--text2); line-height:1.3; }}
  .world-src {{ font-size:9.5px; color:var(--text3); font-family:var(--font-mono); }}
  .world-desc {{ font-size:10.5px; color:var(--text3); line-height:1.4; }}
  .p-pink::before  {{ background:linear-gradient(90deg,var(--pink),var(--purple)); }}
  .p-teal::before  {{ background:linear-gradient(90deg,var(--teal),var(--cyan)); }}
  .p-yellow::before {{ background:linear-gradient(90deg,var(--yellow),var(--orange)); }}
  .tpill {{ display:flex; align-items:center; gap:5px; padding:5px 11px; border-radius:20px; font-size:11px; font-weight:600; border:1px solid; margin-bottom:5px; }}
  .tpill-dot {{ width:6px; height:6px; border-radius:50%; flex-shrink:0; }}
  .theme-wrap {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px; }}
  .tp-curr  {{ background:rgba(91,138,247,.07);  color:var(--blue);   border-color:rgba(91,138,247,.25);  }} .tp-curr .tpill-dot  {{ background:var(--blue); }}
  .tp-home  {{ background:rgba(245,200,66,.07);  color:var(--yellow); border-color:rgba(245,200,66,.25);  }} .tp-home .tpill-dot  {{ background:var(--yellow); }}
  .tp-agent {{ background:rgba(249,124,60,.07);  color:var(--orange); border-color:rgba(249,124,60,.25);  }} .tp-agent .tpill-dot {{ background:var(--orange); }}
  .tp-model {{ background:rgba(124,92,252,.07);  color:var(--purple); border-color:rgba(124,92,252,.25);  }} .tp-model .tpill-dot {{ background:var(--purple); }}
  .tp-infra {{ background:rgba(56,201,212,.07);  color:var(--teal);   border-color:rgba(56,201,212,.25);  }} .tp-infra .tpill-dot {{ background:var(--teal); }}
  .tp-econ  {{ background:rgba(240,93,154,.07);  color:var(--pink);   border-color:rgba(240,93,154,.25);  }} .tp-econ .tpill-dot  {{ background:var(--pink); }}
  .tp-gis   {{ background:rgba(52,216,154,.07);  color:var(--green);  border-color:rgba(52,216,154,.25);  }} .tp-gis .tpill-dot   {{ background:var(--green); }}
  .tp-design {{ background:rgba(56,201,212,.07); color:var(--cyan);   border-color:rgba(56,201,212,.25);  }} .tp-design .tpill-dot {{ background:var(--cyan); }}
  .sig {{ display:flex; align-items:center; gap:9px; margin-bottom:8px; }}
  .sig-icon {{ font-size:13px; width:18px; flex-shrink:0; text-align:center; }}
  .sig-lbl {{ font-size:11px; color:var(--text2); flex:1; }}
  .sig-bar-bg {{ width:80px; height:5px; background:var(--bg4); border-radius:3px; flex-shrink:0; overflow:hidden; }}
  .sig-bar {{ height:100%; border-radius:3px; }}
  .sig-ct {{ font-size:10px; font-family:var(--font-mono); color:var(--text3); width:14px; text-align:right; }}
  .model-row {{ display:flex; align-items:center; justify-content:space-between; padding:7px 0; border-bottom:1px solid var(--border); }}
  .model-row:last-child {{ border-bottom:none; }}
  .model-name {{ font-size:12px; font-weight:700; color:var(--text); }}
  .model-co {{ font-size:10px; color:var(--text3); font-family:var(--font-mono); }}
  .model-status {{ font-size:9px; font-weight:700; padding:3px 8px; border-radius:20px; }}
  .ms-new  {{ background:rgba(52,216,154,.12); color:var(--green); }}
  .ms-watch {{ background:rgba(91,138,247,.12); color:var(--blue); }}
  .ms-arch {{ background:rgba(124,92,252,.12); color:var(--purple); }}
  .ms-tool {{ background:rgba(249,124,60,.12); color:var(--orange); }}
  .ms-infra {{ background:rgba(56,201,212,.12); color:var(--teal); }}
  .apply-card {{ background:var(--bg3); border:1px solid var(--border); border-radius:9px; padding:12px 14px; margin-bottom:9px; }}
  .apply-card:last-child {{ margin-bottom:0; }}
  .apply-head {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:5px; }}
  .apply-title {{ font-size:12px; font-weight:700; color:var(--text); flex:1; line-height:1.3; }}
  .effort {{ font-size:8.5px; font-weight:700; padding:2px 6px; border-radius:5px; margin-left:8px; flex-shrink:0; white-space:nowrap; }}
  .e-low  {{ background:rgba(52,216,154,.12); color:var(--green); }}
  .e-med  {{ background:rgba(245,200,66,.12); color:var(--yellow); }}
  .e-high {{ background:rgba(249,124,60,.12); color:var(--orange); }}
  .apply-desc {{ font-size:10.5px; color:var(--text2); line-height:1.5; }}
  .panel {{ background:var(--bg2); border:1px solid var(--border); border-radius:13px; padding:18px 20px; position:relative; overflow:hidden; }}
  .panel::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px; }}
  .p-blue::before {{ background:linear-gradient(90deg,var(--blue),var(--purple)); }}
  .plabel {{ font-size:10px; font-weight:700; letter-spacing:1.1px; text-transform:uppercase; color:var(--text3); margin-bottom:11px; }}
  .g3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-top:12px; }}
  .footer {{ margin-top:20px; padding-top:14px; border-top:1px solid var(--border); font-size:10px; color:var(--text3); font-family:var(--font-mono); display:flex; justify-content:space-between; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="h-title">AI Discovery Hub</div>
    <div class="h-sub">{today} &nbsp;·&nbsp; {n_personal} relevant · {n_world} world signals</div>
  </div>
</div>

<div class="stat-row">
  <div class="sc" onclick="filterTier('all')"><div class="sc-num c-blue">{n_personal}</div><div class="sc-lbl">Your Stack</div></div>
  <div class="sc" onclick="filterTier('adopt')"><div class="sc-num c-green">{n_adopt}</div><div class="sc-lbl">✅ Adopt Now</div></div>
  <div class="sc" onclick="filterTier('watch')"><div class="sc-num c-blue">{n_watch}</div><div class="sc-lbl">👁 Watch Closely</div></div>
  <div class="sc" onclick="filterTier('radar')"><div class="sc-num c-teal">{n_radar}</div><div class="sc-lbl">🌱 On Radar</div></div>
  <div class="sc" style="cursor:default"><div class="sc-num c-orange">{n_adjacent}</div><div class="sc-lbl">🔀 Adjacent</div></div>
  <div class="sc" style="cursor:default"><div class="sc-num c-text3">{n_world}</div><div class="sc-lbl">🌐 AI World</div></div>
</div>

<div class="controls">
  <div class="sort-row">
    <span class="row-lbl">SORT</span>
    <button class="sort-btn active" id="sort-tier" onclick="sortHub('tier')">By Tier Priority</button>
    <button class="sort-btn" id="sort-date" onclick="sortHub('date')">By Recency</button>
  </div>
  <div class="filter-row">
    <span class="row-lbl">LENS</span>
    <button class="filter-btn active" id="f-all" onclick="filterHub('all')">All</button>
    <button class="filter-btn f-home" id="f-home" onclick="filterHub('home')" data-tip="Personal projects, home automation, local tools, budgeting">🏠 Home</button>
    <button class="filter-btn f-curr" id="f-curr" onclick="filterHub('curr')" data-tip="Claude API, model releases, AI industry, agent tooling">📡 Current</button>
    <button class="filter-btn f-gis"  id="f-gis"  onclick="filterHub('gis')"  data-tip="Geospatial AI, FME, Sentinel Hub, QGIS, spatial data">🗺 GIS/FME</button>
  </div>
  <div class="filter-row">
    <span class="row-lbl">TIER</span>
    <button class="filter-btn active" id="t-all" onclick="filterTier('all')">All</button>
    <button class="filter-btn fb-adopt" id="t-adopt" onclick="filterTier('adopt')" data-tip="High ROI — ready to use in your projects today">✅ Adopt Now</button>
    <button class="filter-btn fb-watch" id="t-watch" onclick="filterTier('watch')" data-tip="Important signal — evaluate soon">👁 Watch Closely</button>
    <button class="filter-btn fb-hype"  id="t-hype"  onclick="filterTier('hype')"  data-tip="Viral or contested — verify before acting">🔥 Hype Check</button>
    <button class="filter-btn fb-found" id="t-found" onclick="filterTier('found')" data-tip="Core infrastructure or concept worth understanding">🏗 Foundation</button>
    <button class="filter-btn fb-radar" id="t-radar" onclick="filterTier('radar')" data-tip="Early traction — not proven yet, but watch it">🌱 On Radar</button>
  </div>
</div>

<div class="section-header">
  <div class="section-title">Your Stack &amp; Adjacent</div>
  <span class="section-badge sb-personal">{n_personal} signals</span>
  <div class="section-line"></div>
</div>

<div class="hub-grid" id="hub-grid">
"""

    for art in personal:
        icon       = art.get('icon', '📦')
        tier_key   = "adopt" if "Adopt" in art['tier'] else "watch" if "Watch" in art['tier'] else "hype" if "Hype" in art['tier'] else "radar" if "Radar" in art['tier'] else "found"
        tier_class = f"t-{tier_key}"
        lens_key   = "home" if "Home" in art.get('lens','') else "gis" if "GIS" in art.get('lens','') else "curr"
        topics     = art.get('topics', [])
        topic_tags = "".join(f'<span class="tag t-topic">{t.replace("t-","")}</span>' for t in topics)
        dur        = duration_map.get(art['url'], '') if art.get('type') == 'video' else ''
        dur_html   = f'<span class="vid-dur">⏱ {dur}</span>' if dur else ''
        why        = art.get('relevance_why', '')
        is_adj     = why.lower().startswith('adjacent')
        adj_class  = ' adjacent' if is_adj else ''
        why_html   = f'<div class="fycard-why">↳ {why}</div>' if why else ''
        html += f"""  <a class="fycard{adj_class}" href="{art['url']}" target="_blank" rel="noopener noreferrer" data-date="{art['date']}" data-tier="{art['tier']}" data-tierkey="{tier_key}" data-lens="{art['lens']}" data-lenskey="{lens_key}">
    <div class="fycard-icon">{icon}</div>
    <div class="fycard-title">{art['title']}</div>
    <div class="fycard-src"><span>{art['source']} · {art['date']}</span>{dur_html}</div>
    <div class="fycard-desc">{art['desc']}</div>
    {why_html}<div class="tag-row">
      <span class="tag t-lens">{art['lens']}</span>
      <span class="tag t-tier {tier_class}">{art['tier']}</span>
      {topic_tags}
    </div>
  </a>
"""

    html += f"""</div>

<div class="section-header" style="margin-top:28px;">
  <div class="section-title">AI World at Large</div>
  <span class="section-badge sb-world">{n_world} signals · awareness only</span>
  <div class="section-line"></div>
</div>

<div class="world-list">
{world_rows_html}
</div>

<div class="g3">
  <div class="panel p-pink">
    <div class="plabel">Weekly Themes</div>
    <div class="theme-wrap">{themes_html}</div>
    <div class="plabel">Signal Mix (Your Stack)</div>
    {bars_html}
  </div>
  <div class="panel p-teal">
    <div class="plabel">Model Tracker</div>
    {tracker_html}
  </div>
  <div class="panel p-yellow">
    <div class="plabel">The Lab — Apply This Week</div>
    {lab_html}
  </div>
</div>

<div class="footer">
  <div>powered by {data['metadata']['model']} · hub-v2</div>
  <div>{today}</div>
</div>

<script>
  let currentLens = 'all';
  let currentTier = 'all';
  let currentSort = 'tier';

  function applyFilters() {{
    document.querySelectorAll('#hub-grid .fycard').forEach(card => {{
      const lk = card.dataset.lenskey || '';
      const tk = card.dataset.tierkey || '';
      const lensOk = currentLens === 'all' || lk === currentLens;
      const tierOk = currentTier === 'all' || tk === currentTier;
      card.classList.toggle('hidden', !(lensOk && tierOk));
    }});
  }}

  function filterHub(lens) {{
    currentLens = lens;
    ['all','home','curr','gis'].forEach(id => document.getElementById('f-' + id).classList.remove('active'));
    document.getElementById('f-' + lens).classList.add('active');
    applyFilters();
  }}

  function filterTier(tier) {{
    currentTier = tier;
    ['all','adopt','watch','hype','found','radar'].forEach(id => document.getElementById('t-' + id).classList.remove('active'));
    document.getElementById('t-' + tier).classList.add('active');
    applyFilters();
  }}

  function sortHub(method) {{
    currentSort = method;
    const grid = document.getElementById('hub-grid');
    const cards = Array.from(grid.children);
    document.getElementById('sort-tier').classList.toggle('active', method === 'tier');
    document.getElementById('sort-date').classList.toggle('active', method === 'date');
    const getTierVal = t => {{
      if (!t) return 5;
      const s = t.toLowerCase();
      if (s.includes('adopt')) return 1;
      if (s.includes('watch')) return 2;
      if (s.includes('hype'))  return 3;
      if (s.includes('found')) return 4;
      return 5;
    }};
    cards.sort((a, b) => method === 'date'
      ? new Date(b.dataset.date) - new Date(a.dataset.date)
      : getTierVal(a.dataset.tier) - getTierVal(b.dataset.tier));
    grid.innerHTML = '';
    cards.forEach(card => grid.appendChild(card));
    applyFilters();
  }}

  document.addEventListener('DOMContentLoaded', () => sortHub('tier'));
</script>
</body>
</html>"""
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/hub-input.json", help="Path to unified input data")
    parser.add_argument("--output", type=str, default="dashboards", help="Output directory")
    args = parser.parse_args()

    input_path = PROJECT_ROOT / args.input
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)

    with open(input_path, "r") as f:
        input_data = json.load(f)

    # Build URL → duration lookup from raw fetch data
    duration_map = {v["url"]: v["duration"] for v in input_data.get("videos", []) if v.get("duration")}

    print("Generating Unified Hub Content...")
    content = generate_hub_content(input_data)

    # Add generation metadata
    content["metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "model": DEFAULT_MODEL,
        "provider": DEFAULT_PROVIDER
    }

    print("Rendering HTML...")
    html = render_html(content, duration_map)
    
    today_iso = datetime.now().strftime("%Y-%m-%d")
    output_dir_path = Path(args.output)
    output_path = output_dir_path / f"AI-Discovery-Hub-{today_iso}.html"
    output_path.write_text(html, encoding="utf-8")
    
    # Also create latest.html
    latest_path = output_dir_path / "latest.html"
    latest_path.write_text(html, encoding="utf-8")
    
    print(f"Dashboard created: {output_path}")
    print(f"Latest dashboard updated: {latest_path}")

if __name__ == "__main__":
    main()
