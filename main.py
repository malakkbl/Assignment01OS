# Main driver for CPU Scheduling Simulator
# This module provides a command-line interface for testing and comparing
# different CPU scheduling algorithms. It handles user input, process creation,
# algorithm selection, and result visualization.

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
import json
import pandas as pd
from datetime import datetime

# Terminal UI Components
# Color class provides ANSI escape codes for terminal text formatting
# These codes enable colored output and text styling for better UX
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

# UI Helper Functions
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

# Core Menu Functions

# Function of comparison mode, do you want single or comparison mode?
def choose_mode():
    """
    Display mode selection menu and handle user input.
    Returns:
        str: 'single' for single algorithm mode or 'comparison' for comparison mode
    """
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
    """
    Display algorithm selection menu and handle user input.
    Returns:
        tuple: (algorithm_name, algorithm_function) for the chosen algorithm
    """
    # Dictionary mapping menu options to (name, function) pairs
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

def choose_input_method():
    """Choose between manual entry, JSON file, or Excel file."""
    print_subheader("INPUT METHOD")
    print(f"  {Color.CYAN}1{Color.RESET}) {Color.BOLD}Manual Entry{Color.RESET} - Input process details manually")
    print(f"  {Color.CYAN}2{Color.RESET}) {Color.BOLD}JSON File{Color.RESET} - Import processes from a JSON file")
    print(f"  {Color.CYAN}3{Color.RESET}) {Color.BOLD}Excel/CSV File{Color.RESET} - Import from Excel or CSV file")
    
    while True:
        choice = input_styled("Choose input method").strip()
        print(Color.RESET, end="")
        
        if choice in ["1", "2", "3"]:
            return choice
        
        print_error("Invalid option – try again.")
        time.sleep(1)

def choose_output_method():
    """Choose between terminal display only or saving to file."""
    print_subheader("OUTPUT METHOD")
    print(f"  {Color.CYAN}1{Color.RESET}) {Color.BOLD}Terminal Only{Color.RESET} - Display results in terminal")
    print(f"  {Color.CYAN}2{Color.RESET}) {Color.BOLD}Save to Text File{Color.RESET} - Save results to a text file")
    print(f"  {Color.CYAN}3{Color.RESET}) {Color.BOLD}Save to JSON{Color.RESET} - Save results to a JSON file")
    print(f"  {Color.CYAN}4{Color.RESET}) {Color.BOLD}Save to Excel{Color.RESET} - Save results to an Excel file")
    print(f"  {Color.CYAN}5{Color.RESET}) {Color.BOLD}Save to CSV{Color.RESET} - Save results to a CSV file")
    
    while True:
        choice = input_styled("Choose output method").strip()
        print(Color.RESET, end="")
        
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        
        print_error("Invalid option – try again.")
        time.sleep(1)

# ------------- DATA ENTRY --------------

def read_processes(need_priority: bool = False):
    """Choose input method and read processes accordingly."""
    input_method = choose_input_method()
    
    if input_method == "1":
        return read_processes_manually(need_priority)
    elif input_method == "2":
        return read_processes_from_json(need_priority)
    elif input_method == "3":
        return read_processes_from_excel(need_priority)
    else:
        # Fallback to manual entry
        return read_processes_manually(need_priority)
    
def read_processes_manually(need_priority: bool = False):
    """
    Interactive process data collection with input validation.
    
    Args:
        need_priority: Whether to collect priority values (for priority-based algorithms)
    
    Returns:
        list: List of Process objects with user-specified attributes
    
    Features:
    - Auto-generated PIDs (1, 2, 3, ...)
    - Input validation for all fields
    - Clear error messages for invalid input
    - Support for priority and non-priority algorithms
    """
    print_subheader("PROCESS INFORMATION")
    
    try:
        n = int(input_styled("Number of processes").strip())
        if n <= 0:
            print_error("Number of processes must be positive")
            return read_processes_manually(need_priority)
    except ValueError:
        print_error("Please enter a valid number")
        return read_processes_manually(need_priority)
    
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
            # Priority with validation
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

