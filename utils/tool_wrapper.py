import subprocess
import shlex
import os
import shutil
from rich.console import Console

# --- Smart Environment Setup ---
# Add custom tool directories to the PATH environment variable for this script's session.
# This makes the script's environment aware of where to find the installed tools.
go_bin_dir = os.path.join(os.path.expanduser('~'), 'go', 'bin')
local_bin_dir = os.path.join(os.path.expanduser('~'), '.local', 'bin')
os.environ['PATH'] = f"{go_bin_dir}:{local_bin_dir}:{os.environ['PATH']}"
# --- End of Smart Environment Setup ---


# Initialize a console for rich text output
console = Console()

def run_command(command, timeout=None, stdin_data=None):
    """
    Executes an external command safely and returns its output.

    This function is a wrapper around Python's subprocess module to provide
    a standardized way of running external command-line tools.

    Args:
        command (str): The full command to execute (e.g., "subfinder -d example.com").
        timeout (int, optional): The maximum time in seconds for the command to complete. Defaults to None.
        stdin_data (str, optional): Data to be passed to the command's standard input. Defaults to None.

    Returns:
        str: The standard output (stdout) of the command as a string if successful.
        None: If the command fails, times out, or is not found.
    """
    try:
        # Use shlex.split to correctly handle commands with arguments and quotes
        args = shlex.split(command)
        tool_name = args[0]

        # Now that we've modified the PATH, shutil.which should find the tool.
        # This is a final check to ensure the tool exists before running it.
        if not shutil.which(tool_name):
            console.print(f"[bold red][!] Error: Command '{tool_name}' not found. Is it installed correctly?[/bold red]")
            return None

        process = subprocess.run(
            args,
            capture_output=True,
            text=True,       # Decode stdout/stderr as text
            check=False,     # Do not raise an exception for non-zero exit codes
            timeout=timeout,
            input=stdin_data # Pass data to stdin
        )

        if process.returncode != 0:
            # We already checked if the command exists, so this handles other runtime errors.
            error_snippet = process.stderr.strip().split('\n')[0]
            console.print(f"[yellow][!] Warning: Command '{command}' finished with exit code {process.returncode}. Error: {error_snippet}[/yellow]")
            return None

        return process.stdout.strip()

    except FileNotFoundError:
        # This is a fallback, but shutil.which should prevent this.
        console.print(f"[bold red][!] Error: Command '{shlex.split(command)[0]}' not found. Is it installed and in your PATH?[/bold red]")
        return None
    except subprocess.TimeoutExpired:
        console.print(f"[bold red][!] Error: Command '{command}' timed out after {timeout} seconds.[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red][!] An unexpected error occurred while running '{command}': {e}[/bold red]")
        return None
