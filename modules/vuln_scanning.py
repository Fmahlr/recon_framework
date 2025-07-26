# This module is responsible for running various vulnerability scanning tools.
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tool_wrapper import run_command
from rich.console import Console

console = Console()

def run_nuclei(input_file, config):
    """
    Runs Nuclei to scan for vulnerabilities.

    Args:
        input_file (str): Path to the file containing URLs to scan.
        config (dict): The configuration dictionary.

    Returns:
        str: The raw output from Nuclei, which can be parsed later.
    """
    console.print(f"[yellow][*] Running Nuclei on {input_file}...[/yellow]")
    output_file = "vulns/nuclei_results.txt"
    
    # -c: concurrency, -bs: batch size for performance
    # -o: output file
    command = f"nuclei -l {input_file} -c 50 -bs 25 -o {output_file}"
    
    # We run the command and capture the output to display it, 
    # but the primary results are saved to the file by Nuclei itself.
    output = run_command(command)
    
    try:
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, 'r') as f:
                results_count = len(f.readlines())
            console.print(f"[bold green][+] Nuclei scan complete. Found {results_count} potential vulnerabilities.[/bold green]")
            console.print(f"[green][*] Results saved to {output_file}[/green]")
        else:
            console.print("[yellow][!] Nuclei scan completed, but no vulnerabilities were found.[/yellow]")
    except Exception as e:
        console.print(f"[bold red][!] Error reading Nuclei output file: {e}[/bold red]")

    return output # Returning raw output for potential live display in the future

# This is a main block for testing this module individually
if __name__ == '__main__':
    test_urls = ["http://scanme.nmap.org", "http://testphp.vulnweb.com"]
    test_file = "test_urls.txt"
    with open(test_file, "w") as f:
        for url in test_urls:
            f.write(f"{url}\n")

    console.print(f"[bold blue]--- Running Test for vuln_scanning.py ---[/bold blue]")
    test_config = {}
    if not os.path.exists("vulns"):
        os.makedirs("vulns")

    run_nuclei(test_file, test_config)
    
    os.remove(test_file)
