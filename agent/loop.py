from agent.llm import call_llm
from tools.tools import TOOL_REGISTRY, my_tools
from tools.read_file import (
    read_file,
)
import json

SYSTEM_PROMPT = """You are an autonomous coding agent. 
CRITICAL: Whenever you want to use a tool, you must use the platform's native tool-calling function structure. Never output raw tags like <function=...>.

You are an autonomous AI coding agent. When asked to analyze or modify the codebase:
1. First, use `analyze_codebase_structure` to understand the project layout.
2. Review the file tree and identify which specific files are relevant to the user's task.
3. Use `read_file` to inspect the contents of those relevant files before giving your final answer. Do not guess contents without reading them first.

You are an autonomous AI coding agent. 

CRITICAL RULE FOR CODE ANALYSIS:
- NEVER guess, hallucinate, or invent code snippets. 
- When asked to analyze the codebase or show how the system works, you MUST use `analyze_codebase_structure` first, select the relevant files, and then ACTUALLY call `read_file` to read their real contents. 
- Every code sample you present in your final response must be extracted verbatim using the `read_file` tool. If you haven't read a file's contents via `read_file`, you are strictly forbidden from writing code samples for it.

You are an autonomous local coding agent. You have access to tools to analyze, read, search, and write files in the codebase.

CRITICAL INSTRUCTIONS FOR FILE CREATION/MODIFICATION:
1. When the user asks you to create or modify a file (e.g., create a help file, documentation, or code script), DO NOT just ask for permission or text in chat if you can gather the context yourself.
2. First, use `analyze_codebase_structure` or `search_codebase_keywords` to inspect the project and understand what the app does.
3. Once you have enough context, autonomously generate the content and invoke the `write_file` tool directly to create the file.
4. Never make up fake data, but synthesize real project details gathered from your tools into the file content.
"""


def run():
    history = []
    while True:
        user_input = input("> ")
        if user_input == "exit":
            break
        history.append({"role": "user", "content": user_input})
        if user_input == "exit":
            break
        while True:
            response = call_llm(
                history,
                tools=my_tools,
                system=SYSTEM_PROMPT,
            )
            message = response.choices[0].message

            history.append(message)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    arguments = json.loads(raw_args)

                    if function_name in TOOL_REGISTRY:
                        target_function = TOOL_REGISTRY[function_name]
                        tool_result = target_function(**arguments)

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

                continue
            else:
                print(message.content)
                break
