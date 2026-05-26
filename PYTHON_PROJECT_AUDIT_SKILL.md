---
name: python-project-audit
description: >
  Deep audit, bug fixing, and hardening of Python projects pulled from GitHub.
  Use this skill whenever the user wants to: review a Python repo for bugs,
  perform cross-file behavioral analysis, fix silent errors or unsafe code,
  harden production readiness, analyze logic flows across multiple files,
  set up GitHub Actions CI/CD, or do any multi-level code quality analysis
  (static + runtime + behavioral). Triggers on phrases like "audit my repo",
  "check my code", "find bugs", "fix my project", "review my files",
  "cross-file review", "production ready", "debug my agent", or any request
  involving a GitHub repo and code quality. Always use this skill — do not
  attempt a repo audit from memory or general knowledge alone.
---

# Python Project Audit Skill

A complete methodology for pulling a Python project from GitHub, auditing it
at every level (static → runtime → cross-file behavior → logic), fixing all
findings, and pushing the hardened result back.

This skill encodes the exact process used to take a production agentic AI
project from a 6.5/10 to an 8.8/10 over multiple audit rounds.

---

## Phase 0 — Setup

### 0.1 Get GitHub Access

If no GitHub MCP is connected, use the API directly via bash:

```python
TOKEN = "ghp_..."   # From user
REPO  = "username/repo-name"
```

Always verify the token works before pulling files:

```python
curl -s -H "Authorization: token {TOKEN}" \
  "https://api.github.com/user/repos?per_page=5"
```

### 0.2 List All Repos

```python
import urllib.request, json

url = f"https://api.github.com/user/repos?per_page=100"
req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
with urllib.request.urlopen(req) as resp:
    repos = json.loads(resp.read())
for r in repos:
    print(r['name'], '|', 'Private' if r['private'] else 'Public', '|', r['updated_at'][:10])
```

### 0.3 Pull All Python Files

```python
import urllib.request, json, base64, os

os.makedirs("/home/claude/audit", exist_ok=True)

url = f"https://api.github.com/repos/{REPO}/contents/"
req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
with urllib.request.urlopen(req) as resp:
    contents = json.loads(resp.read())

for item in contents:
    if item["type"] == "file" and item["name"].endswith(".py"):
        req = urllib.request.Request(item["url"], headers={"Authorization": f"token {TOKEN}"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        content = base64.b64decode(data["content"]).decode("utf-8")
        with open(f"/home/claude/audit/{item['name']}", "w") as f:
            f.write(content)
        print(f"Synced: {item['name']}")
```

---

## Phase 1 — Static Analysis (Layer 1)

Run these in order. Each layer catches different things.

### 1.1 Syntax Check

```python
import ast, os
for fname in sorted(os.listdir("/home/claude/audit")):
    if not fname.endswith(".py"): continue
    try:
        ast.parse(open(f"/home/claude/audit/{fname}").read())
        print(f"OK  {fname}")
    except SyntaxError as e:
        print(f"FAIL  {fname} — {e}")
```

**Stop here if any file fails syntax.** Fix before proceeding.

### 1.2 Pyflakes (Unused imports, undefined names, redefinitions)

```bash
pip install pyflakes --break-system-packages -q
cd /home/claude/audit && python3 -m pyflakes .
```

Key findings to look for:
- `imported but unused` — dead import
- `undefined name` — will crash at runtime (**critical**)
- `redefinition of unused` — duplicate function (**critical**)

### 1.3 AST Deep Scan

Run this single script — covers all static checks in one pass:

