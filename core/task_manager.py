import multiprocessing
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# --- Smart Environment Setup ---
import os
os.environ['PATH'] = f"{os.path.join(os.path.expanduser('~'), 'go', 'bin')}:{os.path.join(os.path.expanduser('~'), '.local', 'bin')}:{os.environ['PATH']}"
# --- End of Smart Environment Setup ---

console = Console()

def run_task(task, target, config, results_queue):
    """
    A wrapper function to execute a single task and put its result into a queue.
    """
    try:
        result = task(target, config)
        if result:
            results_queue.put(result)
    except Exception as e:
        console.print(f"[bold red][!] Error in task '{task.__name__}': {e}[/bold red]")


def run_tasks_in_parallel(tasks, target, config, description="Running tasks in parallel...", process_timeout=None):
    """
    Executes a list of tasks in parallel using multiprocessing with a timeout.
    """
    results_queue = multiprocessing.Queue()
    processes = []
    all_results = []

    for task in tasks:
        process = multiprocessing.Process(target=run_task, args=(task, target, config, results_queue))
        processes.append(process)
        process.start()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"[cyan]{description}[/cyan]", total=None)
        
        # Wait for all processes to complete, with a timeout for each one
        for process in processes:
            try:
                process.join(timeout=process_timeout)
                if process.is_alive():
                    console.print(f"[yellow][!] Task process {process.pid} timed out after {process_timeout} seconds. Terminating.[/yellow]")
                    process.terminate() # Forcefully stop the process
                    process.join() # Clean up the terminated process
            except KeyboardInterrupt:
                console.print(f"[bold red]User interrupted. Terminating process {process.pid}...[/bold red]")
                process.terminate()
                process.join()


    while not results_queue.empty():
        all_results.extend(results_queue.get())

    unique_results = sorted(list(set(all_results)))
    
    console.print(f"[bold green][+] All parallel tasks completed. Found {len(unique_results)} unique results.[/bold green]")
    
    return unique_results
