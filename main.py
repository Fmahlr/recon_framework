import os
import sys
import yaml
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from core.orchestrator import run_subdomain_enumeration_phase, run_host_discovery_phase, run_crawling_phase, run_vuln_scanning_phase

console = Console()

def display_banner():
    """Displays the tool's banner."""
    banner_text = """
    ██████╗ ███████╗ ██████╗ █████╗ ██╗   ██╗
    ██╔══██╗██╔════╝██╔════╝██╔══██╗██║   ██║
    ██████╔╝█████╗  ██║     ███████║██║   ██║
    ██╔══██╗██╔══╝  ██║     ██╔══██║██║   ██║
    ██║  ██║███████╗╚██████╗██║  ██║╚██████╔╝
    ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝
                Recon Framework v0.5
    """
    console.print(Panel.fit(banner_text, style="bold blue"))

def load_config(config_path='config.yaml'):
    """
    Loads configuration from the config.yaml file.
    Handles the case where the config file is empty.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            config = {}
            
        console.print("[bold green][+] Configuration file loaded successfully.[/bold green]")
        return config
    except FileNotFoundError:
        console.print(f"[bold red][!] Error: Configuration file '{config_path}' not found.[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red][!] Error loading configuration file: {e}[/bold red]")
        sys.exit(1)

def create_output_directory(domain):
    """Creates the output directory."""
    dir_name = f"recon_{domain.replace('.', '_')}_{datetime.now().strftime('%Y%m%d%H%M')}"
    try:
        os.makedirs(dir_name, exist_ok=True)
        sub_dirs = ["subs", "hosts", "urls", "vulns", "misc"]
        for sub_dir in sub_dirs:
            os.makedirs(os.path.join(dir_name, sub_dir), exist_ok=True)
        console.print(f"[bold green][+] Output directory created: {dir_name}[/bold green]")
        return dir_name
    except Exception as e:
        console.print(f"[bold red][!] Could not create output directory: {e}[/bold red]")
        sys.exit(1)

def main_menu(domain, config):
    """Displays the main interactive menu."""
    while True:
        console.print("\n")
        console.print(Panel.fit(f"Current Target: [bold cyan]{domain}[/bold cyan]", title="[yellow]Main Menu[/yellow]", border_style="yellow"))
        console.print("  [bold green]1.[/bold green] Quick Scan Methodology (Coming Soon)")
        console.print("  [bold green]2.[/bold green] Full & Deep Scan Methodology")
        console.print("  [bold blue]---------------------------------------------[/bold blue]")
        console.print("  [bold cyan]3.[/bold cyan] Phase 1: Subdomain Enumeration")
        console.print("  [bold cyan]4.[/bold cyan] Phase 2: Live Host Discovery")
        console.print("  [bold cyan]5.[/bold cyan] Phase 3: Crawling & URL Gathering")
        console.print("  [bold cyan]6.[/bold cyan] Phase 4: Vulnerability Scanning")
        console.print("  [bold blue]---------------------------------------------[/bold blue]")
        console.print("  [bold yellow]u.[/bold yellow] Update Tools (Coming Soon)")
        console.print("  [bold red]0.[/bold red] Exit")

        choice = Prompt.ask("\n[*] Select an option", choices=["1", "2", "3", "4", "5", "6", "u", "0"], default="2")

        if choice == '1':
            console.print("\n[yellow][*] Quick Scan selected (Execution coming soon)...[/yellow]")
        
        elif choice == '2':
            console.print("\n[yellow][*] Starting Full & Deep Scan Methodology...[/yellow]")
            subdomains = run_subdomain_enumeration_phase(domain, config)
            if subdomains:
                live_hosts = run_host_discovery_phase(domain, config)
                if live_hosts:
                    urls = run_crawling_phase(domain, config)
                    if urls:
                        run_vuln_scanning_phase(domain, config)
            console.print("\n[bold magenta]*** Full Scan Workflow Complete ***[/bold magenta]")

        elif choice == '3':
            run_subdomain_enumeration_phase(domain, config)
        elif choice == '4':
            run_host_discovery_phase(domain, config)
        elif choice == '5':
            run_crawling_phase(domain, config)
        elif choice == '6':
            run_vuln_scanning_phase(domain, config)
        elif choice == '0':
            console.print("\n[bold blue][*] Goodbye![/bold blue]")
            sys.exit(0)
        else:
            console.print(f"\n[yellow][*] Option '{choice}' will be implemented soon.[/yellow]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="An advanced framework for reconnaissance operations.")
    parser.add_argument("domain", help="The target domain (e.g., example.com)")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    display_banner()
    
    config_path = 'config.yaml'
    if not os.path.exists(config_path) and os.path.exists(f"../{config_path}"):
        config_path = f"../{config_path}"
        
    config = load_config(config_path)
    
    output_dir = create_output_directory(args.domain)
    os.chdir(output_dir) 

    main_menu(args.domain, config)
