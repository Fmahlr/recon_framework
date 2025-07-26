# This module is responsible for discovering live hosts from a list of subdomains.
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tool_wrapper import run_command
from rich.console import Console

console = Console()

def run_httpx(input_file, config):
    """
    Runs the httpx tool to find live web servers.

    Args:
        input_file (str): The path to the file containing subdomains to scan.
        config (dict): The configuration dictionary.

    Returns:
        list: A list of live hosts found by httpx.
    """
    console.print(f"[yellow][*] Running HTTPX on {input_file}...[/yellow]")
    output_file = "hosts/live_hosts.txt"
    # -silent: show only results. -threads: for speed.
    threads = config.get('settings', {}).get('threads', 50)
    command = f"httpx -l {input_file} -silent -threads {threads} -o {output_file}"
    
    # We run the command but don't need its stdout, as httpx saves directly to a file.
    run_command(command)
    
    # Read the results from the output file
    try:
        with open(output_file, 'r') as f:
            live_hosts = [line.strip() for line in f.readlines()]
        
        if live_hosts:
            console.print(f"[bold green][+] HTTPX found {len(live_hosts)} live hosts.[/bold green]")
            return live_hosts
        else:
            console.print("[yellow][!] HTTPX did not find any live hosts.[/yellow]")
            return []
    except FileNotFoundError:
        console.print("[yellow][!] HTTPX did not produce an output file.[/yellow]")
        return []

# This is a main block for testing this module individually
if __name__ == '__main__':
    # This part of the script will only run when you execute this file directly
    test_domain_list = ["scanme.nmap.org", "example.com", "test.invalid-domain-for-testing.com"]
    test_file = "test_subs.txt"
    with open(test_file, "w") as f:
        for domain in test_domain_list:
            f.write(f"{domain}\n")

    console.print(f"[bold blue]--- Running Test for host_discovery.py ---[/bold blue]")
    
    # For testing, we pass an empty config dictionary and create a dummy hosts dir
    test_config = {}
    if not os.path.exists("hosts"):
        os.makedirs("hosts")

    live_hosts_results = run_httpx(test_file, test_config)
    print("\nLive Host Results:")
    print(live_hosts_results)
    
    # Clean up test file
    os.remove(test_file)
