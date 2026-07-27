import subprocess
import ast
import difflib


def run_type_check(path: str = ".") -> str:
    """
    Runs MyPy static type checking on the repository or specified path to catch type errors.

    Args:
        path: The file or directory path to type-check (defaults to current directory ".")
    """
    try:
        result = subprocess.run(
            ["mypy", path], capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            return f"Type check passed with no errors:\n{output}"
        return f"Type check found errors:\n{output}"
    except FileNotFoundError:
        return "Error: 'mypy' is not installed in the environment."
    except Exception as e:
        return f"Error running type check: {str(e)}"


def run_security_audit(path: str = ".") -> str:
    """
    Runs Bandit security linting on the codebase to detect vulnerabilities.

    Args:
        path: The file or directory path to audit (defaults to current directory ".")
    """
    try:
        result = subprocess.run(
            ["bandit", "-r", path, "-f", "txt"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            return f"Security audit passed with no high-risk vulnerabilities:\n{output}"
        return f"Security audit discovered potential issues:\n{output}"
    except FileNotFoundError:
        return "Error: 'bandit' is not installed in the environment."
    except Exception as e:
        return f"Error running security audit: {str(e)}"


def extract_symbols(file_path: str) -> str:
    """
    Parses a Python file using AST to extract all classes, functions,
    their signatures, and docstrings cleanly.

    Args:
        file_path: Path to the Python file to analyze.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)

        symbols = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                symbols.append(
                    f"Function: {node.name}({', '.join(args)}) [Line {node.lineno}]"
                )
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                symbols.append(
                    f"Class: {node.name} (Methods: {', '.join(methods)}) [Line {node.lineno}]"
                )

        if not symbols:
            return f"No classes or functions found in {file_path}."
        return f"Symbols found in {file_path}:\n" + "\n".join(symbols)
    except Exception as e:
        return f"Error parsing AST for {file_path}: {str(e)}"


def preview_diff(file_path: str, new_content: str) -> str:
    """
    Generates a unified diff comparing the existing file content
    with the proposed new content.

    Args:
        file_path: Path to the target file.
        new_content: The proposed new text content for the file.
    """
    try:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                old_content = f.read()
        except FileNotFoundError:
            old_content = ""

        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3,
        )

        diff_text = "".join(diff)
        if not diff_text:
            return "No changes detected between old and new content."

        return f"Diff Preview for {file_path}:\n```diff\n{diff_text}\n```"
    except Exception as e:
        return f"Error generating diff preview: {str(e)}"
