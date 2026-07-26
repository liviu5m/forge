import subprocess
from typing import List, Optional


def run_terminal_commands(command: str, working_dir: str = ".") -> str:
    """
    Executes a shell command in the terminal and returns its output.

    Args:
        command: The shell command to run (e.g., 'pytest', 'pip install -r requirements.txt').
        working_dir: The directory to execute the command in (defaults to current directory).
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        if result.returncode != 0:
            output += f"\nCommand exited with non-zero status code: {result.returncode}"

        return output.strip() or "Command executed successfully with no output."

    except subprocess.TimeoutExpired:
        return "Error: Terminal command timed out after 60 seconds."
    except Exception as e:
        return f"Error executing terminal command: {str(e)}"
