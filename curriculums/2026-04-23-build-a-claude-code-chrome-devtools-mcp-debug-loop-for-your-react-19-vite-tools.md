# Build a Claude Code + Chrome DevTools MCP Debug Loop for React 19/Vite

## A Hands-On Tutorial for Agentic Frontend Debugging

---

## 1. Introduction & Context

### What Is This?

This tutorial walks you through wiring together three powerful tools into a single autonomous debugging loop:

- **Claude Code CLI** — Anthropic's agentic coding assistant that can read, write, and reason about your codebase
- **Chrome DevTools MCP Server** — A Model Context Protocol server that gives AI agents direct access to Chrome's debugging APIs (console logs, network requests, DOM inspection, JavaScript evaluation)
- **Your React 19/Vite app** — The live frontend target where bugs get caught and fixed

The end result: Claude can *see* your browser's console, *inspect* the DOM, *read* network errors, and *patch your source code* — all without you manually opening DevTools or copying error messages.

### Why This Matters

Traditional debugging is a human-in-the-loop process:

```
Bug appears → You open DevTools → You read errors → You describe them to AI → AI suggests fix → You apply fix → Repeat
```

With this setup, the loop becomes:

```
Bug appears → Claude inspects DevTools → Claude reads errors → Claude patches code → Bug fixed
```

This is particularly powerful for:
- **Hydration errors** common in React 19's new concurrent rendering model
- **Vite HMR edge cases** where hot module replacement silently fails
- **Network/API mismatch bugs** visible only in the Network tab
- **CSS-in-JS rendering issues** that only appear in computed styles

### Why Sentdex's Walkthrough Is the Right Starting Point

Sentdex's video provides the most practical, no-fluff setup path for the Chrome DevTools MCP server. This tutorial expands that walkthrough specifically for a **React 19/Vite** development context, adds the Claude Code CLI integration layer, and documents everything in a format suitable for a **Globe & Atlas workflow post**.

---

## 2. Prerequisites

### Required Knowledge
- [ ] Comfortable with terminal/CLI usage
- [ ] Basic understanding of what MCP (Model Context Protocol) is
- [ ] Familiarity with React and Vite project structure
- [ ] Have used Claude Code CLI at least once before

### Required Software

