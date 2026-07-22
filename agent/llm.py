from typing import Any, List, Optional
from dotenv import load_dotenv
from litellm import completion
import os

load_dotenv()
os.environ["LITELLM_LOG"] = "ERROR"


def call_llm(
    messages,
    tools: Optional[List[Any]] = None,
    tool_choice: Optional[str] = None,
    system: str = "",
):
    """
    Calls the primary model with an automatic fallback chain spanning Groq,
    Google AI Studio, and OpenRouter free-tier models. If the primary model
    hits rate limits or errors, LiteLLM automatically shifts to the next backup.
    """
    try:
        response = completion(
            model="openrouter/openrouter/free",
            messages=messages,
            fallbacks=[
                "openrouter/openai/gpt-oss-20b:free",
                "gemini/gemini-1.5-flash",
                "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
                "openrouter/qwen/qwen3-coder:free",
                "groq/llama-3.3-70b-versatile",
                "groq/llama-3.1-8b-instant",
            ],
            max_tokens=4096,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print(f"All free fallback providers exhausted: {e}")
        raise
