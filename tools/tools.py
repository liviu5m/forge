from tools.read_file import read_file


def get_current_temperature(location: str):
    return f"The temperature in {location} is 22°C."


TOOL_REGISTRY = {
    "read_file": read_file,
}
read_file_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file, optionally a line range.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read (e.g., 'src/main.py')",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional starting line number (1-based index).",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional ending line number (1-based index).",
                },
            },
            "required": ["path"],
        },
    },
}
my_tools = [read_file_schema]