| Tool | Version | Install |
|------|---------|---------|
| Node.js | ≥ 18.x | [nodejs.org](https://nodejs.org) |
| npm or pnpm | latest | bundled with Node / `npm i -g pnpm` |
| Google Chrome | ≥ 121 | [google.com/chrome](https://google.com/chrome) |
| Claude Code CLI | latest | `npm install -g @anthropic-ai/claude-code` |
| Git | any | [git-scm.com](https://git-scm.com) |

### Required Accounts/Keys
- [ ] Anthropic API key with Claude Code access (set as `ANTHROPIC_API_KEY` in your environment)

### Your React 19/Vite App

You need a running React 19/Vite project. If you don't have one, scaffold one now:

```bash
npm create vite@latest my-debug-lab -- --template react
cd my-debug-lab
npm install
npm run dev
```

Confirm it's running at `http://localhost:5173` before proceeding.

> **Note:** If you're using a Streamlit app instead, jump to the [Streamlit Variant](#streamlit-variant) section after completing the core setup.

---

## 3. Step-by-Step Guide

### Phase 1: Install and Configure the Chrome DevTools MCP Server

#### Step 1.1 — Install the MCP Server Package

The Chrome DevTools MCP server bridges Claude to Chrome's [Chrome DevTools Protocol (CDP)](https://chromedevtools.github.io/devtools-protocol/).

```bash
npm install -g @modelcontextprotocol/server-chrome-devtools
```

Verify the installation:

```bash
mcp-server-chrome-devtools --version
```

> If you see a version number, you're good. If the command isn't found, check that your npm global bin directory is in your `PATH`.

#### Step 1.2 — Launch Chrome with Remote Debugging Enabled

Chrome must be started with a specific flag that opens a debugging port. **Close any existing Chrome windows first**, then run:

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  --no-first-run \
  --no-default-browser-check
```

**Linux:**
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  --no-first-run \
  --no-default-browser-check
```

**Windows (PowerShell):**
```powershell
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList `
  "--remote-debugging-port=9222", `
  "--user-data-dir=$env:TEMP\chrome-debug-profile", `
  "--no-first-run", `
  "--no-default-browser-check"
```

#### Step 1.3 — Verify Chrome Is Debuggable

Open a new terminal and run:

```bash
curl http://localhost:9222/json/version
```

You should see a JSON response like:

```json
{
  "Browser": "Chrome/121.0.0.0",
  "Protocol-Version": "1.3",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/..."
}
```

If you get a connection refused error, Chrome isn't running with remote debugging. Repeat Step 1.2.

#### Step 1.4 — Navigate Chrome to Your React App

In the debugging Chrome instance, navigate to:

```
http://localhost:5173
```

This is important — the MCP server needs an active tab with your app loaded.

---

### Phase 2: Configure Claude Code CLI to Use the MCP Server

#### Step 2.1 — Understand Claude Code's MCP Configuration

Claude Code reads MCP server configurations from a `.mcp.json` file. This file can live at:

- **Project level:** `<your-project-root>/.mcp.json` (affects only this project)
- **Global level:** `~/.claude/mcp.json` (affects all Claude Code sessions)

For this tutorial, we'll use **project-level** configuration to keep things contained.

#### Step 2.2 — Create the MCP Configuration File

In your React project root, create `.mcp.json`:

```bash
cd my-debug-lab  # or your existing project root
touch .mcp.json
```

Paste the following configuration:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "mcp-server-chrome-devtools",
      "args": [],
      "env": {
        "CHROME_DEBUGGING_URL": "http://localhost:9222"
      }
    }
  }
}
```

> **What this does:** When Claude Code starts, it launches `mcp-server-chrome-devtools` as a subprocess. Claude can then call tools exposed by this server — things like `get_console_logs`, `evaluate_javascript`, `get_dom_snapshot`, and `get_network_requests`.

#### Step 2.3 — Verify Claude Code Sees the MCP Server

Start Claude Code in your project directory:

```bash
claude
```

Once the interactive session starts, type:

```
/mcp
```

You should see output listing your configured servers:

```
MCP Servers:
  ✓ chrome-devtools (connected)
    Tools: get_console_logs, evaluate_javascript, get_dom_snapshot, 
           get_network_requests, take_screenshot, navigate_to_url
```

If you see `✗ chrome-devtools (failed)`, go back and confirm:
1. Chrome is running with `--remote-debugging-port=9222`
2. `curl http://localhost:9222/json/version` returns valid JSON
3. The `mcp-server-chrome-devtools` binary is in your PATH

---

### Phase 3: Plant a Realistic Frontend Bug

Before we test the debug loop, we need a bug to find and fix. Let's plant one that's representative of real React 19/Vite issues.

#### Step 3.1 — Create a Buggy Component

In your project, create `src/components/UserDashboard.jsx`:

```jsx
// src/components/UserDashboard.jsx
import { useState, useEffect } from 'react';

// BUG 1: API endpoint is wrong (typo) — will cause network 404
const API_URL = 'http://localhost:3001/api/usres'; // "usres" instead of "users"

// BUG 2: Rendering a non-existent nested property without optional chaining
function UserCard({ user }) {
  return (
    <div className="user-card">
      {/* This will throw if user.profile is undefined */}
      <h2>{user.profile.displayName}</h2>
      <p>{user.email}</p>
    </div>
  );
}

export default function UserDashboard() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('UserDashboard mounted, fetching users...');
    
    fetch(API_URL)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        console.log('Users fetched:', data);
        setUsers(data);
      })
      .catch(err => {
        console.error('Failed to fetch users:', err.message);
        setError(err.message);
        // BUG 3: Fallback data has wrong shape — missing .profile property
        setUsers([{ email: 'fallback@example.com', name: 'Fallback User' }]);
      });
  }, []);

  if (!users) return <p>Loading...</p>;

  return (
    <div className="dashboard">
      <h1>User Dashboard</h1>
      {error && <div className="error-banner">API Error: {error}</div>}
      {users.map((user, i) => (
        <UserCard key={i} user={user} />
      ))}
    </div>
  );
}
```

