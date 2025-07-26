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
    Saves output directly to a file.

    Args:
        input_file (str): Path to the file containing URLs to scan.
        config (dict): The configuration dictionary.

    Returns:
        str: Path to the output file if successful, None otherwise.
    """
    console.print(f"[yellow][*] Running Nuclei on {input_file}...[/yellow]")
    output_file = "vulns/nuclei_results.txt" # Specific output file for Nuclei
    
    # -c: concurrency, -bs: batch size for performance
    # -o: output file
    command = f"nuclei -l {input_file} -c 50 -bs 25 -o {output_file}"
    
    run_command(command) # Execute the command
    
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'r') as f:
            results_count = len(f.readlines())
        console.print(f"[bold green][+] Nuclei scan complete. Found {results_count} potential vulnerabilities. Results saved to {output_file}[/bold green]")
        return output_file # Return the path to the file
    else:
        console.print("[yellow][!] Nuclei scan completed, but no vulnerabilities were found or output file is empty.[/yellow]")
        return None

# This is a main block for testing this module individually
if __name__ == '__main__':
    test_urls = ["http://scanme.nmap.org", "http://testphp.vulnweb.com"]
    test_file = "test_urls.txt"
    with open(test_file, "w") as f:
        for url in test_urls:
            f.write(f"{url}\n")

    console.print(f"[bold blue]--- Running Test for vuln_scanning.py ---[/bold blue]")
    test_config = {}
    if not os.path.exists("vulns"): # Ensure 'vulns' directory exists for testing
        os.makedirs("vulns")

    nuclei_output_file = run_nuclei(test_file, test_config)
    if nuclei_output_file:
        print(f"\nNuclei Results saved to: {nuclei_output_file}")
    else:
        print("\nNuclei found no vulnerabilities.")
    
    os.remove(test_file)
    if nuclei_output_file and os.path.exists(nuclei_output_file):
        os.remove(nuclei_output_file)
    if os.path.exists("vulns"):
        os.rmdir("vulns") # Remove directory if empty