```python
import ast, os, re

directory = "/home/claude/audit"

print("=== SILENT EXCEPT BLOCKS ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            exc = node.type.id if (node.type and isinstance(node.type, ast.Name)) else "bare"
            if exc == "FileNotFoundError": continue   # intentional silent
            has_log = any(
                isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and
                any(kw in ast.dump(s.value) for kw in ["logging", "logger"])
                for s in node.body
            )
            if not has_log:
                body = [type(s).__name__ for s in node.body]
                print(f"  {fname}:{node.lineno}  except {exc}  body={body}")

print("\n=== UNSAFE DIRECT KEY READS ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript) and
            isinstance(node.value, ast.Name) and
            isinstance(node.ctx, ast.Load) and
            isinstance(node.slice, ast.Constant) and
            isinstance(node.slice.value, str)):
            print(f"  {fname}:{node.lineno}  {node.value.id}['{node.slice.value}']")

print("\n=== print() CALLS (use logging instead) ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            print(f"  {fname}:{node.lineno}")

print("\n=== HARDCODED .json FILENAMES ===")
pattern = re.compile(r'"[\w_]+\.json"')
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    for i, line in enumerate(open(f"{directory}/{fname}").readlines(), 1):
        if pattern.search(line):
            print(f"  {fname}:{i}  {line.strip()}")

print("\n=== DUPLICATE FUNCTION NAMES ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    seen = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in seen:
                print(f"  {fname}: '{node.name}' at lines {seen[node.name]} and {node.lineno}")
            seen[node.name] = node.lineno

print("\n=== MUTABLE DEFAULT ARGUMENTS ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    print(f"  {fname}:{node.lineno}  {node.name}() mutable default")

print("\n=== int(os.getenv()) WITHOUT DEFAULT ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "int":
            if node.args and isinstance(node.args[0], ast.Call):
                inner = node.args[0]
                if isinstance(inner.func, ast.Attribute) and inner.func.attr == "getenv":
                    has_default = len(inner.args) >= 2
                    key = inner.args[0].value if isinstance(inner.args[0], ast.Constant) else "?"
                    if not has_default:
                        print(f"  {fname}:{node.lineno}  int(os.getenv('{key}')) — crashes if missing")

print("\n=== json.loads() WITHOUT SCHEMA VALIDATION ===")
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "loads":
                print(f"  {fname}:{node.lineno}  json.loads() — verify schema validation exists")
```

---

## Phase 2 — Runtime Logic Analysis (Layer 2)

Read the actual file contents. Focus on these patterns:

### 2.1 Cross-File Dependency Map

For every function that is **defined** in one file and **called** in another:

```python
import ast, os

directory = "/home/claude/audit"

# Build definition map
defined = {}  # fname -> [func_names]
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    tree = ast.parse(open(f"{directory}/{fname}").read())
    defined[fname] = [
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

# Find imports
for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    src = open(f"{directory}/{fname}").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [alias.name for alias in node.names]
            print(f"  {fname}  ←  {node.module}: {names}")
```

**What to verify for each imported function:**
- Is it actually defined in the source file?
- Does the caller pass the right argument types?
- Does the callee handle all edge cases the caller might produce?

### 2.2 Data Schema Consistency

For any system using JSON state files or dict objects passed between functions:

1. Find where objects are **created** (what keys are set)
2. Find where objects are **read** (what keys are accessed)
3. Verify every key read has a corresponding key written

**Common failure:** Function A creates `{"type": "X", "items": [...]}` but
Function B calls `task["message"]` — key doesn't exist, KeyError at runtime.

Fix: always use `.get("key", default)` for reads on external data.

### 2.3 State Mutation Audit

For any file that reads and writes shared state (JSON files, global dicts):

```
load() → mutate → save()
```

Verify:
- Is `save()` always called after mutation? (not just on success path)
- Is `save()` wrapped in try/except? (disk full, permissions)
- Can two concurrent runs corrupt the file? (GitHub Actions parallel runs)

### 2.4 Retry and Fallback Paths

For any LLM API call:

```
Does it retry on failure?          → If not: single point of failure
Does it validate the response?     → If not: malformed output silently breaks downstream
Does it strip JSON fences?         → LLMs wrap JSON in ```json ... ``` frequently
Does it have a hard fallback?      → If LLM is down, what happens?
```

Standard pattern to implement:

