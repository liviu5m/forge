import subprocess


def run_tests(file_path: str, test_framework: str = "python3") -> str:
    """
    Execute tests for modified code and report results.
    Captures stdout and stderr from the test runner subprocess.
    """
    try:
        result = subprocess.run(
            [test_framework, file_path], capture_output=True, text=True, timeout=60
        )

        output = f"--- STDOUT ---\n{result.stdout}\n--- STDERR ---\n{result.stderr}"

        if result.returncode == 0:
            return f"Success: Tests passed cleanly.\n\n{output}"
        else:
            return (
                f"Failure: Tests failed with exit code {result.returncode}.\n\n{output}"
            )

    except FileNotFoundError:
        return f"Error: Testing framework '{test_framework}' is not installed or not found in the environment PATH."
    except subprocess.TimeoutExpired:
        return f"Error: Test execution timed out after 60 seconds."
    except Exception as e:
        return f"Error running tests: {str(e)}"
