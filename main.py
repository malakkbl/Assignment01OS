from process import Process
from algorithms.fcfs import fcfs_schedule
from algorithms.priority_non_preemptive import priority_schedule
from algorithms.priority_preemptive import priority_preemptive_schedule
from algorithms.sjf import sjf               
from algorithms.round_robin import round_robin
from algorithms.priority_rr import priority_round_robin
from algorithm_comparison import run_algorithm_comparison
import time
import os
import sys

# Terminal colors and styles
class Color:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

# Utility functions for terminal UI
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print a formatted header."""
    width = 60
    print(f"\n{Color.BG_BLUE}{Color.WHITE}{Color.BOLD} {text.center(width-2)} {Color.RESET}")

def print_subheader(text):
    """Print a formatted subheader."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'═' * 5} {text} {'═' * (45 - len(text))}{Color.RESET}")

def print_footer():
    """Print a footer."""
    print(f"\n{Color.BG_BLUE}{Color.WHITE}{Color.BOLD} {'CPU Scheduler Simulator'.center(58)} {Color.RESET}")

def print_success(text):
    """Print a success message."""
    print(f"{Color.GREEN}✓ {text}{Color.RESET}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Color.YELLOW}⚠️  {text}{Color.RESET}")

def print_error(text):
    """Print an error message."""
    print(f"{Color.RED}✗ {text}{Color.RESET}")

