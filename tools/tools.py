from tests.run_tests import run_tests
from tools.codebase import analyze_codebase_structure, search_codebase_keywords
from tools.read_file import read_file
from tools.write_file import edit_file, write_file

TOOL_REGISTRY = {
    "read_file": read_file,
    "analyze_codebase_structure": analyze_codebase_structure,
    "search_codebase_keywords": search_codebase_keywords,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_tests": run_tests,
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

write_file_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Create a new file or overwrite an existing file with new content.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The destination path of the file to write (e.g., 'src/utils.py')",
                },
                "content": {
                    "type": "string",
                    "description": "The full text content to write into the file.",
                },
            },
            "required": ["path", "content"],
        },
    },
}

edit_file_schema = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": "Replaces a specific text snippet inside an existing file with new content. Use this for targeted code updates instead of rewriting the whole file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to edit.",
                },
                "target_content": {
                    "type": "string",
                    "description": "The exact existing text or code block to look for and replace.",
                },
                "new_content": {
                    "type": "string",
                    "description": "The new text or code block that will replace the target content.",
                },
            },
            "required": ["path", "target_content", "new_content"],
        },
    },
}

run_tests_schema = {
    "type": "function",
    "function": {
        "name": "run_tests",
        "description": "Execute unit tests on a specified test file using python3.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the test file to execute (e.g., tests/test_math.py)",
                },
                "test_framework": {
                    "type": "string",
                    "description": "Testing framework to use, defaults to pytest.",
                },
            },
            "required": ["file_path"],
        },
    },
}

my_tools = [
    read_file_schema,
    analyze_codebase_structure_schema,
    search_codebase_keywords_schema,
    write_file_schema,
    edit_file_schema,
    run_tests_schema,
]
