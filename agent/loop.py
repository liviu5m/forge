from types import SimpleNamespace

from agent.llm import call_llm
from agent.memory import list_sessions, load_session, save_session
from tools.tools import TOOL_REGISTRY, my_tools
from tools.read_file import (
    read_file,
)
import json
import inspect
from typing import Callable, Any
import os
import json
import re

SYSTEM_PROMPT = """You are an autonomous coding agent. 
CRITICAL ENFORCEMENT: 
- DO NOT answer in plain text if a tool can be used to fulfill the user's request. 
- Always prefer calling a tool over asking the user for information.
CRITICAL TOOL-CALLING RULE:
- Whenever you want to use a tool, you must use the platform's native tool-calling function structure. Never output raw tags like <function=...>.

TASK CLASSIFICATION & EFFICIENCY:
- For simple, isolated tasks (e.g., writing a standalone text file, answering general coding logic, or running a direct command), DO NOT waste time analyzing the entire codebase structure. Just perform the task directly.
- For tasks requiring codebase integration, context, or modification of existing files, follow the rigorous workflow below.

WORKFLOW FOR CODEBASE & FILE MODIFICATION TASKS:
1. First, use `analyze_codebase_structure` or `search_codebase_keywords` to understand the project layout before guessing or editing.
2. NEVER guess, hallucinate, or invent code snippets. When referencing existing files, you MUST use `read_file` to inspect their contents verbatim.
3. When creating or modifying files (`write_file` or `edit_file`), autonomously generate the content using real project details gathered from your tools.
4. Whenever you modify or create a file, you MUST immediately call `run_tests` (or `run_terminal_commands` to run tests) to verify your changes for errors before responding to the user.

You have access to a set of specialized tools:
- Use `read_file` to view file contents.
- Use `analyze_codebase_structure` to inspect directory layouts and project architecture.
- Use `search_codebase_keywords` to find specific symbols or keywords across source files.
- Use `write_file` or `edit_file` to create or modify code.
- Use `run_tests` to execute unit tests and verify functionality.
- Use `run_type_check` to run MyPy static type checking and catch type errors.
- Use `run_security_audit` to run Bandit security linting and detect vulnerabilities.
- Use `extract_symbols` to explore file structures quickly instead of reading whole files blindly.
- Use `preview_diff` to visually check changes before applying them.

Guidelines for execution:
- Run `run_type_check` to validate code health.
- Run `run_security_audit` to validate code health.
- Use `extract_symbols` to explore file structures quickly instead of reading whole files blindly.
- Use `preview_diff` before applying complex edits.
"""


def initiate_session() -> str:
    """
    Displays past sessions and prompts the user to either
    select an existing session or create/type a new one.
    """
    sessions = list_sessions()

    print("\n" + "─" * 50)
    print("📂 SESSION MANAGER")
    print("─" * 50)

    if sessions:
        print("Available previous sessions:")
        for idx, session in enumerate(sessions, start=1):
            print(f"  {idx}. {session}")
    else:
        print("No previous sessions found.")

    print("\nOptions:")
    print("- Enter a number to load an existing session.")
    print("- Type a new name to create a fresh session.")
    print("- Press Enter directly to use 'default_session'.")
    print("─" * 50)

    choice = input("Select or create session > ").strip()

    if not choice:
        return "default_session"

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            selected_session = sessions[idx]
            print(f"✔️ Resumed session: '{selected_session}'")
            return selected_session
        else:
            print("⚠️ Invalid session number. Creating a new session with that input.")

    return choice


def print_session_history(history):
    for msg in history:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        print(
            f"  [{role}]: {content[:100]}..."
            if len(content) > 100
            else f"  [{role}]: {content}"
        )


def prune_message_history(messages, max_recent_turns=4):
    """
    Truncates bulky tool outputs from older turns while preserving
    user instructions, assistant turns, and the most recent interactions.
    """
    pruned_messages = []
    total_messages = len(messages)

    cutoff_index = max(0, total_messages - (max_recent_turns * 2))

    for i, msg in enumerate(messages):
        # Preserve the most recent interactions based on cutoff index
        if i >= cutoff_index:
            pruned_messages.append(msg)
            continue

        # For older messages containing heavy tool data or outputs, truncate them
        if (
            msg.get("role") == "tool"
            or msg.get("function_call")
            or msg.get("tool_calls")
        ):
            truncated_msg = msg.copy()
            if (
                isinstance(truncated_msg.get("content"), str)
                and len(truncated_msg["content"]) > 300
            ):
                truncated_msg["content"] = (
                    "[Old tool output truncated for context length optimization]"
                )
            pruned_messages.append(truncated_msg)
        else:
            pruned_messages.append(msg)

    return pruned_messages