```python
MAX_RETRIES = 3

for attempt in range(1, MAX_RETRIES + 1):
    try:
        response = call_llm(prompt)
        cleaned = strip_json_fences(response)
        parsed = json.loads(cleaned)
        if not validate_schema(parsed):
            logger.warning("Schema invalid [attempt=%d]", attempt)
            continue
        return parsed
    except json.JSONDecodeError:
        logger.warning("JSON parse failed [attempt=%d/%d]", attempt, MAX_RETRIES)
    except Exception:
        logger.exception("LLM call failed [attempt=%d/%d]", attempt, MAX_RETRIES)
        break

logger.error("All %d attempts failed — returning fallback", MAX_RETRIES)
return fallback_value
```

### 2.5 Deduplication Audit

For any system that creates records (tasks, events, messages):

- Is there a `exists()` check before `create()`?
- If the script runs twice (cron restart, retry), will it create duplicates?
- For scheduled jobs: is there a "already ran today" guard?
- For reminders: is there a cooldown between sends?

### 2.6 Environment Variable Safety

```python
# UNSAFE — crashes with TypeError if var missing
API_ID = int(os.getenv("API_ID"))

# SAFE — fail-fast with clear message
_REQUIRED = ["API_ID", "API_HASH", "BOT_TOKEN", "GROQ_API_KEY"]
_missing = [k for k in _REQUIRED if not os.getenv(k)]
if _missing:
    logging.critical("Missing env vars: %s", ", ".join(_missing))
    raise SystemExit(1)
API_ID = int(os.getenv("API_ID", "0"))  # safe after validation
```

---

## Phase 3 — Cross-File Behavioral Review (Layer 3)

This is the most important phase. Read every file that interacts with every
other file. Build a mental model of the full data flow.

### 3.1 The Five Questions

For each pair of files that share data:

1. **Schema contract:** Does File A produce exactly what File B expects?
2. **Error propagation:** If File A fails, does File B crash or degrade gracefully?
3. **State consistency:** If File A writes state and File B reads it, can they diverge?
4. **Duplication:** Is the same logic or constant defined in both files?
5. **Missing calls:** Is there a function defined for a purpose that is never actually called?

### 3.2 The "Never Called" Pattern (High Impact)

The most insidious bug in multi-file systems: a function that exists and looks
correct but is never imported or called anywhere.

```python
# Scan for defined-but-never-called functions across files
import ast, os

directory = "/home/claude/audit"

all_defined = {}
all_called = set()

for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    src = open(f"{directory}/{fname}").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            all_defined[node.name] = fname
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                all_called.add(node.func.id)
            if isinstance(node.func, ast.Attribute):
                all_called.add(node.func.attr)

never_called = {k: v for k, v in all_defined.items()
                if k not in all_called and not k.startswith("_")}
for fname_def, func in [(v,k) for k,v in never_called.items()]:
    print(f"  {fname_def}: {func}() — defined but never called")
```

### 3.3 Config Centralization Check

Any constant defined in more than one file is a maintenance hazard:

```python
import os, re

directory = "/home/claude/audit"
constants = {}  # value -> [files that define it]

for fname in sorted(os.listdir(directory)):
    if not fname.endswith(".py"): continue
    for i, line in enumerate(open(f"{directory}/{fname}").readlines(), 1):
        # Match: CONSTANT_NAME = "value" or CONSTANT_NAME = 123
        m = re.match(r'^([A-Z_]{3,})\s*=\s*(.+)', line.strip())
        if m:
            key, val = m.group(1), m.group(2).strip()
            constants.setdefault(f"{key}={val}", []).append(fname)

for const, files in constants.items():
    if len(files) > 1:
        print(f"  DUPLICATE: {const}  in  {files}")
```

### 3.4 Utility Code Duplication

Look for identical or near-identical function bodies across files:

- Same function defined in 4 files → extract to `utils.py`
- Same constant defined in 4 files → move to `config.py`
- Same try/except pattern copy-pasted → extract to helper

---

## Phase 4 — Severity Classification

Before fixing, classify every finding:

| Severity | Definition | Examples |
|---|---|---|
| **Critical** | Crashes at runtime, always | NameError, duplicate function, missing key |
| **High** | Causes wrong behavior silently | Never-called dedup, broken completion logic |
| **Medium** | Degrades reliability over time | Silent excepts, no retry, reminder spam |
| **Low** | Code quality, maintenance risk | Unused imports, hardcoded values, duplication |

