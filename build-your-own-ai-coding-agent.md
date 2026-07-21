# Build Your Own AI Coding Agent — The Complete Zero-to-Working Roadmap

This guide assumes **you know nothing about AI agents**. It walks through every concept, every tool, and every phase of implementation, in order, so you end up with a real terminal-based AI coding agent (like a mini Claude Code / Cursor Agent) that can read a codebase, write and edit files, run tests, and open pull requests.

---

## Table of Contents

1. [What You're Actually Building](#1-what-youre-actually-building)
2. [Concepts You Need First](#2-concepts-you-need-first)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
4. [Project Skeleton](#4-project-skeleton)
5. [Phase 1 — A Basic Chat Loop (No Tools Yet)](#5-phase-1--a-basic-chat-loop-no-tools-yet)
6. [Phase 2 — Giving the Agent Tools](#6-phase-2--giving-the-agent-tools)
7. [Phase 3 — The ReAct Agent Loop](#7-phase-3--the-react-agent-loop)
8. [Phase 4 — File Editing Without Burning Tokens](#8-phase-4--file-editing-without-burning-tokens)
9. [Phase 5 — Sandboxing & Safe Command Execution](#9-phase-5--sandboxing--safe-command-execution)
10. [Phase 6 — The Test-Fix-Retest Loop](#10-phase-6--the-test-fix-retest-loop)
11. [Phase 7 — Human-in-the-Loop Permissions](#11-phase-7--human-in-the-loop-permissions)
12. [Phase 8 — Context Window Management](#12-phase-8--context-window-management)
13. [Phase 9 — Git & GitHub Integration](#13-phase-9--git--github-integration)
14. [Phase 10 — Terminal UX Polish](#14-phase-10--terminal-ux-polish)
15. [Phase 11 — Advanced Features](#15-phase-11--advanced-features)
16. [Full Tech Stack Reference Table](#16-full-tech-stack-reference-table)
17. [Suggested Build Order (Milestones)](#17-suggested-build-order-milestones)
18. [Learning Resources](#18-learning-resources)

---

## 1. What You're Actually Building

An **AI coding agent** is a program that:

- Takes a plain-English instruction ("fix the bug in auth.py")
- Decides, on its own, what files to look at, what commands to run, and what code to change
- Actually performs those actions (not just suggests them)
- Checks its own work (runs tests) and corrects itself if something fails
- Reports back when the task is done

The key difference from a normal chatbot: a chatbot only *talks*. An agent *acts* — it calls real functions (tools) in a loop until the goal is met. This is called the **ReAct pattern**: Reason, then Act, then Observe the result, then repeat.

---

## 2. Concepts You Need First

If any of these are new to you, read this section slowly — everything else depends on it.

### 2.1 What an LLM is, in practical terms
A Large Language Model (LLM) like Claude or GPT-4 is a text-in, text-out function. You send it a conversation (a list of messages), and it predicts the next chunk of text. It has no memory between calls — your program must resend the whole conversation history every time.

### 2.2 Tool calling / function calling
Modern LLMs can be given a list of "tools" — essentially function signatures (name, description, and parameters as JSON Schema). Instead of just replying with text, the model can reply with a structured request like:

```json
{
  "tool_name": "read_file",
  "input": { "path": "src/auth.py" }
}
```

Your code — not the model — actually executes `read_file`. You then send the result back to the model as a new message, and it continues reasoning. **The model never touches your filesystem directly.** Your application is the only thing with real-world access; the model just requests actions.

### 2.3 The agent loop
This is the heart of the whole project:

```
while not done:
    response = call_llm(conversation_history)
    if response contains a tool call:
        result = execute_tool(response.tool_call)
        conversation_history.append(response)
        conversation_history.append(result)
    else:
        done = True  # model gave a final text answer
```

### 2.4 System prompt
A special instruction block sent with every request that defines the agent's identity, rules, and constraints (e.g., "You are a coding agent. Always read a file before editing it. Never run destructive commands without asking.").

### 2.5 Context window
The maximum amount of text (measured in tokens) the model can see at once. Large codebases don't fit, so agents must be selective about what they load — this is a major engineering challenge covered in Phase 8.

---

## 3. Prerequisites & Environment Setup

### What you should already know
- Basic Python (functions, classes, dictionaries, `try/except`)
- Basic command line usage (`cd`, `ls`, running scripts)
- What Git is (commit, branch, push) — doesn't need to be advanced

### Tools to install

| Tool | Purpose | Install |
|---|---|---|
| Python 3.10+ | Main language | python.org or `pyenv` |
| pip / venv | Package management | included with Python |
| Git | Version control operations | git-scm.com |
| Docker Desktop | Sandboxing (Phase 5) | docker.com |
| An API key | Access to the LLM | console.anthropic.com or platform.openai.com |
| VS Code (optional) | Editing your agent's own code | code.visualstudio.com |

### Initial setup commands

```bash
mkdir my-coding-agent && cd my-coding-agent
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install anthropic rich python-dotenv gitpython
```

Create a `.env` file (never commit this):

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

---

## 4. Project Skeleton

Set up this folder structure before writing any logic — it keeps tools, loop logic, and sandboxing cleanly separated as the project grows.

```
my-coding-agent/
├── .env
├── requirements.txt
├── main.py                 # entry point / CLI
├── agent/
│   ├── __init__.py
│   ├── loop.py              # the ReAct loop
│   ├── llm.py                # LLM API wrapper
│   ├── prompts.py            # system prompt templates
│   └── memory.py              # conversation/context management
├── tools/
│   ├── __init__.py
│   ├── file_tools.py          # read_file, write_file, edit_file
│   ├── search_tools.py         # search_codebase (ripgrep wrapper)
│   ├── shell_tools.py          # run_command, run_tests
│   └── git_tools.py            # git_commit_and_pr
├── sandbox/
│   └── docker_runner.py         # isolated execution
└── tests/
    └── test_tools.py
```

---

## 5. Phase 1 — A Basic Chat Loop (No Tools Yet)

Before adding any tools, get a plain conversational loop working so you understand the request/response cycle.

```python
# agent/llm.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def call_llm(messages, tools=None, system=""):
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system,
        messages=messages,
        tools=tools or [],
    )
```

```python
# main.py
from agent.llm import call_llm

history = []
print("Agent ready. Type a message (or 'exit').")
while True:
    user_input = input("> ")
    if user_input == "exit":
        break
    history.append({"role": "user", "content": user_input})
    response = call_llm(history)
    text = response.content[0].text
    print(text)
    history.append({"role": "assistant", "content": text})
```

Run it, talk to it, confirm history is preserved across turns. This is your foundation — everything else layers on top.

---

## 6. Phase 2 — Giving the Agent Tools

### 6.1 Define tool schemas
Each tool needs a strict JSON Schema so the model knows exactly what arguments to pass.

```python
# tools/__init__.py
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file, optionally a line range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file with new content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "search_codebase",
        "description": "Search the repository for a pattern using ripgrep.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "run_tests",
        "description": "Run the project's test suite and return output.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
]
```

### 6.2 Implement the actual functions

```python
# tools/file_tools.py
from pathlib import Path

def read_file(path, start_line=None, end_line=None):
    lines = Path(path).read_text().splitlines()
    if start_line and end_line:
        lines = lines[start_line - 1:end_line]
    return "\n".join(lines)

def write_file(path, content):
    Path(path).write_text(content)
    return f"Wrote {len(content)} characters to {path}"
```

```python
# tools/search_tools.py
import subprocess

def search_codebase(query):
    result = subprocess.run(
        ["rg", "--line-number", query], capture_output=True, text=True
    )
    return result.stdout or "No matches found."
```

### 6.3 A dispatch table
This maps tool names (strings from the model) to real Python functions.

```python
# tools/dispatch.py
from tools.file_tools import read_file, write_file
from tools.search_tools import search_codebase

TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "search_codebase": search_codebase,
}

def execute_tool(name, tool_input):
    fn = TOOL_FUNCTIONS[name]
    return fn(**tool_input)
```

---

## 7. Phase 3 — The ReAct Agent Loop

This replaces your Phase 1 loop. This is the core of the whole project.

```python
# agent/loop.py
from agent.llm import call_llm
from tools import TOOLS
from tools.dispatch import execute_tool

SYSTEM_PROMPT = """You are an autonomous coding agent.
Always read a file before editing it.
Explain your reasoning briefly before each tool call.
When the task is complete, respond with plain text and no tool call."""

def run_agent(user_goal, max_steps=15):
    history = [{"role": "user", "content": user_goal}]

    for step in range(max_steps):
        response = call_llm(history, tools=TOOLS, system=SYSTEM_PROMPT)
        history.append({"role": "assistant", "content": response.content})

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        if not tool_calls:
            final_text = next(b.text for b in response.content if b.type == "text")
            print(f"\n[Agent finished]: {final_text}")
            return final_text

        tool_results = []
        for call in tool_calls:
            print(f"[Tool call] {call.name}({call.input})")
            output = execute_tool(call.name, call.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": call.id,
                "content": str(output),
            })

        history.append({"role": "user", "content": tool_results})

    print("[Agent stopped: max steps reached]")
```

**What's happening each loop iteration:**
1. Send full history + tool list to the model.
2. Model replies with either a final answer or one/more tool calls.
3. If tool calls: execute them for real, wrap outputs as `tool_result` messages, append to history, loop again.
4. If no tool calls: the model considers itself done — exit the loop.

This is genuinely the entire mechanism behind every AI coding agent that exists today. Everything from here is refinement and safety.

---

## 8. Phase 4 — File Editing Without Burning Tokens

Rewriting an entire 2,000-line file every time you change one line is slow, expensive, and error-prone. Real agents use a **search-and-replace / diff-based edit tool** instead.

```python
# tools/file_tools.py (add this)
def edit_file(path, old_text, new_text):
    content = Path(path).read_text()
    if content.count(old_text) != 1:
        return "Error: old_text must match exactly once in the file."
    content = content.replace(old_text, new_text, 1)
    Path(path).write_text(content)
    return f"Edited {path}"
```

Add a matching tool schema (`old_text`, `new_text`, `path`, all required) and register it in the dispatch table. Instruct the model in the system prompt to prefer `edit_file` over `write_file` for existing files, and to always `read_file` first so it copies exact text (avoiding "old_text not found" failures from whitespace mismatches).

For larger projects, consider adopting a real diff/patch format (unified diff) applied with the `patch` command or a Python diffing library — this scales better than exact string matching.

---

## 9. Phase 5 — Sandboxing & Safe Command Execution

Never let the agent run shell commands directly against your real machine. Two options, from simplest to most robust:

### Option A — Restricted subprocess whitelist (good for learning/local use)

```python
# tools/shell_tools.py
import subprocess

ALLOWED_COMMANDS = {"pytest", "npm", "python", "ls", "cat"}

def run_command(command):
    program = command.split()[0]
    if program not in ALLOWED_COMMANDS:
        return f"Blocked: '{program}' is not an allowed command."
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    return result.stdout + result.stderr
```

### Option B — Docker sandbox (recommended for anything beyond personal use)

```python
# sandbox/docker_runner.py
import docker

client = docker.from_env()

def run_in_sandbox(command, workdir="/workspace"):
    container = client.containers.run(
        image="python:3.11-slim",
        command=f"sh -c '{command}'",
        volumes={workdir: {"bind": "/workspace", "mode": "rw"}},
        working_dir="/workspace",
        mem_limit="512m",
        network_disabled=True,
        remove=True,
        detach=False,
    )
    return container.decode()
```

The container has no network access, a memory cap, and is destroyed after each run — the agent can execute arbitrary commands inside it without endangering your host machine.

---

## 10. Phase 6 — The Test-Fix-Retest Loop

This is what turns your agent from "makes an edit" into "actually solves the bug." No new architecture is needed — `run_tests` is just another tool, and the model naturally loops: edit → run tests → read failure → edit again, because that's what the ReAct loop already does. Your job here is prompting, not code:

```python
SYSTEM_PROMPT += """
After any code change, always run the test suite using run_tests.
If tests fail, read the traceback carefully, form a hypothesis about
the root cause, and make a targeted fix. Do not guess randomly.
Stop and report to the user if the same test fails three times in a row.
"""
```

That last line matters — without it, the agent can spiral into repeated identical failed attempts and burn your API budget.

---

## 11. Phase 7 — Human-in-the-Loop Permissions

Before executing any command that isn't clearly safe (writes outside the project, deletes files, deploys, pushes to remote), pause and ask the human.

```python
# agent/loop.py (inside the tool execution section)
DESTRUCTIVE_TOOLS = {"run_command", "git_commit_and_pr"}

for call in tool_calls:
    if call.name in DESTRUCTIVE_TOOLS:
        approved = input(f"Agent wants to run: {call.input}. Allow? (y/n) ")
        if approved.lower() != "y":
            output = "User denied this action."
            tool_results.append({...})
            continue
    output = execute_tool(call.name, call.input)
```

This single gate is the most important safety feature in the whole project — treat it as non-negotiable, not a "nice to have."

---

## 12. Phase 8 — Context Window Management

Once your agent works on real repositories, you'll overflow the context window. Techniques, roughly in order of implementation difficulty:

1. **Truncate old tool outputs** — once a `read_file` result is several turns old and no longer relevant, replace it in history with `"[file content omitted, already processed]"`.
2. **Summarize instead of resending** — periodically ask the LLM to summarize the conversation so far into a few sentences, and replace older messages with that summary.
3. **Selective file loading** — only load files the model has explicitly asked for via `search_codebase` or `read_file`, never the whole repo.
4. **Chunked reading** — for huge files, always read by `start_line`/`end_line` range rather than the whole file.
5. **Token counting** — use the Anthropic token counting endpoint (or `tiktoken` for OpenAI) to track usage and trigger summarization proactively before you hit the limit, not after an error.

---

## 13. Phase 9 — Git & GitHub Integration

```python
# tools/git_tools.py
import git
from github import Github
import os

def git_commit_and_pr(branch_name, commit_message, repo_path="."):
    repo = git.Repo(repo_path)
    repo.git.checkout("-b", branch_name)
    repo.git.add(A=True)
    repo.index.commit(commit_message)
    origin = repo.remote(name="origin")
    origin.push(branch_name)

    gh = Github(os.environ["GITHUB_TOKEN"])
    gh_repo = gh.get_repo("your-username/your-repo")
    pr = gh_repo.create_pull(
        title=commit_message,
        body="Automated change by AI coding agent.",
        head=branch_name,
        base="main",
    )
    return f"Opened PR: {pr.html_url}"
```

Add `GITHUB_TOKEN` (a personal access token with repo scope) to your `.env`. Gate this tool behind the human-approval check from Phase 7 — pushing and opening PRs should never happen silently.

---

## 14. Phase 10 — Terminal UX Polish

A few small additions make the agent dramatically nicer to use:

- **`rich` library** for colored output, spinners while waiting on the LLM, and syntax-highlighted diffs.
- **Streaming responses** — use the streaming variant of the API call so text appears as it's generated instead of after a long pause.
- **Step counter display** — show `[Step 3/15]` so the user knows how much budget is left.
- **Diff previews** — before writing a file, print a colored unified diff of old vs. new content so the human can see the change at a glance.

```python
from rich.console import Console
from rich.syntax import Syntax
console = Console()
console.print(Syntax(diff_text, "diff", theme="monokai"))
```

---

## 15. Phase 11 — Advanced Features

Once the core loop is solid, these separate a toy project from a genuinely powerful tool:

- **Sub-agents / multi-agent delegation** — a "planner" agent breaks a large task into sub-tasks, each handed to a fresh "worker" agent with its own clean context window.
- **Persistent memory** — store facts learned about the codebase (e.g., "this repo uses Poetry, not pip") in a local file or vector database so future sessions don't relearn them.
- **Semantic code search** — replace plain `ripgrep` search with an embeddings-based search (e.g., using a vector database like Chroma or LanceDB) so the agent can find *conceptually* related code, not just exact text matches.
- **Cost/token dashboards** — log every API call's token usage and running dollar cost to a file.
- **Checkpointing** — save agent state to disk after each step so a crashed session can resume instead of restarting.
- **Multi-model routing** — use a cheaper/faster model for simple file reads and a stronger model only for the actual reasoning/planning steps, to cut cost.

---

## 16. Full Tech Stack Reference Table

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.10+ | Best LLM tooling ecosystem |
| LLM API | Anthropic SDK (`anthropic`) or OpenAI SDK | Native tool-calling support |
| Orchestration (optional) | LangGraph | Only if you want prebuilt cyclic-graph state management instead of hand-rolling the loop |
| Code search | `ripgrep` (`rg`) via subprocess | Extremely fast text search |
| Sandboxing | Docker SDK for Python | Isolated, network-disabled command execution |
| Version control | `GitPython` | Programmatic git operations |
| GitHub integration | `PyGithub` | Create branches, PRs via API |
| Terminal UI | `rich` | Colors, diffs, spinners, streaming |
| Config/secrets | `python-dotenv` | Keep API keys out of source |
| Testing | `pytest` | Both for your own agent's tests and as a tool the agent invokes on target repos |
| Token counting | Anthropic token-count endpoint / `tiktoken` | Context window management |
| (Advanced) Vector search | `chromadb` or `lancedb` | Semantic code search |

---

## 17. Suggested Build Order (Milestones)

Work through these in order; each is a fully working, demoable checkpoint.

1. **Milestone 1:** Plain chat loop (Phase 1) — talk to the model, nothing else.
2. **Milestone 2:** Add `read_file` and `search_codebase` only — a read-only "codebase Q&A" agent.
3. **Milestone 3:** Add `write_file`/`edit_file` with human approval before every write — a supervised editing agent.
4. **Milestone 4:** Add `run_tests` and the fix-retest prompting — an agent that can actually resolve a failing test on a toy repo.
5. **Milestone 5:** Wrap shell commands in Docker sandboxing — safe to leave semi-unattended.
6. **Milestone 6:** Add git/GitHub tools — agent opens real PRs.
7. **Milestone 7:** Add context management + terminal polish — usable on real, large repositories.
8. **Milestone 8 (stretch):** Sub-agents, semantic search, memory, cost dashboard.

Do not skip to Milestone 4 before Milestones 2–3 work reliably — most of the hard bugs (malformed tool calls, infinite loops, bad edits) show up early and are much easier to debug in a small, read-only agent.

---

## 18. Learning Resources

- Anthropic's tool-use documentation (docs.claude.com) — the exact schema and message format used above.
- The ReAct paper ("ReAct: Synergizing Reasoning and Acting in Language Models") — the original research behind this pattern.
- Open-source reference implementations to read (not copy) once your own version works: Aider, OpenHands (formerly OpenDevin), and SWE-agent — all are real, working coding agents with public source code showing production-grade versions of every phase above.

---

**Where to start today:** create the project skeleton in Section 4, get Phase 1's plain chat loop running, and add exactly one tool (`read_file`) before doing anything else. Everything past that point is repetition of the same pattern with more tools and more safety rails.