#### Step 3.2 — Wire It Into Your App

Update `src/App.jsx`:

```jsx
import UserDashboard from './components/UserDashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <UserDashboard />
    </div>
  );
}

export default App;
```

#### Step 3.3 — Save and Watch Vite HMR Update

Vite should hot-reload automatically. The app will now show a React error boundary crash or a blank screen, with errors in the console. **Do not open Chrome DevTools manually.** Let Claude find them.

---

### Phase 4: Run the Autonomous Debug Loop

This is the core of the exercise. We'll give Claude a high-level prompt and watch it use the MCP tools to diagnose and fix bugs.

#### Step 4.1 — Craft Your Debug Prompt

In your Claude Code session, paste this prompt:

```
I have a React 19/Vite app running at http://localhost:5173. 
The UserDashboard component appears to be broken. 

Please do the following:
1. Navigate to http://localhost:5173 using the browser tools
2. Check the browser console for any errors or warnings
3. Check the network tab for any failed requests
4. Inspect the DOM to understand what's actually rendering
5. Read the source file at src/components/UserDashboard.jsx
6. Identify ALL bugs you find
7. Fix them directly in the source file
8. Verify your fix works by checking the console again after Vite reloads

Do not ask me for permission at each step. Work autonomously through the full debug cycle.
```

#### Step 4.2 — Observe Claude's Tool Calls

Watch Claude work through the debug loop. You should see it making tool calls similar to:

```
● chrome-devtools:navigate_to_url
  url: "http://localhost:5173"
  
● chrome-devtools:get_console_logs
  → [ERROR] Failed to fetch users: HTTP 404: Not Found
  → [ERROR] Cannot read properties of undefined (reading 'displayName')
  → [LOG] UserDashboard mounted, fetching users...

● chrome-devtools:get_network_requests
  → GET http://localhost:3001/api/usres — 404 Not Found

● Read(src/components/UserDashboard.jsx)
  → [reads file content]

● Edit(src/components/UserDashboard.jsx)
  → Fixes API URL typo: 'usres' → 'users'
  → Adds optional chaining: user.profile?.displayName ?? user.name
  → Updates fallback data shape to include profile object

● chrome-devtools:get_console_logs
  → [LOG] UserDashboard mounted, fetching users...
  → No errors present
```

#### Step 4.3 — Example of What Claude Should Produce

After the debug loop, your fixed file should look something like:

```jsx
// src/components/UserDashboard.jsx (FIXED)
import { useState, useEffect } from 'react';

// FIXED: Corrected API endpoint typo
const API_URL = 'http://localhost:3001/api/users';

// FIXED: Added optional chaining and fallback for missing profile
function UserCard({ user }) {
  return (
    <div className="user-card">
      <h2>{user.profile?.displayName ?? user.name ?? 'Unknown User'}</h2>
      <p>{user.email}</p>
    </div>
  );
}

export default function UserDashboard() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('UserDashboard mounted, fetching users...');
    
    fetch(API_URL)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        console.log('Users fetched:', data);
        setUsers(data);
      })
      .catch(err => {
        console.error('Failed to fetch users:', err.message);
        setError(err.message);
        // FIXED: Fallback data now matches expected shape with profile object
        setUsers([{ 
          email: 'fallback@example.com', 
          name: 'Fallback User',
          profile: { displayName: 'Fallback User' }
        }]);
      });
  }, []);

  if (!users) return <p>Loading...</p>;

  return (
    <div className="dashboard">
      <h1>User Dashboard</h1>
      {error && <div className="error-banner">API Error: {error}</div>}
      {users.map((user, i) => (
        <UserCard key={i} user={user} />
      ))}
    </div>
  );
}
```

---

### Phase 5: Document Your Setup (Globe & Atlas Workflow Post)

#### Step 5.1 — Create a Setup Script for Repeatability

Create `scripts/start-debug-session.sh` in your project:

