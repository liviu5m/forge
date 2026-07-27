# Forge: An Autonomous Coding Agent

**Forge** is a self‑directed, autonomous coding agent designed to assist developers by intelligently interacting with a codebase, executing custom tools, and managing sessions with minimal human intervention. It combines natural‑language prompting with a robust plugin‑style tool registry to automate tasks ranging from file manipulation to complex code‑analysis workflows.

---  

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [Architectural Overview](#architectural-overview)  
4. [Core Modules](#core-modules)  
5. [Tool Registry & Dispatch](#tool-registry--dispatch)  
6. [Session Management](#session-management)  
7. [Large Language Model (LLM) Integration](#llm-integration)  
8. [Secure Tool Execution & Human‑in‑the‑Loop Gate](#secure-tool-execution--human‑in‑the‑loop-gate)  
9. [Running Tests](#running-tests)  
10. [Configuration & Environment](#configuration--environment)  
11. [Contributing & Development Workflow](#contributing--development-workflow)  
12. [License & Attribution](#license--attribution)  

---  

## 1. Project Overview
Forge lives in a single root directory (`/home/liviu/code/projects/forge`) and consists of roughly 20 files and several sub‑directories (`agent/`, `tests/`, `sandbox/`, `tools/`). It is deliberately lightweight, exposing only a handful of entry points while keeping utilities modular and extensible.

---  

## 2. Key Features

| Feature | Description |
|---|---|
| **Autonomous Session Management** | `initiate_session()` lists, loads, or creates named sessions, persisting conversation history on disk. |
| **Tool‑Driven Execution** | A registry (`TOOL_REGISTRY`) maps human‑readable tool names to callable functions; the LLM can request tools via a secure dispatch mechanism (`safe_dispatch`). |
| **LLM‑Backed Reasoning** | Calls to `call_llm()` use a fallback chain (OpenRouter → Groq → Gemini → etc.) and can embed *tool calls* directly in the model’s output, enabling the agent to self‑drive. |
| **Pruned Conversation History** | `prune_message_history()` limits context size by truncating large tool outputs, preserving only the most recent relevant turns. |
| **Secure Human‑in‑the‑Loop Permission Gate** | Destructive tools (`write_file`, `edit_file`, `run_terminal_commands`) trigger a vivid permission prompt requiring explicit user affirmation before execution. |
| **Automatic Context Pruning & Optimization** | System enforces a maximum of 4 recent turns, ensuring the LLM stays within token limits while still preserving critical instructions. |
| **Extensible CLI‑Like Interface** | The interactive REPL loop supports commands such as `clear`, `exit`, and inline code execution via natural language. |
| **Test Runner Integration** | `run_tests()` executes test suites (currently using `pytest`) to validate changes automatically after file modifications. |
| **Modular Codebase** | Core responsibilities are split into clear modules (`loop.py`, `llm.py`, `memory.py`, `prompts.py`, `read_file.py`, etc.) encouraging plug‑in development. |

---  

## 3. Architectural Overview
```
forge/
│
├─ .env                 # optional env vars (e.g., LITELLM_*)
├─ .gitignore
├─ main.py              # entry point – launches `run()`
├─ README.md            # this file
├─ requirements.txt
│
├─ agent/               # core agent logic
│   ├─ loop.py          # session handling, REPL loop, run() entry
│   ├─ llm.py           # LLM wrapper with fallbacks
│   ├─ memory.py        # session persistence helpers
│   ├─ prompts.py       # default and custom prompts
│   └─ ...             
│
├─ tools/               # tool definitions & utilities
│   ├─ read_file.py
│   ├─ write_file.py
│   ├─ run_terminal_commands.py
│   └─ codebase.py
│
└─ tests/               # pytest based test suite
    ├─ run_tests.py
    └─ test_tools.py
```

The **flow** starts with `main.py`, which imports and calls `run(initiate_session())`. `initiate_session()` either loads an existing session or starts a fresh one, after which `run()` enters an infinite REPL that:

1. Receives user input.  
2. Sends *optimized* history to `call_llm()`.  
3. Parses any tool calls embedded in the LLM response.  
4. Dispatches them through `safe_dispatch()`.  
5. Persists the updated message history back to disk.

---  

## 4. Core Modules

| Module | Purpose | Notable Functions |
|--------|---------|-------------------|
| `agent/loop.py` | Handles session interaction, message pruning, and dispatch loop. | `initiate_session()`, `run()`, `safe_dispatch()` |
| `agent/llm.py` | Wrapper around `litellm.completion` with a rich fallback chain. | `call_llm()` |
| `agent/memory.py` | Persists and retrieves named session histories. | `list_sessions()`, `load_session()`, `save_session()` |
| `tools/read_file.py` | Minimal wrapper for reading file contents (used by the agent). | `read_file()` |
| `tools/write_file.py` | Provides a safe wrapper for writing files, integrated with the permission gate. | `write_file()` |
| `tools/run_terminal_commands.py` | Executes arbitrary shell commands safely. | `run_terminal_commands()` |
| `tools/codebase.py` | Offers utilities for searching/analyzing the codebase. | `search_codebase_keywords()` etc. |

---  

## 5. Tool Registry & Dispatch

### 5.1 Registry Definition
```python
TOOL_REGISTRY = {
    "read_file": read_file,
    "write_file": write_file,
    "run_terminal_commands": run_terminal_commands,
    # ...additional tools can be added here
}
```

### 5.2 Dispatch Mechanism (`safe_dispatch`)
- **Input Validation**: Uses `inspect.signature()` to ensure all required parameters are present and correctly typed.  
- **Destructive‑Tool Gate**: Functions like `write_file`, `edit_file`, and `run_terminal_commands` pause execution and request explicit human confirmation (`y`/`n`).  
- **Error Handling**: Returns detailed error strings that the LLM can interpret to self‑correct.  

### 5.3 Example Tool Call Flow
1. LLM outputs:  
   ```json
   {"tool_calls":[{"id":"call-1","type":"function","function":{"name":"write_file","arguments":{"path":"README.md","content":"# New Section\\n...","target_content":"... "}}}]}  
   ```
2. Agent parses the call, extracts `path` and `content`.  
3. Calls `safe_dispatch(write_file, {"path":"README.md","content":"# New Section\n..."}, "write_file")`.  
4. Gate appears, user confirms → operation proceeds → new content is persisted.  

---  

## 6. Session Management

- **Naming**: Sessions are identified by a user‑defined string (default: `"default_session"`).  
- **Persistence**: Histories are stored in `agent_sessions.db` (SQLite‑like or JSON‑based depending on implementation).  
- **Pruning**: Old messages are truncated by `prune_message_history()` to keep the context within token limits.  
- **Commands**:  
  - `clear` – empties the current session history.  
  - `exit` – terminates the REPL.  
  - Numbered selection – loads an existing session.  
  - Free‑form input – creates a new session name.  

---  

## 7. Large Language Model (LLM) Integration

- **Primary Model**: Calls are made to the free tier of **OpenRouter** (`openrouter/openrouter/free`).  
- **Fallback Chain**: If the primary endpoint fails, the library automatically retries with a list of backup providers:  
  1. OpenRouter free OpenAI model (`gpt-oss-20b`)  
  2. Gemini‑1.5‑flash  
  3. NVIDIA’s Nemotron‑3‑ultra‑550b (free tier)  
  4. Qwen3‑coder (free)  
  5. Groq Llama‑3.3‑70b‑versatile  
  6. Groq Llama‑3.1‑8b‑instant  

- **Parameters**:  
  - `max_tokens=4096` (adjustable)  
  - `tools` – passes the `TOOL_REGISTRY` list so the model knows which functions are available.  
  - `tool_choice` – optional flag for forcing a specific tool.  

- **Structured Output**: The agent extracts *tool calls* from the raw response text using regexes that locate JSON blocks, parses them, and maps them onto the `TOOL_REGISTRY`.

---  

## 8. Secure Tool Execution & Human‑in‑the‑Loop Gate

When an LLM‑initiated tool call matches a **destructive** function (`write_file`, `edit_file`, `run_terminal_commands`):

1. The system prints a **security banner**:  

   ```
   🛡️  [SECURITY GATE] Action Required: **write_file**
   ───────────────────────────────────────
   ```
2. It prints a verbose representation of the provided arguments (e.g., file path & content).  
3. The user is prompted: `Do you want to allow this action? [y/N]:`.  
4. Acceptance (`y`/`yes`) proceeds; any other input aborts with an explicit error message fed back to the LLM.  

This gate protects against accidental file overwrites or command execution in production environments.

---  

## 9. Running Tests

- **Runner**: `run_tests()` located in `tests/run_tests.py`.  
- **Framework**: Default is `pytest`; can be overridden via the `test_framework` argument.  
- **Usage Example**:  

  ```bash
  python -m pytest tests/
  # or via the agent:
  run_tests(file_path="tests/test_tools.py")
  ```

- **Continuous Integration**: After any file modification (e.g., after updating `README.md`), the agent automatically calls `run_tests()` to verify that the changes did not break existing functionality.

---  

## 10. Configuration & Environment

| Variable | Description |
|----------|-------------|
| `LITELLM_LOG` (set in `.env`) | Controls logging verbosity for LiteLLM (`ERROR` suppresses debug output). |
| `API_KEY` (if needed) | For paid providers; usually left empty when using free fallback models. |
| `DOTENV` loading | `load_dotenv()` reads `.env` automatically at start‑up. |

**Tip**: To change the model endpoint, edit `agent/llm.py` – replace the `model` argument in `completion()` with your preferred model identifier.

---  

## 11. Contributing & Development Workflow

1. **Fork** the repository and clone locally.  
2. Create a **feature branch** (`git checkout -b feat/your-feature`).  
3. Add/modify modules following the existing structure (`agent/`, `tools/`).  
4. Write **unit tests** under `tests/` for any new functionality.  
5. Run the test suite locally:  

   ```bash
   python tests/run_tests.py
   ```
6. Commit with a clear message and push.  
7. Open a **Pull Request**; the CI pipeline will automatically execute `run_tests.py` and verify linting.  

> **Note**: All destructive changes (e.g., editing core files) must pass the human‑in‑the‑loop gate before merging.

---  

## 12. License & Attribution

Forge is released under the **MIT License** (see `LICENSE` file).  
The project leverages the following open‑source components:

- **LiteLLM** – unified wrapper for many LLM providers.  
- **OpenRouter** – free tier for model inference.  
- **llama.cpp / llama‑models** – underlying open‑source inference engines used by free fallback providers.  

Please acknowledge these dependencies when using Forge in commercial or public contexts.

---  

# Using Forge Effectively

1. **Start a Session** – Run `python main.py` and type a name (e.g., `my_project`) or press <Enter> for the default.  
2. **Ask the Agent** – Type natural‑language instructions (e.g., “Create a new Python file `utils.py` that implements a decorator `cached`”).  
3. **Watch the Agent** – It will display the pruned conversation, request confirmations where needed, and automatically persist the updated history.  
4. **Validate** – After each batch of changes, the agent runs the test suite to ensure stability.  

Happy coding with an AI‑powered partner! 🚀  

---  

*Document generated on 2025‑11‑03 – last updated to reflect the current codebase snapshot.*