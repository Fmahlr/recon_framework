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

def run_subdomain_enumeration_phase(domain, config):
    """Orchestrates the subdomain enumeration phase (Phase 1)."""
    console.print("\n\n" + "="*50)
    console.print("[bold blue]      STARTING PHASE 1: SUBDOMAIN ENUMERATION[/bold blue]")
    console.print("="*50 + "\n")

    process_timeout = config.get('settings', {}).get('process_timeout', 600)
    subdomain_tasks = [run_subfinder, run_assetfinder, run_findomain]
    all_subdomains = run_tasks_in_parallel(
        subdomain_tasks, domain, config, 
        description="Running subdomain enumeration...",
        process_timeout=process_timeout
    )

    if all_subdomains:
        save_results(all_subdomains, "subs/all_subdomains.txt")
    else:
        console.print("[yellow][!] No subdomains were found in this phase.[/yellow]")

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
        if not run_subdomain_enumeration_phase(domain, config):
            console.print("[bold red][!] Phase 1 did not find any subdomains. Aborting Phase 2.[/bold red]")
            return []
    
    live_hosts = run_httpx(subdomains_file, config)
    
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
        if not run_host_discovery_phase(domain, config):
            console.print("[bold red][!] Phase 2 did not find any live hosts. Aborting Phase 3.[/bold red]")
            return []

    process_timeout = config.get('settings', {}).get('process_timeout', 600)
    crawling_tasks = [run_katana, run_gau]
    all_urls = run_tasks_in_parallel(
        crawling_tasks, live_hosts_file, config,
        description="Crawling for URLs...",
        process_timeout=process_timeout
    )

    if all_urls:
        save_results(all_urls, "urls/all_urls.txt")
    else:
        console.print("[yellow][!] No URLs were found in this phase.[/yellow]")
    
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
        if not run_crawling_phase(domain, config):
            console.print("[bold red][!] Phase 3 did not find any URLs. Aborting Phase 4.[/bold red]")
            return

    # Vulnerability scanning is not run in parallel by default as Nuclei handles its own concurrency.
    run_nuclei(urls_file, config)

    console.print("\n" + "="*50)
    console.print("[bold blue]      PHASE 4: VULNERABILITY SCANNING COMPLETE[/bold blue]")
    console.print("="*50 + "\n")