```bash
#!/usr/bin/env bash
# Globe & Atlas Dev Workflow: Claude Code + Chrome DevTools Debug Loop
# Run this before starting a debugging session

set -e

echo "🔍 Starting Chrome DevTools debug session..."

# Kill any existing debug Chrome instances
pkill -f "remote-debugging-port=9222" 2>/dev/null || true
sleep 1

# Detect OS and launch Chrome with debugging
if [[ "$OSTYPE" == "darwin"* ]]; then
  CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  CHROME_BIN="google-chrome"
else
  echo "Windows detected: please run the PowerShell command manually"
  exit 1
fi

"$CHROME_BIN" \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  --no-first-run \
  --no-default-browser-check \
  &

echo "⏳ Waiting for Chrome to initialize..."
sleep 3

# Verify Chrome is ready
if curl -s http://localhost:9222/json/version > /dev/null; then
  echo "✅ Chrome DevTools accessible at port 9222"
else
  echo "❌ Chrome failed to start with debugging enabled"
  exit 1
fi

# Start Vite dev server in background if not running
if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
  echo "🚀 Starting Vite dev server..."
  npm run dev &
  sleep 3
  echo "✅ Vite running at http://localhost:5173"
else
  echo "✅ Vite already running at http://localhost:5173"
fi

echo ""
echo "🤖 Ready! Start your Claude Code session:"
echo "   cd $(pwd) && claude"
echo ""
echo "💡 In Claude, run: /mcp to verify chrome-devtools is connected"
```

Make it executable:

```bash
chmod +x scripts/start-debug-session.sh
```

#### Step 5.2 — Document Your MCP Configuration in the Project README

Add this section to your project's `README.md`:

````markdown
## 🤖 Claude Code + Chrome DevTools Debug Loop

This project is configured for autonomous AI-assisted debugging using Claude Code CLI
and the Chrome DevTools MCP server.

### Quick Start

```bash
# 1. Start the debug environment
./scripts/start-debug-session.sh

# 2. Launch Claude Code
claude

# 3. Verify MCP connection inside Claude
/mcp

# 4. Give Claude a debug task
# "Check the browser console for errors and fix any issues you find in src/"
```

### How It Works

| Component | Role |
|-----------|------|
| Chrome (port 9222) | Exposes DevTools Protocol for AI access |
| MCP Server | Translates CDP into tools Claude can call |
| Claude Code CLI | Reads console, inspects network, edits source |
| Vite HMR | Applies fixes instantly without full reload |

### MCP Tools Available

- `get_console_logs` — Read browser console output
- `get_network_requests` — Inspect HTTP requests and responses  
- `evaluate_javascript` — Run JS in the browser context
- `get_dom_snapshot` — Get current DOM structure
- `take_screenshot` — Capture visual state
- `navigate_to_url` — Control browser navigation
````

---

### Streamlit Variant

If you're debugging a **Streamlit app** instead of React/Vite, the MCP server setup is identical. Only the target URL and bug patterns differ.

#### Key Differences

```bash
# Streamlit runs on port 8501 by default
streamlit run app.py

# Navigate Claude to:
# http://localhost:8501
```

#### Streamlit-Specific Debug Prompt

```
I have a Streamlit app running at http://localhost:8501.
Check the browser console for WebSocket errors or component rendering failures.
Look specifically for st.session_state KeyErrors or widget key conflicts.
Read app.py and fix any issues you find.
```

> **Note:** Streamlit's WebSocket-based rendering means console errors are often more informative than React's — Claude tends to catch session state bugs very effectively through this loop.

---

## 4. Validation

Use this checklist to confirm you've successfully completed the exercise.

### ✅ Infrastructure Validation

```bash
# 1. Chrome debugging port is accessible
curl http://localhost:9222/json/version | python3 -m json.tool
# Expected: Valid JSON with Browser version info

# 2. MCP server binary is available
which mcp-server-chrome-devtools
# Expected: A file path (not "not found")

# 3. Vite is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
# Expected: 200
```

### ✅ Claude Code Integration Validation

Inside a Claude Code session:

```
/mcp
```

Expected output:
```
✓ chrome-devtools (connected)
  Tools available: get_console_logs, evaluate_javascript, ...
```

### ✅ Debug Loop Validation

Run this prompt in Claude Code and verify each step produces real output:

