# This module is responsible for running various subdomain enumeration tools.

# We need to adjust the Python path to be able to import from the parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tool_wrapper import run_command
from rich.console import Console

console = Console()

def run_subfinder(domain, config):
    """
    Runs the subfinder tool to find subdomains.
    Saves output directly to a file.

    Args:
        domain (str): The target domain.
        config (dict): The configuration dictionary (not used in this function yet).

    Returns:
        str: Path to the output file if successful, None otherwise.
    """
    console.print(f"[yellow][*] Running Subfinder for {domain}...[/yellow]")
    output_file = "subs/subfinder_raw.txt" # Specific output file for Subfinder
    command = f"subfinder -d {domain} -silent -o {output_file}" # Use -o for direct output
    
    run_command(command) # Execute the command
    
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'r') as f:
            subdomains_count = len(f.readlines())
        console.print(f"[bold green][+] Subfinder scan complete. Found {subdomains_count} subdomains. Results saved to {output_file}[/bold green]")
        return output_file
    else:
        console.print("[yellow][!] Subfinder scan completed, but no subdomains were found or output file is empty.[/yellow]")
        return None

def run_assetfinder(domain, config):
    """
    Runs the assetfinder tool to find subdomains.
    Saves output directly to a file.

    Args:
        domain (str): The target domain.
        config (dict): The configuration dictionary.

    Returns:
        str: Path to the output file if successful, None otherwise.
    """
    console.print(f"[yellow][*] Running Assetfinder for {domain}...[/yellow]")
    output_file = "subs/assetfinder_raw.txt" # Specific output file for Assetfinder
    command = f"assetfinder --subs-only {domain} > {output_file}" # Redirect output to file
    
    run_command(command)
    
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'r') as f:
            subdomains_count = len(f.readlines())
        console.print(f"[bold green][+] Assetfinder scan complete. Found {subdomains_count} subdomains. Results saved to {output_file}[/bold green]")
        return output_file
    else:
        console.print("[yellow][!] Assetfinder scan completed, but no subdomains were found or output file is empty.[/yellow]")
        return None

def run_findomain(domain, config):
    """
    Runs the findomain tool to find subdomains.
    Saves output directly to a file.

    Args:
        domain (str): The target domain.
        config (dict): The configuration dictionary.

    Returns:
        str: Path to the output file if successful, None otherwise.
    """
    console.print(f"[yellow][*] Running Findomain for {domain}...[/yellow]")
    output_file = "subs/findomain_raw.txt" # Specific output file for Findomain
    # The -q flag makes findomain quiet, and -o for output file
    command = f"findomain -t {domain} -q -o {output_file}" 
    
    run_command(command)
    
    # Findomain might save to a file named after the domain, so we need to check that.
    # A more robust approach might be to ensure findomain saves to the exact output_file.
    # For now, assuming -o flag works as expected to the specified path.
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'r') as f:
            subdomains_count = len(f.readlines())
        console.print(f"[bold green][+] Findomain scan complete. Found {subdomains_count} subdomains. Results saved to {output_file}[/bold green]")
        return output_file
    else:
        console.print("[yellow][!] Findomain scan completed, but no subdomains were found or output file is empty.[/yellow]")
        return None


# This is a main block for testing this module individually
if __name__ == '__main__':
    test_domain = "example.com"
    console.print(f"[bold blue]--- Running Test for subdomain_enum.py ---[/bold blue]")
    console.print(f"Target: {test_domain}")

    test_config = {}
    if not os.path.exists("subs"): # Ensure 'subs' directory exists for testing
        os.makedirs("subs")

    subfinder_output_file = run_subfinder(test_domain, test_config)
    if subfinder_output_file:
        print(f"\nSubfinder Results saved to: {subfinder_output_file}")
    else:
        print("\nSubfinder found no subdomains.")

    assetfinder_output_file = run_assetfinder(test_domain, test_config)
    if assetfinder_output_file:
        print(f"\nAssetfinder Results saved to: {assetfinder_output_file}")
    else:
        print("\nAssetfinder found no subdomains.")
    
    findomain_output_file = run_findomain(test_domain, test_config)
    if findomain_output_file:
        print(f"\nFindomain Results saved to: {findomain_output_file}")
    else:
        print("\nFindomain found no subdomains.")
    
    # Clean up test files and output files
    test_output_files = [subfinder_output_file, assetfinder_output_file, findomain_output_file]
    for f_path in test_output_files:
        if f_path and os.path.exists(f_path):
            os.remove(f_path)
    if os.path.exists("subs"):
        os.rmdir("subs") # Remove directory if empty
