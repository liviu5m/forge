from pathlib import Path
from typing import Optional


def write_file(path: str, content: str) -> str:
    """
    Writes text content to a file. Creates parent directories if they don't exist.

    Args:
        path: The relative or absolute path to the file.
        content: The text content to write into the file.

    Returns:
        A success or error message.
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to file '{path}'."
    except Exception as e:
        return f"Error writing to file '{path}': {str(e)}"


def edit_file(path: str, target_content: str, new_content: str) -> str:
    """
    Replaces a specific section of text in an existing file with new content.

    Args:
        path: The path to the file to edit.
        target_content: The exact text/code snippet to find and replace.
        new_content: The new text/code snippet to replace it with.

    Returns:
        A success or error message.
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Error: File '{path}' does not exist."

        content = file_path.read_text(encoding="utf-8")

        if target_content not in content:
            return f"Error: Target content not found in '{path}'. Make sure the snippet matches exactly."

        # Perform the targeted replacement
        updated_content = content.replace(target_content, new_content, 1)
        file_path.write_text(updated_content, encoding="utf-8")

        return f"Successfully edited file '{path}'."
    except Exception as e:
        return f"Error editing file '{path}': {str(e)}"