**Fix order:** Critical → High → Medium → Low

---

## Phase 5 — Fix Patterns

### 5.1 Logging Fix (replaces all silent excepts)

```python
# Add at top of every file
import logging
logger = logging.getLogger(__name__)

# Replace every bare except or except Exception: pass
# BAD
except Exception:
    pass

# GOOD
except Exception:
    logger.exception(
        "function_name failed [context_var=%s other=%s]",
        context_var, other
    )
    return safe_fallback_value
```

Always include: function name + relevant variable values in log message.
Use `logger.exception()` not `logger.error()` — captures full traceback.

### 5.2 Safe Key Access

```python
# BAD — KeyError if key missing
value = task["status"]

# GOOD — safe with sensible default
value = task.get("status", "PENDING")
```

### 5.3 JSON Schema Validation

```python
def _validate_schema(parsed):
    """Returns True if parsed matches expected shape."""
    if not isinstance(parsed, dict): return False
    items = parsed.get("items")
    if not isinstance(items, list): return False
    if not all(isinstance(i, str) for i in items): return False
    return True
```

### 5.4 Central Config

Create `config.py` as single source of truth:

```python
# config.py
TASKS_FILE     = "tasks.json"
STATE_FILE     = "state.json"
MAX_RETRIES    = 3
LOG_TRUNCATE   = 200
```

Import everywhere:
```python
from config import TASKS_FILE, MAX_RETRIES
```

### 5.5 Startup Validation

```python
_REQUIRED_ENV = ["API_KEY", "BOT_TOKEN", "USER_ID"]
_missing = [k for k in _REQUIRED_ENV if not os.getenv(k)]
if _missing:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logging.critical("Missing required env vars: %s — add to .env and restart.",
                     ", ".join(_missing))
    raise SystemExit(1)
```

---

## Phase 6 — Cross-File Validation (before every push)

Run this full suite after every batch of fixes. Zero failures required before pushing.

```python
import ast, os, re, subprocess

directory = "/home/claude/audit"

checks = {
    "pyflakes": lambda: subprocess.run(
        ["python3", "-m", "pyflakes", "."],
        cwd=directory, capture_output=True, text=True
    ).stdout.strip() == "",

    "syntax": lambda: all(
        __import__("ast").parse(open(f"{directory}/{f}").read()) or True
        for f in os.listdir(directory) if f.endswith(".py")
    ),

    "no_print": lambda: not any(
        any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "print"
            for n in ast.walk(ast.parse(open(f"{directory}/{f}").read())))
        for f in os.listdir(directory) if f.endswith(".py")
    ),

    "no_hardcoded_json": lambda: not any(
        re.search(r'"[\w_]+\.json"', line)
        for f in os.listdir(directory) if f.endswith(".py") and f != "config.py"
        for line in open(f"{directory}/{f}")
    ),
}

for name, check in checks.items():
    try:
        result = check()
        print(f"  {'✅' if result else '❌'}  {name}")
    except Exception as e:
        print(f"  ❌  {name} — {e}")
```

---

## Phase 7 — Push to GitHub

### 7.1 Push Single File

```python
import urllib.request, json, base64

def push_file(token, repo, fname, local_path, commit_msg):
    url = f"https://api.github.com/repos/{repo}/contents/{fname}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})

    # Get current SHA (None if new file)
    try:
        with urllib.request.urlopen(req) as resp:
            sha = json.loads(resp.read())["sha"]
    except urllib.error.HTTPError as e:
        sha = None if e.code == 404 else (_ for _ in ()).throw(e)

    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    body = {"message": commit_msg, "content": content}
    if sha: body["sha"] = sha

    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="PUT",
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    print(f"{fname} → {result['commit']['sha'][:10]}")
```

### 7.2 Push Multiple Files

```python
FILES = {
    "file1.py": "fix: description of what changed",
    "file2.py": "refactor: description of what changed",
}
for fname, msg in FILES.items():
    push_file(TOKEN, REPO, fname, f"/home/claude/audit/{fname}", msg)
```

### 7.3 Commit Message Convention

