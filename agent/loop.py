from agent.llm import call_llm
from tools.tools import TOOL_REGISTRY, my_tools
from tools.read_file import (
    read_file,
)
import json

SYSTEM_PROMPT = """You are an autonomous coding agent. 
CRITICAL: Whenever you want to use a tool, you must use the platform's native tool-calling function structure. Never output raw tags like <function=...>.
"""


def run():
    history = []
    while True:
        user_input = input("> ")
        if user_input == "exit":
            break
        history.append({"role": "user", "content": user_input})
        response = call_llm(
            history,
            tools=my_tools,
            system=SYSTEM_PROMPT,
        )
        message = response.choices[0].message
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
                else:
                    print(
                        f"Error: Tool '{function_name}' was requested by LLM, but is not registered."
                    )
        else:
            print(message.content)
        history.append({"role": "assistant", "content": message.content})
