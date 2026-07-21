from pathlib import Path
from typing import Optional


def read_file(
    path: str, start_line: Optional[int] = None, end_line: Optional[int] = None
) -> str:
    """
    Read the contents of a file, optionally restricted to a specific line range.

    Args:
        path: The relative or absolute path to the file.
        start_line: Optional 1-based starting line number.
        end_line: Optional 1-based ending line number.

    Returns:
        The file contents as a string, or an error message if it fails.
    """
    try:
        print("Reading file..." + path)
        file_path = Path(path)

        if not file_path.exists():
            return f"Error: File '{path}' does not exist."
        if not file_path.is_file():
            return f"Error: Path '{path}' is a directory, not a file."

        lines = file_path.read_text(encoding="utf-8").splitlines()

        if start_line is not None and end_line is not None:
            start_idx = max(0, start_line - 1)
            end_idx = max(0, end_line)
            lines = lines[start_idx:end_idx]

        return "\n".join(lines)

    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"
