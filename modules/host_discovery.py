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
    Saves output directly to a file.

    Args:
        input_file (str): The path to the file containing subdomains to scan.
        config (dict): The configuration dictionary.

    Returns:
        str: Path to the output file if successful, None otherwise.
    """
    console.print(f"[yellow][*] Running HTTPX on {input_file}...[/yellow]")
    output_file = "hosts/httpx_live_raw.txt" # Specific output file for HTTPX
    
    # -silent: show only results. -threads: for speed.
    threads = config.get('settings', {}).get('threads', 50)
    # Define common web ports to scan
    common_ports = "80,443,8080,8000,8888,8443,3000,5000,9000" # You can extend this list
    
    # Construct the command with explicit ports, directing output to the specified file
    command = f"httpx -l {input_file} -silent -threads {threads} -ports {common_ports} -o {output_file}"
    
    run_command(command) # Execute the command
    
    # Check if the output file was created and has content
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'r') as f:
            live_hosts_count = len(f.readlines())
        console.print(f"[bold green][+] HTTPX scan complete. Found {live_hosts_count} live hosts. Results saved to {output_file}[/bold green]")
        return output_file # Return the path to the file
    else:
        console.print("[yellow][!] HTTPX scan completed, but no live hosts were found or output file is empty.[/yellow]")
        return None

# This is a main block for testing this module individually
if __name__ == '__main__':
    test_domain_list = ["scanme.nmap.org", "example.com", "test.invalid-domain-for-testing.com"]
    test_file = "test_subs.txt"
    with open(test_file, "w") as f:
        for domain in test_domain_list:
            f.write(f"{domain}\n")

    console.print(f"[bold blue]--- Running Test for host_discovery.py ---[/bold blue]")
    
    test_config = {}
    if not os.path.exists("hosts"): # Ensure 'hosts' directory exists for testing
        os.makedirs("hosts")

    httpx_output_file = run_httpx(test_file, test_config)
    if httpx_output_file:
        print(f"\nHTTPX Results saved to: {httpx_output_file}")
    else:
        print("\nHTTPX found no live hosts.")
    
    # Clean up test file and output file
    os.remove(test_file)
    if httpx_output_file and os.path.exists(httpx_output_file):
        os.remove(httpx_output_file)
    if os.path.exists("hosts"):
        os.rmdir("hosts") # Remove directory if empty
