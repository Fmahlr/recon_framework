# This module acts as the "brain" of the application.
import sys
import os
from rich.console import Console

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task_manager import run_tasks_in_parallel
from modules.subdomain_enum import run_subfinder, run_assetfinder, run_findomain
from modules.host_discovery import run_httpx
from modules.crawling import run_katana, run_gau
from modules.vuln_scanning import run_nuclei

console = Console()

def save_results(results, filename):
    """Saves a list of results to a specified file."""
    try:
        with open(filename, 'w') as f:
            for item in results:
                f.write(f"{item}\n")
        console.print(f"[bold green][+] Results saved to {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red][!] Error saving results to {filename}: {e}[/bold red]")

def combine_and_save_raw_results(raw_output_files, output_filename):
    """
    Reads lines from multiple raw output files, combines them, removes duplicates,
    and saves the unique sorted lines to a single output file.
    """
    all_lines = set() # Use a set to automatically handle duplicates
    for file_path in raw_output_files:
        if file_path and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        stripped_line = line.strip()
                        if stripped_line: # Ensure line is not empty
                            all_lines.add(stripped_line)
            except Exception as e:
                console.print(f"[yellow][!] Warning: Could not read lines from {file_path}: {e}[/yellow]")
        
        # Optionally, remove the raw file after processing to keep the directory clean
        # try:
        #     if file_path and os.path.exists(file_path):
        #         os.remove(file_path)
        # except Exception as e:
        #     console.print(f"[yellow][!] Warning: Could not remove raw file {file_path}: {e}[/yellow]")

    sorted_unique_lines = sorted(list(all_lines))
    if sorted_unique_lines:
        save_results(sorted_unique_lines, output_filename)
        console.print(f"[bold green][+] Combined and saved {len(sorted_unique_lines)} unique results to {output_filename}[/bold green]")
        return sorted_unique_lines
    else:
        console.print(f"[yellow][!] No unique results found to save to {output_filename}.[/yellow]")
        return []


def run_subdomain_enumeration_phase(domain, config):
    """Orchestrates the subdomain enumeration phase (Phase 1)."""
    console.print("\n\n" + "="*50)
    console.print("[bold blue]      STARTING PHASE 1: SUBDOMAIN ENUMERATION[/bold blue]")
    console.print("="*50 + "\n")

    process_timeout = config.get('settings', {}).get('process_timeout', 600)
    subdomain_tasks = [run_subfinder, run_assetfinder, run_findomain]
    
    # run_tasks_in_parallel will now return a list of file paths (or None)
    raw_subdomain_files = run_tasks_in_parallel(
        subdomain_tasks, domain, config, 
        description="Running subdomain enumeration...",
        process_timeout=process_timeout
    )

    # Combine and save results from the individual raw output files
    all_subdomains = combine_and_save_raw_results(raw_subdomain_files, "subs/all_subdomains.txt")

    console.print("\n" + "="*50)
    console.print("[bold blue]      PHASE 1: SUBDOMAIN ENUMERATION COMPLETE[/bold blue]")
    console.print("="*50 + "\n")
    return all_subdomains

def run_host_discovery_phase(domain, config):
    """Orchestrates the host discovery phase (Phase 2)."""
    console.print("\n\n" + "="*50)
    console.print("[bold blue]      STARTING PHASE 2: LIVE HOST DISCOVERY[/bold blue]")
    console.print("="*50 + "\n")

    subdomains_file = "subs/all_subdomains.txt"
    if not os.path.exists(subdomains_file) or os.path.getsize(subdomains_file) == 0:
        console.print("[yellow][!] Subdomain list not found. Running Phase 1 first...[/yellow]")
        # If phase 1 doesn't find subdomains, abort phase 2
        if not run_subdomain_enumeration_phase(domain, config):
            console.print("[bold red][!] Phase 1 did not find any subdomains. Aborting Phase 2.[/bold red]")
            return []
    
    # HTTPX is run individually, not in parallel with other tools in this phase
    # It now returns the path to its output file
    httpx_output_file = run_httpx(subdomains_file, config)
    
    # Combine and save results (even if only one file for now)
    live_hosts = combine_and_save_raw_results([httpx_output_file], "hosts/live_hosts.txt")

    console.print("\n" + "="*50)
    console.print("[bold blue]      PHASE 2: LIVE HOST DISCOVERY COMPLETE[/bold blue]")
    console.print("="*50 + "\n")
    return live_hosts

def run_crawling_phase(domain, config):
    """Orchestrates the URL crawling phase (Phase 3)."""
    console.print("\n\n" + "="*50)
    console.print("[bold blue]      STARTING PHASE 3: CRAWLING & URL GATHERING[/bold blue]")
    console.print("="*50 + "\n")

    live_hosts_file = "hosts/live_hosts.txt"
    if not os.path.exists(live_hosts_file) or os.path.getsize(live_hosts_file) == 0:
        console.print("[yellow][!] Live host list not found. Running Phase 2 first...[/yellow]")
        # If phase 2 doesn't find live hosts, abort phase 3
        if not run_host_discovery_phase(domain, config):
            console.print("[bold red][!] Phase 2 did not find any live hosts. Aborting Phase 3.[/bold red]")
            return []

    process_timeout = config.get('settings', {}).get('process_timeout', 600)
    crawling_tasks = [run_katana, run_gau]
    
    # run_tasks_in_parallel will now return a list of file paths (or None)
    raw_url_files = run_tasks_in_parallel(
        crawling_tasks, live_hosts_file, config,
        description="Crawling for URLs...",
        process_timeout=process_timeout
    )

    # Combine and save results from the individual raw output files
    all_urls = combine_and_save_raw_results(raw_url_files, "urls/all_urls.txt")
    
    console.print("\n" + "="*50)
    console.print("[bold blue]      PHASE 3: CRAWLING & URL GATHERING COMPLETE[/bold blue]")
    console.print("="*50 + "\n")
    return all_urls

def run_vuln_scanning_phase(domain, config):
    """Orchestrates the vulnerability scanning phase (Phase 4)."""
    console.print("\n\n" + "="*50)
    console.print("[bold blue]      STARTING PHASE 4: VULNERABILITY SCANNING[/bold blue]")
    console.print("="*50 + "\n")

    urls_file = "urls/all_urls.txt"
    if not os.path.exists(urls_file) or os.path.getsize(urls_file) == 0:
        console.print("[yellow][!] URL list not found. Running Phase 3 first...[/yellow]")
        # If phase 3 doesn't find URLs, abort phase 4
        if not run_crawling_phase(domain, config):
            console.print("[bold red][!] Phase 3 did not find any URLs. Aborting Phase 4.[/bold red]")
            return

    # Nuclei is run individually, not in parallel with other tools in this phase (for now)
    # It now returns the path to its output file
    nuclei_output_file = run_nuclei(urls_file, config)
    
    # Combine and save results (even if only one file for now)
    # This step is here for consistency and future expansion if more vuln scanners are added
    all_vulns = combine_and_save_raw_results([nuclei_output_file], "vulns/all_vulns.txt")

    console.print("\n" + "="*50)
    console.print("[bold blue]      PHASE 4: VULNERABILITY SCANNING COMPLETE[/bold blue]")
    console.print("="*50 + "\n")
    return all_vulns
