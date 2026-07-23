import subprocess
from typing import List, Optional
# AI agent generated btw


def run_terminal_command(command: str, timeout: int = 10) -> str:
    """
    Executes a terminal/command-line command and returns the output.

    Args:
        command: The shell command to execute (e.g., 'ls -la', 'git status')
        timeout: Maximum time in seconds to wait for command completion (default: 10)

    Returns:
        The command output (stdout + stderr) or an error message.
    """
    try:
        # Split command into list for safer execution
        cmd = command.split()

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr

        # Truncate very long outputs
        if len(output) > 4000:
            output = output[:4000] + "\n\n[Output truncated due to length...]"

        if result.returncode != 0:
            return f"Command exited with code {result.returncode}:\n{output}"

        return (
            output
            if output.strip()
            else "Command executed successfully with no output."
        )

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except FileNotFoundError:
        return f"Error: Command not found: '{command}'"
    except Exception as e:
        return f"Error executing command '{command}': {str(e)}"

