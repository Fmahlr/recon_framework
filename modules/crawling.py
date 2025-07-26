# This module is responsible for crawling URLs from live hosts.
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tool_wrapper import run_command
from rich.console import Console

console = Console()

def run_katana(input_file, config):
    """
    Runs Katana to crawl URLs from a list of live hosts, using flags from the methodology.

    Args:
        input_file (str): Path to the file containing live hosts.
        config (dict): The configuration dictionary.

    Returns:
        list: A list of URLs found.
    """
    console.print(f"[yellow][*] Running Katana on {input_file}...[/yellow]")
    # Using flags from the reference bash script: -jc (javascript parsing), -d 2 (crawl depth)
    command = f"katana -list {input_file} -silent -jc -d 2"
    output = run_command(command)
    
    if output:
        urls = output.splitlines()
        console.print(f"[bold green][+] Katana found {len(urls)} URLs.[/bold green]")
        return urls
    return []

def run_gau(input_file, config):
    """
    Runs GAU (Get All URLs) to fetch historical URLs from multiple providers.
    This version reads the file and passes its content to stdin.

    Args:
        input_file (str): Path to the file containing live hosts.
        config (dict): The configuration dictionary.

    Returns:
        list: A list of URLs found.
    """
    console.print(f"[yellow][*] Running GAU on {input_file}...[/yellow]")
    # The '-t' flag for threads has been removed as it's deprecated in newer versions of gau.
    command = "gau"
    
    try:
        with open(input_file, 'r') as f:
            input_content = f.read()
    except FileNotFoundError:
        console.print(f"[bold red][!] Input file for GAU not found: {input_file}[/bold red]")
        return []

    # Pass the file content to the command's standard input
    output = run_command(command, stdin_data=input_content)
    
    if output:
        urls = output.splitlines()
        console.print(f"[bold green][+] GAU found {len(urls)} URLs.[/bold green]")
        return urls
    return []

# This is a main block for testing this module individually
if __name__ == '__main__':
    test_hosts = ["https://scanme.nmap.org", "http://example.com"]
    test_file = "test_hosts.txt"
    with open(test_file, "w") as f:
        for host in test_hosts:
            f.write(f"{host}\n")

    console.print(f"[bold blue]--- Running Test for crawling.py ---[/bold blue]")
    test_config = {}

    katana_urls = run_katana(test_file, test_config)
    print("\nKatana Results:")
    print(katana_urls[:10]) # Print first 10 for brevity

    gau_urls = run_gau(test_file, test_config)
    print("\nGAU Results:")
    print(gau_urls[:10])
    
    os.remove(test_file)