```
Using the chrome-devtools MCP server:
1. Get the current console logs from the browser
2. Evaluate this JavaScript: document.title
3. Take a screenshot
Tell me what you found at each step.
```

Claude should return:
- Actual console log entries (not empty/error)
- The actual page title string
- A description of what's visible in the screenshot

### ✅ Autonomous Bug Fix Validation

After Claude fixes your `UserDashboard.jsx`:

1. **No crash:** The React app renders without an error boundary triggering
2. **No console errors:** Claude's re-check of `get_console_logs` returns clean output
3. **Source file updated:** `git diff src/components/UserDashboard.jsx` shows the three bug fixes
4. **Bug fixes are correct:** Optional chaining added, API URL corrected, fallback data shape fixed

### ✅ Documentation Validation

- [ ] `.mcp.json` exists in project root and is committed to git
- [ ] `scripts/start-debug-session.sh` exists and runs without errors
- [ ] `README.md` contains the Claude Code debug loop section
- [ ] You can answer: *"What's the difference between running Claude with and without the chrome-devtools MCP server?"*

---

## 5. Next Steps

### Immediate Improvements (This Week)

**A. Add Playwright to the Loop**

Claude Code + Chrome DevTools MCP + Playwright creates a complete test-debug-fix triangle:

```bash
npm install -D @playwright/test
npx playwright install chromium
```

Create `playwright.config.ts` with `use: { channel: 'chrome' }` so Playwright reuses your debug Chrome instance. Now Claude can write a failing Playwright test, watch it fail via DevTools, fix the code, and verify the test passes — all autonomously.

**B. Persist Console Logs to a File**

Add this to your Vite dev setup to create a queryable log history:

```javascript
// vite.config.js — custom plugin to log browser errors to file
// Useful for post-mortem analysis of what Claude found
```

**C. Add Network Request Interception**

Ask Claude to use `evaluate_javascript` to inject a fetch interceptor that logs all API calls to the console — this makes network debugging even richer.

### Medium-Term Projects (Next Month)

**D. Build a Pre-Commit Debug Hook**

Wire Claude Code into a pre-commit hook that:
1. Runs your app
2. Checks the console for errors
3. Blocks the commit if errors are found
4. Optionally auto-fixes and re-stages

**E. Create a Reusable MCP Config Library**

Abstract your `.mcp.json` into a shared config package for all your Globe & Atlas projects:

```
@globe-atlas/mcp-config
  ├── react-vite.mcp.json
  ├── streamlit.mcp.json
  └── next-js.mcp.json
```

**F. Add the Filesystem MCP Server**

Combine Chrome DevTools MCP with the filesystem MCP server for deeper context:

```json
{
  "mcpServers": {
    "chrome-devtools": { ... },
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--root", "."]
    }
  }
}
```

### Resources for Deeper Learning

| Resource | What You'll Learn |
|----------|-------------------|
| [Chrome DevTools Protocol Docs](https://chromedevtools.github.io/devtools-protocol/) | All available CDP domains and methods |
| [MCP Specification](https://spec.modelcontextprotocol.io/) | How to build your own MCP servers |
| [Claude Code Docs](https://docs.anthropic.com/claude-code) | Advanced Claude Code CLI configuration |
| [Sentdex YouTube Channel](https://youtube.com/@sentdex) | More practical AI agent walkthroughs |
| [Vite Plugin API](https://vitejs.dev/guide/api-plugin.html) | Building custom Vite plugins for dev tooling |

### The Bigger Picture

What you've built here is a microcosm of **agentic software development**:

```
Observe (DevTools) → Reason (Claude) → Act (Edit source) → Verify (DevTools again)
```

This loop is the foundation of autonomous software agents. The same pattern scales to:
- Multi-page application audits
- Accessibility scanning and auto-remediation  
- Performance regression detection
- Cross-browser compatibility testing

The Chrome DevTools MCP server is one node in what will become a much larger network of tool integrations. Getting comfortable with this pattern now puts you ahead of the curve for how software development will work at scale.

---

*Tutorial designed for the Globe & Atlas workflow documentation series. Last validated against Claude Code CLI v1.x, Chrome 121+, and Vite 5.x.*