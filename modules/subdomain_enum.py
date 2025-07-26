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

    Args:
        domain (str): The target domain.
        config (dict): The configuration dictionary (not used in this function yet).

    Returns:
        list: A list of subdomains found by subfinder.
    """
    console.print(f"[yellow][*] Running Subfinder for {domain}...[/yellow]")
    command = f"subfinder -d {domain} -silent"
    output = run_command(command)
    
    if output:
        subdomains = output.splitlines()
        console.print(f"[bold green][+] Subfinder found {len(subdomains)} subdomains.[/bold green]")
        return subdomains
    return []

def run_assetfinder(domain, config):
    """
    Runs the assetfinder tool to find subdomains.

    Args:
        domain (str): The target domain.
        config (dict): The configuration dictionary.

    Returns:
        list: A list of subdomains found by assetfinder.
    """
    console.print(f"[yellow][*] Running Assetfinder for {domain}...[/yellow]")
    command = f"assetfinder --subs-only {domain}"
    output = run_command(command)
    
    if output:
        subdomains = output.splitlines()
        console.print(f"[bold green][+] Assetfinder found {len(subdomains)} subdomains.[/bold green]")
        return subdomains
    return []

def run_findomain(domain, config):
    """
    Runs the findomain tool to find subdomains.

    Args:
        domain (str): The target domain.
        config (dict): The configuration dictionary.

    Returns:
        list: A list of subdomains found by findomain.
    """
    console.print(f"[yellow][*] Running Findomain for {domain}...[/yellow]")
    # The -q flag makes findomain quiet
    command = f"findomain -t {domain} -q"
    output = run_command(command)
    
    if output:
        subdomains = output.splitlines()
        console.print(f"[bold green][+] Findomain found {len(subdomains)} subdomains.[/bold green]")
        return subdomains
    return []


# This is a main block for testing this module individually
if __name__ == '__main__':
    # This part of the script will only run when you execute this file directly
    # e.g., python modules/subdomain_enum.py
    
    test_domain = "example.com"
    console.print(f"[bold blue]--- Running Test for subdomain_enum.py ---[/bold blue]")
    console.print(f"Target: {test_domain}")

    # For testing, we pass an empty config dictionary
    test_config = {}

    subfinder_results = run_subfinder(test_domain, test_config)
    print("\nSubfinder Results:")
    print(subfinder_results)

    assetfinder_results = run_assetfinder(test_domain, test_config)
    print("\nAssetfinder Results:")
    print(assetfinder_results)
    
    findomain_results = run_findomain(test_domain, test_config)
    print("\nFindomain Results:")
    print(findomain_results)