def read_processes_from_json(need_priority: bool = False):
    """Read process information from a JSON file."""
    print_subheader("JSON FILE INPUT")
    print("Just know that even if you put pids for processes they wont be taken into considertion and will be auto generated")
    
    while True:
        filename = input_styled("Enter JSON file path").strip()
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                
                if not isinstance(data, list):
                    print_error("JSON file must contain a list of process objects")
                    continue
                
                processes = []
                
                for i, proc in enumerate(data, start=1):
                    # Check required fields
                    if 'arrival_time' not in proc or 'burst_time' not in proc:
                        print_error(f"Process #{i} is missing required fields (arrival_time or burst_time)")
                        continue
                    
                    # Extract values with validation
                    try:
                        arrival = int(proc['arrival_time'])
                        burst = int(proc['burst_time'])
                        
                        if arrival < 0:
                            print_warning(f"Process #{i} has negative arrival time, setting to 0")
                            arrival = 0
                        
                        if burst <= 0:
                            print_warning(f"Process #{i} has invalid burst time, setting to 1")#just a default value could be 0
                            burst = 1
                        
                        # Always read priority if available
                        priority = int(proc.get('priority', 0))  # Default to 0 if missing
                        if priority < 0:
                            print_warning(f"Process #{i} has negative priority, setting to 0")
                            priority = 0
                        
                        # Only require validation if the algorithm needs priority
                        if need_priority and 'priority' not in proc:
                            print_warning(f"Process #{i} is missing priority, setting to 0")
                            priority = 0
                        
                        processes.append(Process(i, arrival, burst, priority))
                    
                    except ValueError:
                        print_error(f"Process #{i} has invalid numeric values")
                        continue
                
                if not processes:
                    print_error("No valid processes found in the JSON file")
                    continue
                
                print_success(f"Successfully loaded {len(processes)} processes from {filename}")
                return processes
                
        except FileNotFoundError:
            print_error(f"File not found: {filename}")
        except json.JSONDecodeError:
            print_error(f"Invalid JSON format in file: {filename}")
        except Exception as e:
            print_error(f"Error reading file: {str(e)}")
        
        retry = input_styled("Try another file? (y/n)").lower().strip()
        if retry != 'y':
            print_warning("Falling back to manual entry...")
            return read_processes_manually(need_priority)

def read_processes_from_excel(need_priority: bool = False):
    """Read process information from an Excel or CSV file."""
    print_subheader("EXCEL/CSV FILE INPUT")
    
    while True:
        filename = input_styled("Enter file path").strip()
        try:
            # Detect file type and read appropriately
            if filename.endswith('.csv'):
                df = pd.read_csv(filename)
            else:
                df = pd.read_excel(filename)
            
            # Check required columns
            required_cols = ['arrival_time', 'burst_time']
            if need_priority:
                required_cols.append('priority')
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print_error(f"Missing required columns: {', '.join(missing_cols)}")
                print_warning("File must have columns: arrival_time, burst_time" + 
                            (", priority" if need_priority else ""))
                continue
            
            # Process the data
            processes = []
            for i, row in df.iterrows():
                pid = i + 1  # Auto-generate PIDs starting from 1
                
                try:
                    arrival = int(row['arrival_time'])
                    burst = int(row['burst_time'])
                    
                    if arrival < 0:
                        print_warning(f"Process #{pid} has negative arrival time, setting to 0")
                        arrival = 0
                    
                    if burst <= 0:
                        print_warning(f"Process #{pid} has invalid burst time, setting to 1")
                        burst = 1
                    
                    # Handle priority for all cases
                    priority = 0
                    if 'priority' in df.columns and not pd.isna(row['priority']):
                        try:
                            priority = int(row['priority'])
                            if priority < 0:
                                print_warning(f"Process #{pid} has negative priority, setting to 0")
                                priority = 0
                        except ValueError:
                            print_warning(f"Invalid priority for Process #{pid}, using 0")
                    
                    processes.append(Process(pid, arrival, burst, priority))
                
                except (ValueError, TypeError):
                    print_warning(f"Skipping row {i+1} due to invalid numeric values")
                    continue
            
            if not processes:
                print_error("No valid processes found in the file")
                continue
            
            print_success(f"Successfully loaded {len(processes)} processes from {filename}")
            return processes
            
        except FileNotFoundError:
            print_error(f"File not found: {filename}")
        except Exception as e:
            print_error(f"Error reading file: {str(e)}")
        
        retry = input_styled("Try another file? (y/n)").lower().strip()
        if retry != 'y':
            print_warning("Falling back to manual entry...")
            return read_processes_manually(need_priority)

            


