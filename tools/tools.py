from tools.codebase import analyze_codebase_structure, search_codebase_keywords
from tools.read_file import read_file

TOOL_REGISTRY = {
    "read_file": read_file,
    "analyze_codebase_structure": analyze_codebase_structure,
    "search_codebase_keywords": search_codebase_keywords,
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

search_codebase_keywords_schema = {
    "type": "function",
    "function": {
        "name": "search_codebase_keywords",
        "description": "Search for a specific keyword, function name, or string pattern across all source files in the codebase.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "The keyword or text string to search for in the codebase.",
                },
                "directory_path": {
                    "type": "string",
                    "description": "The root directory path to search within (defaults to current directory '.').",
                },
            },
            "required": ["keyword"],
        },
    },
}

analyze_codebase_structure_schema = {
    "type": "function",
    "function": {
        "name": "analyze_codebase_structure",
        "description": "Analyze the directory layout, compile a file tree map, and get a structural overview of the project architecture.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "The root directory path to analyze (defaults to current directory '.').",
                }
            },
            "required": [],
        },
    },
}
my_tools = [
    read_file_schema,
    analyze_codebase_structure_schema,
    search_codebase_keywords_schema,
]