```
fix:      bug fix — runtime crash, wrong behavior
refactor: restructure without behavior change
chore:    maintenance — unused imports, formatting
docs:     README or documentation only
ci:       GitHub Actions workflow changes
```

---

## Phase 8 — GitHub Actions Setup

### 8.1 Check if Workflow Exists

```python
url = f"https://api.github.com/repos/{REPO}/contents/.github/workflows"
# HTTP 404 → no workflow exists
```

### 8.2 Standard Scheduled Workflow Template

```yaml
name: Agent Name

on:
  schedule:
    - cron: '0 */5 * * *'   # Every 5 hours — adjust as needed
  workflow_dispatch:          # Manual trigger

jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Initialize state files
        run: |
          [ -f state.json ]  || echo "{}" > state.json
          [ -f tasks.json ]  || echo "[]" > tasks.json

      - name: Run agent
        env:
          API_KEY: ${{ secrets.API_KEY }}
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
        run: python main.py

      - name: Commit state files
        run: |
          git config user.name  "Agent Bot"
          git config user.email "agent@github-actions"
          git add state.json tasks.json
          git diff --cached --quiet || git commit -m "chore: update state [skip ci]"

      - name: Push state files
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: main
```

### 8.3 State Persistence (Option A — Commit Back)

Remove all state JSON files from `.gitignore`. They must be tracked by git
for Option A to work. Only these should remain in `.gitignore`:

```gitignore
.env
*.session
*.log
__pycache__/
*.pyc
venv/
.venv/
```

---

## Phase 9 — Evaluation Scoring

Rate the project after each audit round:

| Area | Weight | What to assess |
|---|---|---|
| Architectural thinking | 20% | Is the design sound? Components well-separated? |
| Bug-free execution | 25% | Do critical paths work end-to-end? |
| Error handling | 20% | Are all failures logged and recoverable? |
| Code quality | 15% | Consistent style, no duplication, no dead code |
| Test coverage | 10% | Any tests? Even manual ones? |
| Documentation | 10% | README accurate? Reflects current code? |

Typical progression: 6.5 → 7.2 → 8.1 → 8.8 over 4 audit rounds.

---

## Checklist — Complete Audit

Use this as your checklist. Every item must be ✅ before calling the audit done.

**Static:**
- [ ] Pyflakes: zero warnings
- [ ] Syntax: all files pass
- [ ] No undefined names
- [ ] No duplicate function names
- [ ] No unused imports
- [ ] No print() in production code
- [ ] No bare except blocks
- [ ] No silent except blocks (all log with logger.exception)
- [ ] No mutable default arguments

**Runtime:**
- [ ] All except blocks log with context variables
- [ ] All direct key reads use .get() with defaults
- [ ] All json.loads() from LLM output are validated against schema
- [ ] All json.loads() from LLM output have retry logic
- [ ] All json.loads() from LLM output strip markdown fences first
- [ ] All int(os.getenv()) have safe defaults or prior validation
- [ ] All required env vars validated at startup with fail-fast
- [ ] All file writes wrapped in try/except

**Cross-file behavioral:**
- [ ] Every imported function is actually defined in source
- [ ] Every function with a clear dedup purpose is actually called
- [ ] Data schema consistent between producer and consumer files
- [ ] No constant defined in more than one file
- [ ] No utility function duplicated across files
- [ ] State files committed to .gitignore correctly (NOT if Option A)

**Logic:**
- [ ] Scheduled jobs have "already ran today" guard
- [ ] Reminder/notification systems have cooldown between sends
- [ ] Record creation has exists() check before create()
- [ ] Completion/deletion logic matches actual data schema

**Infrastructure:**
- [ ] GitHub Actions workflow exists and is tested
- [ ] All required secrets documented
- [ ] State files initialized correctly on first run
- [ ] [skip ci] tag on state commits to prevent loops

---

## README Update Checklist

After any code change, verify the README reflects:

- [ ] New files in project structure section
- [ ] Changed behavior in component descriptions
- [ ] Updated capabilities table
- [ ] Correct env variable names (match actual .env keys)
- [ ] Correct state file list in memory architecture section
- [ ] GitHub Actions YAML uses correct secret names