# REPORTING
def print_schedule(tbl):
    """
    Display execution schedule in tabular format.
    Shows when each process starts and finishes, with total makespan.
    
    Args:
        tbl: List of dicts containing execution records
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
    """
    Display per-process statistics in tabular format.
    Shows waiting time, turnaround time, and completion time for each process.
    
    Args:
        processes: List of completed Process objects with calculated metrics
    """
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
    """
    Display overall algorithm performance metrics.
    Shows averages for waiting time, turnaround time, and CPU utilization.
    
    Args:
        metrics: Dictionary containing calculated performance metrics
    """
    print_subheader("PERFORMANCE METRICS")
    
    # Use a more visual presentation for metrics
    for key, value in metrics.items():
        metric_name = key.replace('_', ' ').title()
        print(f"  {Color.YELLOW}{metric_name}:{Color.RESET} {Color.BOLD}{value:.2f}{Color.RESET}")

def generate_text_report(algo_name, processes, schedule_table, metrics):
    """Generate a text report of the scheduling results."""
    report = []
    report.append("=" * 60)
    report.append(f"CPU SCHEDULER SIMULATION REPORT")
    report.append(f"Algorithm: {algo_name}")
    report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    # Schedule
    report.append("\nSCHEDULE")
    report.append("-" * 26)
    report.append(f"{'PID':<6}{'Start':<10}{'Finish':<10}")
    report.append("-" * 26)
    
    for row in schedule_table:
        report.append(f"{row['pid']:<6}{row['start']:<10}{row['finish']:<10}")
    
    makespan = max(r['finish'] for r in schedule_table) if schedule_table else 0
    report.append(f"\nMakespan: {makespan}")
    
    # Process statistics
    report.append("\nPROCESS STATISTICS")
    report.append("-" * 50)
    report.append(f"{'PID':<6}{'Waiting Time':<16}{'Turnaround':<14}{'Completion':<14}")
    report.append("-" * 50)
    
    for proc in processes:
        report.append(f"{proc.pid:<6}{proc.waiting_time:<16}{proc.turnaround_time:<14}{proc.completion_time:<14}")
    
    # Metrics
    report.append("\nPERFORMANCE METRICS")
    report.append("-" * 30)
    
    for key, value in metrics.items():
        metric_name = key.replace('_', ' ').title()
        report.append(f"{metric_name}: {value:.2f}")
    
    return "\n".join(report)

def save_to_text_file(algo_name, processes, schedule_table, metrics):
    """Save results to a text file."""
    report = generate_text_report(algo_name, processes, schedule_table, metrics)
    filename = f"cpu_schedule_{algo_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(filename, 'w') as f:
            f.write(report)
        print_success(f"Results saved to {filename}")
    except Exception as e:
        print_error(f"Failed to save results: {e}")

def save_to_json_file(algo_name, processes, schedule_table, metrics):
    """Save results to a JSON file."""
    result_data = {
        "algorithm": algo_name,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "schedule": schedule_table,
        "processes": [
            {
                "pid": p.pid,
                "arrival_time": p.arrival_time,
                "burst_time": p.burst_time,
                "priority": getattr(p, 'priority', None),
                "waiting_time": p.waiting_time,
                "turnaround_time": p.turnaround_time,
                "completion_time": p.completion_time
            } for p in processes
        ],
        "metrics": metrics
    }
    
    filename = f"cpu_schedule_{algo_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=2)
        print_success(f"Results saved to {filename}")
    except Exception as e:
        print_error(f"Failed to save results: {e}")

def save_to_excel_file(algo_name, processes, schedule_table, metrics):
    """Save results to an Excel file."""
    filename = f"cpu_schedule_{algo_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    try:
        with pd.ExcelWriter(filename) as writer:
            # Process data
            process_data = []
            for p in processes:
                process_dict = {
                    "PID": p.pid,
                    "Arrival Time": p.arrival_time,
                    "Burst Time": p.burst_time,
                    "Waiting Time": p.waiting_time,
                    "Turnaround Time": p.turnaround_time,
                    "Completion Time": p.completion_time
                }
                
                if hasattr(p, 'priority'):
                    process_dict["Priority"] = p.priority
                
                process_data.append(process_dict)
            
            pd.DataFrame(process_data).to_excel(writer, sheet_name='Processes', index=False)
            
            # Schedule data
            pd.DataFrame(schedule_table).to_excel(writer, sheet_name='Schedule', index=False)
            
            # Metrics
            metrics_df = pd.DataFrame([metrics])
            metrics_df.columns = [col.replace('_', ' ').title() for col in metrics_df.columns]
            metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
            
            # Info sheet
            info_data = {
                "Info": ["Algorithm", "Date", "Time", "Makespan"],
                "Value": [
                    algo_name,
                    datetime.now().strftime('%Y-%m-%d'),
                    datetime.now().strftime('%H:%M:%S'),
                    max(r['finish'] for r in schedule_table) if schedule_table else 0
                ]
            }
            pd.DataFrame(info_data).to_excel(writer, sheet_name='Info', index=False)
        
        print_success(f"Results saved to {filename}")
    except Exception as e:
        print_error(f"Failed to save results: {e}")

def save_to_csv_file(algo_name, processes, schedule_table, metrics):
    """Save results to CSV files."""
    base_filename = f"cpu_schedule_{algo_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Process data
        process_data = []
        for p in processes:
            process_dict = {
                "PID": p.pid,
                "Arrival Time": p.arrival_time,
                "Burst Time": p.burst_time,
                "Waiting Time": p.waiting_time,
                "Turnaround Time": p.turnaround_time,
                "Completion Time": p.completion_time
            }
            
            # Add priority if available
            if hasattr(p, 'priority'):
                process_dict["Priority"] = p.priority
            
            process_data.append(process_dict)
        
        # Save to CSV files
        processes_file = f"{base_filename}_processes.csv"
        schedule_file = f"{base_filename}_schedule.csv"
        metrics_file = f"{base_filename}_metrics.csv"
        
        pd.DataFrame(process_data).to_csv(processes_file, index=False)
        pd.DataFrame(schedule_table).to_csv(schedule_file, index=False)
        
        # Metrics
        metrics_df = pd.DataFrame([metrics])
        metrics_df.columns = [col.replace('_', ' ').title() for col in metrics_df.columns]
        metrics_df.to_csv(metrics_file, index=False)
        
        print_success(f"Results saved to {processes_file}, {schedule_file}, and {metrics_file}")
    except Exception as e:
        print_error(f"Failed to save results: {e}")

def save_results(output_choice, algo_name, processes, schedule_table, metrics):
    """Save results based on the chosen output method."""
    if output_choice == "1":
        # Terminal only - already displayed
        pass
    elif output_choice == "2":
        save_to_text_file(algo_name, processes, schedule_table, metrics)
    elif output_choice == "3":
        save_to_json_file(algo_name, processes, schedule_table, metrics)
    elif output_choice == "4":
        save_to_excel_file(algo_name, processes, schedule_table, metrics)
    elif output_choice == "5":
        save_to_csv_file(algo_name, processes, schedule_table, metrics)
# DRIVER 
def main():
    """
    Main program entry point. Handles:
    1. Mode selection (single/comparison)
    2. Algorithm selection (if single mode)
    3. Process data collection
    4. Algorithm execution
    5. Result visualization
    
    Includes error handling for:
    - User interruption (Ctrl+C)
    - Invalid inputs
    - Runtime errors
    """
    clear_screen()
    print_header("CPU SCHEDULER SIMULATOR")
    print(f"\n{Color.YELLOW}Welcome to the CPU Scheduler Simulator!{Color.RESET}")
    print("This tool demonstrates various CPU scheduling algorithms.")
    
    # Mode Selection
    mode = choose_mode()
    
    if mode == "single":
        # Single algorithm mode
        algo_name, algo_fn = choose_algorithm()
        need_priority = "Priority" in algo_name
        processes = read_processes(need_priority)
        
        # Handle Round-Robin Quantum Input
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
        
        # Execute Selected Algorithm
        print_loading(f"Scheduling with {algo_name}")
        if quantum is not None:
            list_processes, schedule_table, metrics = algo_fn(processes, quantum)
        else:
            list_processes, schedule_table, metrics = algo_fn(processes)
        
        # Display Results
        print_success(f"Scheduled {len(processes)} processes using {Color.BOLD}{algo_name}{Color.RESET}")
        print_schedule(schedule_table)
        print_process_stats(list_processes)
        print_metrics(metrics)
        
        # Output results
        output_choice = choose_output_method()
        save_results(output_choice, algo_name, list_processes, schedule_table, metrics)
    
    else:
        # Comparison mode - no file output needed
        need_priority = True
        processes = read_processes(need_priority)
        
        # Run the comparison 
        print_loading("Running algorithm comparison")
        results = run_algorithm_comparison(processes, Color)
        print_success("Algorithm comparison completed! Check above for results.")
    
    print_footer()

# Entry Point with Error Handling
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nProgram terminated by user")
    except Exception as e:
        print_error(f"An error occurred: {e}")
