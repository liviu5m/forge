import os
from pathlib import Path
import subprocess
from typing import Optional


def search_codebase_keywords(keyword: str, directory_path: Optional[str] = ".") -> str:
    """
    Searches for a keyword across the codebase, using the existing path resolution logic
    from read_file and performance search tools.
    """
    try:
        target_path = Path(directory_path) if directory_path else Path(".")

        if not target_path.exists():
            filename = target_path.name
            matches = list(Path(".").rglob(filename))

            if len(matches) == 1:
                target_path = matches[0]
            elif len(matches) > 1:
                match_str = ", ".join(str(m) for m in matches)
                return f"Error: Multiple paths found for '{filename}': [{match_str}]. Please specify the exact path."
            else:
                return (
                    f"Error: Path or file '{directory_path}' not found in the codebase."
                )

        search_target = str(target_path)

        try:
            cmd = [
                "rg",
                "-C",
                "20",
                "--heading",
                "--line-number",
                keyword,
                search_target,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0 and result.stdout.strip():
                matches = result.stdout.strip()
                if len(matches) > 4000:
                    return matches[:4000] + "\n\n[Output truncated due to length...]"
                return matches
        except FileNotFoundError:
            pass
        is_git_repo = Path(".git").exists()
        if is_git_repo:
            cmd = ["git", "grep", "-n", "-C", "20", keyword, search_target]
        else:
            cmd = ["grep", "-r", "-n", "-C", "20", "-I", "-i", keyword, search_target]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode != 0 or not result.stdout.strip():
            return f"No matches found for keyword '{keyword}' in '{directory_path}'."

        matches = result.stdout.strip()
        if len(matches) > 4000:
            return matches[:4000] + "\n\n[Output truncated due to length...]"
        return matches

    except Exception as e:
        return f"Error executing search: {str(e)}"


def analyze_codebase_structure(directory_path: str = ".") -> str:
    """
    Analyzes the directory structure, lists all code files recursively,
    and gives a structural overview of the project architecture.
    """
    base_dir = Path(directory_path)
    if not base_dir.exists():
        return f"Error: Directory {directory_path} does not exist."

    ignored_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
    }

    tree_lines = []
    file_inventory = []

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        rel_root = Path(root).relative_to(base_dir)
        indent_level = len(rel_root.parts)
        indent = "    " * indent_level

        if str(rel_root) != ".":
            tree_lines.append(f"{indent}📁 {Path(root).name}/")

        file_indent = "    " * (indent_level + 1)
        for file in files:
            if file.endswith((".pyc", ".png", ".lock")):
                continue
            tree_lines.append(f"{file_indent}📄 {file}")
            file_inventory.append(str(base_dir / rel_root / file))

    overview = (
        f"=== Project Structure Overview ===\n"
        f"Root Directory: {base_dir.resolve()}\n"
        f"Total Files Tracked: {len(file_inventory)}\n\n"
        + "\n".join(tree_lines)
        + "\n\n⚠️ INSTRUCTION: You have the file structure above. DO NOT guess, hallucinate, or read every file blindly. "
        "Use the `search_codebase_keywords` tool to find specific functions or terms, and use the `read_file` tool "
        "selectively only on the most relevant files (like entry points or core modules) to get precise code samples."
    )
    return overview