def run(session_name: str):
    print(f"🚀 Initiating session '{session_name}'...")

    history = load_session(session_name)

    if history:
        print(f"Resumed past session with {len(history)} messages.")
        print_session_history(history)
    else:
        print("Starting a fresh session.")
    while True:
        user_input = input("> ")
        if session_name == "default_session":
            session_name = user_input
        if user_input == "exit":
            break
        if user_input.strip() == "clear":
            history.clear()
            os.system("cls" if os.name == "nt" else "clear")
            continue
        history.append({"role": "assistant", "content": user_input})
        if user_input == "exit":
            break
        while True:
            optimized_history = prune_message_history(history, max_recent_turns=4)
            response = call_llm(
                optimized_history,
                tools=my_tools,
                system=SYSTEM_PROMPT,
            )
            message = response.choices[0].message
            msg_dict = {"role": "assistant", "content": message.content}
            if hasattr(message, "tool_calls") and message.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            history.append(msg_dict)

            # if not getattr(message, "tool_calls", None) and message.content:
            #     json_match = re.search(
            #         r"```(?:json)?\s*({.*?})\s*```", message.content, re.DOTALL
            #     )
            #     if not json_match:
            #         json_match = re.search(r"({.*?})", message.content, re.DOTALL)
            #
            #     if json_match:
            #         try:
            #             parsed_json = json.loads(json_match.group(1))
            #             if "function" in parsed_json:
            #                 func_name = parsed_json["function"]
            #                 func_args = parsed_json.get("parameters", {})
            #
            #                 # Build a clean namespace object matching the expected structure
            #                 mock_call = SimpleNamespace(
            #                     id="fallback_call_1",
            #                     type="function",
            #                     function=SimpleNamespace(
            #                         name=func_name,
            #                         arguments=json.dumps(func_args),
            #                     ),
            #                 )
            #
            #                 setattr(message, "tool_calls", [mock_call])
            #                 print(
            #                     f"\n[SYSTEM] Caught text-based tool call for '{func_name}', routing to native execution loop."
            #                 )
            #         except json.JSONDecodeError:
            #             pass
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    arguments = json.loads(raw_args)

                    if function_name in TOOL_REGISTRY:
                        target_function = TOOL_REGISTRY[function_name]
                        tool_result = safe_dispatch(
                            target_function, arguments, function_name
                        )
                        print(f"[{function_name}] Executed successfully.")
                        print(tool_result)

                        history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(tool_result),
                            }
                        )
                    else:
                        error_msg = f"Error: Tool '{function_name}' was requested by LLM, but is not registered."
                        print(error_msg)
                        history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": error_msg,
                            }
                        )
                    save_session(session_name, history)
                continue
            else:
                print(message.content)
                break

        save_session(session_name, history)


def safe_dispatch(
    target_function: Callable[..., Any], arguments: dict, function_name: str
) -> str:
    """
    Safely dispatches arguments to a function, catching missing parameters,
    unexpected arguments, or type mismatches by inspecting the function signature.

    Args:
        target_function: The callable tool function to execute.
        arguments: A dictionary of key-value arguments provided by the LLM.

    Returns:
        The result of the function execution as a string, or an error message
        formatted for the LLM to understand and self-correct.
    """
    destructive_tools = {"write_file", "edit_file", "run_terminal_commands"}
    if function_name in destructive_tools:
        print("\n" + "─" * 60)
        print(f"🛡️  [SECURITY GATE] Action Required: **{function_name}**")
        print("─" * 60)

        if "path" in arguments:
            print(f"📁 Target File: {arguments['path']}")
        elif "file_path" in arguments:
            print(f"📁 Target File: {arguments['file_path']}")

        for key, value in arguments.items():
            if key in ["path", "file_path"]:
                continue

            print(f"🔹 {key.replace('_', ' ').capitalize()}:")
            if key == "content" and isinstance(value, str):
                indented_content = "\n".join(
                    ["    " + line for line in value.splitlines()]
                )
                print(indented_content)
            elif key == "target_content" or key == "new_content":
                print(f"    ```\n{value}\n    ```")
            else:
                print(f"    {value}")

        print("─" * 60)

        while True:
            choice = input("Do you want to allow this action? [y/N]: ").strip().lower()
            if choice in ["y", "yes"]:
                print("✔️ Action approved by user.\n")
                break
            elif choice in ["n", "no", ""]:
                print("❌ Action rejected by user.\n")
                return "Error: Tool execution aborted by user via Human-in-the-Loop permission gate."
            else:
                print("Please enter 'y' or 'n'.")
    try:
        sig = inspect.signature(target_function)

        bound_args = sig.bind(**arguments)
        bound_args.apply_defaults()

        result = target_function(*bound_args.args, **bound_args.kwargs)

        return str(result)

    except TypeError as e:
        return (
            f"Error: Invalid tool arguments provided ({str(e)}). "
            "Please check the required parameter names and types for this tool and try again."
        )
    except Exception as e:
        return f"Error executing tool: {str(e)}"