def print_loading(text="Processing"):
    """Show a simple loading animation."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for i in range(10):
        sys.stdout.write(f"\r{Color.CYAN}{chars[i % len(chars)]} {text}...{Color.RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(text) + 15) + "\r")
    sys.stdout.flush()

def input_styled(prompt):
    """Get user input with styled prompt."""
    return input(f"{Color.BOLD}{Color.BLUE}➜ {Color.RESET}{prompt}: {Color.GREEN}")

# ---------------- MENU -----------------
def choose_mode():
    """Choose between single algorithm or comparison mode."""
    print_subheader("OPERATION MODE")
    print(f"  {Color.CYAN}1{Color.RESET}) {Color.BOLD}Single Algorithm{Color.RESET} - Run one scheduling algorithm")
    print(f"  {Color.CYAN}2{Color.RESET}) {Color.BOLD}Algorithm Comparison{Color.RESET} - Compare multiple algorithms")
    
    while True:
        choice = input_styled("Choose mode").strip()
        print(Color.RESET, end="")
        
        if choice in ["1", "2"]:
            return "single" if choice == "1" else "comparison"
        
        print_error("Invalid option – try again.")
        time.sleep(1)

def choose_algorithm():
    """Return (algo_name, algo_function) chosen by the user."""
    algos = {
        "1": ("FCFS", fcfs_schedule),
        "2": ("Priority (non-preemptive)", priority_schedule),
        "3": ("Priority (preemptive)", priority_preemptive_schedule),
        "4": ("Shortest-Job-First (SJF)", sjf),         
        "5": ("Round-Robin", round_robin), 
        "6": ("Priority + Round-Robin", priority_round_robin),
    }

    while True:
        print_subheader("SCHEDULING ALGORITHMS")
        
        # Create a visually appealing menu
        for k, (name, _) in algos.items():
            print(f"  {Color.CYAN}{k}{Color.RESET}) {Color.BOLD}{name}{Color.RESET}")
        
        choice = input_styled("Your choice").strip()
        print(Color.RESET, end="")
        
        if choice in algos:
            return algos[choice]
        
        print_error("Invalid option – try again.")
        time.sleep(1)

# ------------- DATA ENTRY --------------
def read_processes(need_priority: bool = False):
    """
    Interactively build a list of Process objects.
    PIDs are auto-generated as 1, 2, 3, … (no user input).
    """
    print_subheader("PROCESS INFORMATION")
    
    try:
        n = int(input_styled("Number of processes").strip())
        if n <= 0:
            print_error("Number of processes must be positive")
            return read_processes(need_priority)
    except ValueError:
        print_error("Please enter a valid number")
        return read_processes(need_priority)
    
    processes = []
    print(f"\n{Color.YELLOW}Enter details for {n} processes:{Color.RESET}")

    for i in range(1, n + 1):
        print(f"\n{Color.MAGENTA}Process #{i}{Color.RESET}  {Color.BOLD}(PID: {i}){Color.RESET}")
        
        # Validate arrival time
        while True:
            try:
                arrival = int(input(f"  {Color.CYAN}Arrival time{Color.RESET} (≥ 0): "))
                if arrival >= 0:
                    break
                print_warning("Arrival time cannot be negative. Please enter 0 or a positive integer.")
            except ValueError:
                print_error("Please enter a valid number")
        
        # Validate burst time
        while True:
            try:
                burst = int(input(f"  {Color.CYAN}Burst time{Color.RESET} (> 0): "))
                if burst > 0:
                    break
                print_warning("Burst time must be positive.")
            except ValueError:
                print_error("Please enter a valid number")

        if need_priority:
            # --- Priority with validation ---
            while True:
                try:
                    prio = int(input(f"  {Color.CYAN}Priority{Color.RESET} (lower = higher priority): "))
                    if prio >= 0:
                        break
                    print_warning("Negative priorities are reserved for system tasks. Please enter 0 or higher.")
                except ValueError:
                    print_error("Please enter a valid number")
            
            processes.append(Process(i, arrival, burst, prio))
        else:
            processes.append(Process(i, arrival, burst))

    print_success(f"Successfully created {n} processes")
    return processes

# ------------- REPORTING ---------------
def print_schedule(tbl):
    """
    Pretty-print the schedule table.
    """
    print_subheader("SCHEDULE")
    
    # Table headers
    print(f"{Color.BOLD}{'PID':<6}{'Start':<10}{'Finish':<10}{Color.RESET}")
    print(f"{'─' * 26}")

    # Table content with alternating row colors
    for i, row in enumerate(tbl):
        bg_color = Color.BG_BLACK if i % 2 == 0 else ""
        print(f"{bg_color}{Color.BOLD}{Color.CYAN}{row['pid']:<6}{Color.RESET}{bg_color}"
              f"{row['start']:<10}{row['finish']:<10}{Color.RESET}")

    # Calculate metrics
    makespan = max(r['finish'] for r in tbl) if tbl else 0
    print(f"\n{Color.YELLOW}Makespan:{Color.RESET} {Color.BOLD}{makespan}{Color.RESET}")

def print_process_stats(processes):
    """Print statistics for each process with a nice format."""
    print_subheader("PROCESS STATISTICS")
    
    # Table headers
    headers = ["PID", "Waiting Time", "Turnaround", "Completion"]
    print(f"{Color.BOLD}{headers[0]:<6}{headers[1]:<16}{headers[2]:<14}{headers[3]:<14}{Color.RESET}")
    print(f"{'─' * 50}")
    
    # Table content
    for i, proc in enumerate(processes):
        bg_color = Color.BG_BLACK if i % 2 == 0 else ""
        print(f"{bg_color}{Color.CYAN}{proc.pid:<6}{Color.RESET}{bg_color}"
              f"{proc.waiting_time:<16}{proc.turnaround_time:<14}{proc.completion_time:<14}{Color.RESET}")

def print_metrics(metrics):
    """Print overall metrics with visual emphasis."""
    print_subheader("PERFORMANCE METRICS")
    
    # Use a more visual presentation for metrics
    for key, value in metrics.items():
        metric_name = key.replace('_', ' ').title()
        print(f"  {Color.YELLOW}{metric_name}:{Color.RESET} {Color.BOLD}{value:.2f}{Color.RESET}")

# --------------- DRIVER ----------------
def main():
    clear_screen()
    print_header("CPU SCHEDULER SIMULATOR")
    print(f"\n{Color.YELLOW}Welcome to the CPU Scheduler Simulator!{Color.RESET}")
    print("This tool demonstrates various CPU scheduling algorithms.")
    
    # Choose mode: single algorithm or comparison
    mode = choose_mode()
    
    if mode == "single":
        # Single algorithm mode (original functionality)
        algo_name, algo_fn = choose_algorithm()
        need_priority = "Priority" in algo_name
        processes = read_processes(need_priority)
        
        # Get quantum for Round-Robin algorithms
        quantum = None
        if "Round-Robin" in algo_name:
            while True:
                try:
                    quantum = int(input_styled("Time quantum (> 0)").strip())
                    if quantum > 0:
                        break
                    print_warning("Time quantum must be positive")
                except ValueError:
                    print_error("Please enter a valid number")
        
        # Show a loading animation
        print_loading(f"Scheduling with {algo_name}")
        
        # Execute the scheduling algorithm
        if quantum is not None:
            list_processes, schedule_table, metrics = algo_fn(processes, quantum)
        else:
            list_processes, schedule_table, metrics = algo_fn(processes)
        
        # Print results
        print_success(f"Scheduled {len(processes)} processes using {Color.BOLD}{algo_name}{Color.RESET}")
        print_schedule(schedule_table)
        print_process_stats(list_processes)
        print_metrics(metrics)
    
    else:
        # Comparison mode
        # First, determine if we need priority for any algorithm
        need_priority = True  # Always collect priority since we don't know which algorithms will be chosen
        processes = read_processes(need_priority)
        
        # Run the comparison
        run_algorithm_comparison(processes, Color)
    
    print_footer()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nProgram terminated by user")
    except Exception as e:
        print_error(f"An error occurred: {e}")