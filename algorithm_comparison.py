from tabulate import tabulate
from algorithms.fcfs import fcfs_schedule
from algorithms.priority_non_preemptive import priority_schedule
from algorithms.priority_preemptive import priority_preemptive_schedule
from algorithms.sjf import sjf
from algorithms.round_robin import round_robin
from algorithms.priority_rr import priority_round_robin
import copy
from colorama import init

# Initialize colorama for cross-platform terminal colors
init()

class AlgorithmComparison:
    """Class for comparing different CPU scheduling algorithms"""
    
    def __init__(self):
        # Dictionary mapping algorithm keys to (name, function) pairs
        self.algorithms = {
            "1": ("FCFS", fcfs_schedule),
            "2": ("Priority (non-preemptive)", priority_schedule),
            "3": ("Priority (preemptive)", priority_preemptive_schedule),
            "4": ("SJF", sjf),
            "5": ("Round-Robin", round_robin),
            "6": ("Priority + Round-Robin", priority_round_robin),
        }
        
        # Metrics to compare
        self.metrics_to_compare = [
            "avg_waiting_time", 
            "avg_turnaround_time", 
            "avg_response_time",
            "cpu_utilization"
        ]
        
        # Friendly names for metrics
        self.metric_names = {
            "avg_waiting_time": "Avg. Waiting Time",
            "avg_turnaround_time": "Avg. Turnaround Time",
            "avg_response_time": "Avg. Response Time",
            "cpu_utilization": "CPU Utilization %"
        }
        
        # Colors for charts
        self.colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
    
    def select_algorithms_to_compare(self, color):
        """Let the user select multiple algorithms to compare"""
        print(f"\n{color.CYAN}{color.BOLD}{'═' * 5} Select Algorithms to Compare {'═' * 25}{color.RESET}")
        
        # Display available algorithms
        for k, (name, _) in self.algorithms.items():
            print(f"  {color.CYAN}{k}{color.RESET}) {color.BOLD}{name}{color.RESET}")
        
        print(f"\n{color.YELLOW}Enter the numbers of algorithms to compare (comma-separated, e.g., 1,3,4){color.RESET}")
        
        while True:
            choices = input(f"{color.BOLD}{color.BLUE}➜ {color.RESET}Your choices: {color.GREEN}").strip()
            print(color.RESET, end="")
            
            # Split and clean choices
            selected = [c.strip() for c in choices.split(',') if c.strip()]
            
            # Validate
            if not selected:
                print(f"{color.RED}✗ Please select at least one algorithm{color.RESET}")
                continue
                
            if not all(s in self.algorithms for s in selected):
                print(f"{color.RED}✗ Invalid algorithm number(s). Please try again.{color.RESET}")
                continue
                
            # Return selected algorithms
            return [(s, self.algorithms[s][0], self.algorithms[s][1]) for s in selected]
    
    def get_quantum_if_needed(self, selected_algorithms, color):
        """Get time quantum for RR algorithms if needed"""
        quantum_needed = any("Round-Robin" in algo_name for _, algo_name, _ in selected_algorithms)
        
        if quantum_needed:
            while True:
                try:
                    quantum = int(input(f"{color.BOLD}{color.BLUE}➜ {color.RESET}Time quantum for RR algorithms (> 0): {color.GREEN}").strip())
                    print(color.RESET, end="")
                    
                    if quantum > 0:
                        return quantum
                    print(f"{color.YELLOW}⚠️  Time quantum must be positive{color.RESET}")
                except ValueError:
                    print(f"{color.RED}✗ Please enter a valid number{color.RESET}")
        
        return None  # No quantum needed
    
    def run_comparison(self, processes, selected_algorithms, quantum=None, color=None):
        """Run all selected algorithms and collect results"""
        results = {}
        
        print(f"\n{color.CYAN}{color.BOLD}{'═' * 5} Running Algorithms {'═' * 35}{color.RESET}")
        
        for algo_id, algo_name, algo_fn in selected_algorithms:
            # Create a deep copy of processes to avoid modifying the original
            process_copy = copy.deepcopy(processes)
            
            print(f"  {color.CYAN}•{color.RESET} Processing {color.BOLD}{algo_name}{color.RESET}...")
            
            # Run the algorithm
            if "Round-Robin" in algo_name and quantum is not None:
                result_processes, schedule, metrics = algo_fn(process_copy, quantum)
            else:
                result_processes, schedule, metrics = algo_fn(process_copy)
            
            # Ensure all required metrics exist and are valid
            self._validate_and_fix_metrics(metrics, result_processes)
            
            # Store results
            results[algo_id] = {
                'name': algo_name,
                'processes': result_processes,
                'schedule': schedule,
                'metrics': metrics
            }
            
            print(f"    {color.GREEN}✓{color.RESET} Completed")
        
        return results
    
    def _validate_and_fix_metrics(self, metrics, processes):
        """Ensure all required metrics exist and are valid, calculate them if missing"""
        # Check if avg_waiting_time is missing or zero
        if 'avg_waiting_time' not in metrics or metrics['avg_waiting_time'] == 0:
            waiting_times = [p.waiting_time for p in processes if hasattr(p, 'waiting_time')]
            if waiting_times:
                metrics['avg_waiting_time'] = sum(waiting_times) / len(waiting_times)
            else:
                # Calculate waiting time if not set
                waiting_times = []
                for p in processes:
                    if hasattr(p, 'completion_time') and hasattr(p, 'burst_time') and hasattr(p, 'arrival_time'):
                        p.waiting_time = p.completion_time - p.burst_time - p.arrival_time
                        waiting_times.append(p.waiting_time)
                
                if waiting_times:
                    metrics['avg_waiting_time'] = sum(waiting_times) / len(waiting_times)
                else:
                    metrics['avg_waiting_time'] = 0.0  # Default value
        
        # Check if avg_turnaround_time is missing or zero
        if 'avg_turnaround_time' not in metrics or metrics['avg_turnaround_time'] == 0:
            turnaround_times = [p.turnaround_time for p in processes if hasattr(p, 'turnaround_time')]
            if turnaround_times:
                metrics['avg_turnaround_time'] = sum(turnaround_times) / len(turnaround_times)
            else:
                # Calculate turnaround time if not set
                turnaround_times = []
                for p in processes:
                    if hasattr(p, 'completion_time') and hasattr(p, 'arrival_time'):
                        p.turnaround_time = p.completion_time - p.arrival_time
                        turnaround_times.append(p.turnaround_time)
                
                if turnaround_times:
                    metrics['avg_turnaround_time'] = sum(turnaround_times) / len(turnaround_times)
                else:
                    metrics['avg_turnaround_time'] = 0.0  # Default value
        
        # Check if avg_response_time is missing or zero
        if 'avg_response_time' not in metrics or metrics['avg_response_time'] == 0:
            response_times = [p.response_time for p in processes if hasattr(p, 'response_time')]
            if response_times:
                metrics['avg_response_time'] = sum(response_times) / len(response_times)
            else:
                # Look for first_response_time attribute or calculate it
                response_times = []
                for p in processes:
                    if hasattr(p, 'first_response_time'):
                        p.response_time = p.first_response_time - p.arrival_time
                    elif hasattr(p, 'first_execution') and hasattr(p, 'arrival_time'):
                        p.response_time = p.first_execution - p.arrival_time
                    else:
                        # Default to waiting time if no better data available
                        if hasattr(p, 'waiting_time'):
                            p.response_time = p.waiting_time
                    
                    if hasattr(p, 'response_time'):
                        response_times.append(p.response_time)
                
                if response_times:
                    metrics['avg_response_time'] = sum(response_times) / len(response_times)
                else:
                    metrics['avg_response_time'] = 0.0  # Default value
        
        # Check if cpu_utilization is missing
        if 'cpu_utilization' not in metrics or metrics['cpu_utilization'] == 0:
            # Calculate from schedule if available
            if 'schedule' in metrics and metrics['schedule']:
                total_time = max(task['finish'] for task in metrics['schedule'])
                busy_time = sum(task['finish'] - task['start'] for task in metrics['schedule'])
                if total_time > 0:
                    metrics['cpu_utilization'] = (busy_time / total_time) * 100
                else:
                    metrics['cpu_utilization'] = 0.0
            else:
                # Calculate from process burst times
                if processes:
                    total_burst = sum(p.burst_time for p in processes)
                    max_completion = max((p.completion_time for p in processes if hasattr(p, 'completion_time')), default=0)
                    if max_completion > 0:
                        metrics['cpu_utilization'] = (total_burst / max_completion) * 100
                    else:
                        metrics['cpu_utilization'] = 0.0
                else:
                    metrics['cpu_utilization'] = 0.0
    
    def _create_comparison_table(self, results):
        """Create a comparison table of metrics for all algorithms"""
        # Prepare table headers
        headers = ["Metric"]
        for algo_id in results:
            headers.append(results[algo_id]['name'])
        
        # Prepare table rows
        rows = []
        for metric in self.metrics_to_compare:
            row = [self.metric_names[metric]]
            
            for algo_id in results:
                # Format the metric value to 2 decimal places
                value = results[algo_id]['metrics'].get(metric, 0)
                row.append(f"{value:.2f}")
            
            rows.append(row)
        
        # Create table using tabulate
        table = tabulate(rows, headers, tablefmt="grid")
        return table
    
    def display_comparison_results(self, results, color):
        """Display the comparison results in a formatted way"""
        # Display comparison table
        print(f"\n{color.CYAN}{color.BOLD}{'═' * 5} Algorithm Comparison Results {'═' * 25}{color.RESET}")
        table = self._create_comparison_table(results)
        print(table)
        
        # Analyze and highlight the best algorithm for each metric
        print(f"\n{color.CYAN}{color.BOLD}{'═' * 5} Analysis {'═' * 40}{color.RESET}")
        
        for metric in self.metrics_to_compare:
            print(f"\n{color.YELLOW}• {self.metric_names[metric]}{color.RESET}:")
            
            # For CPU utilization, higher is better; for other metrics, lower is better
            is_higher_better = metric == "cpu_utilization"
            
            # Get metric values for all algorithms
            metric_values = [(algo_id, results[algo_id]['metrics'].get(metric, 0)) 
                             for algo_id in results]
            
            # Check if all algorithms have the same value for this metric
            all_same = len(set(value for _, value in metric_values)) == 1
            if all_same:
                value = metric_values[0][1]
                unit = "%" if metric == "cpu_utilization" else ""
                print(f"  {color.YELLOW}All algorithms have the same value ({value:.2f}{unit}){color.RESET}")
                continue
            
            # Skip analysis if all values are 0
            if all(value == 0 for _, value in metric_values):
                print(f"  {color.YELLOW}All algorithms have the same value (0.00){color.RESET}")
                continue
                
            # Find best algorithm based on the metric
            if is_higher_better:
                best_algo_id = max(metric_values, key=lambda x: x[1])[0]
                best_value = results[best_algo_id]['metrics'].get(metric, 0)
                print(f"  {color.GREEN}Best:{color.RESET} {color.BOLD}{results[best_algo_id]['name']}{color.RESET} ({best_value:.2f}%)")
            else:
                best_algo_id = min(metric_values, key=lambda x: x[1])[0]
                best_value = results[best_algo_id]['metrics'].get(metric, 0)
                print(f"  {color.GREEN}Best:{color.RESET} {color.BOLD}{results[best_algo_id]['name']}{color.RESET} ({best_value:.2f})")
            
            # Calculate how much better/worse other algorithms are
            for algo_id in results:
                if algo_id != best_algo_id:
                    current_value = results[algo_id]['metrics'].get(metric, 0)
                    
                    # Handle case where values are the same
                    if abs(best_value - current_value) < 0.0001:  # Floating point comparison
                        print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} has the same value")
                        continue
                    
                    # Skip percentage calculation if one value is 0 (to avoid division by zero)
                    if best_value == 0 or current_value == 0:
                        if is_higher_better:
                            better = best_value > current_value
                            print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} performs {'worse' if better else 'better'}")
                        else:
                            better = best_value < current_value
                            print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} performs {'worse' if better else 'better'}")
                        continue
                        
                    # Calculate percentage difference with proper wording
                    if is_higher_better:
                        # For metrics where higher is better (like CPU utilization)
                        percent_diff = ((best_value - current_value) / current_value) * 100
                        if percent_diff > 0:
                            print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} is {percent_diff:.2f}% lower")
                        else:
                            print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} is {abs(percent_diff):.2f}% higher")
                    else:
                        # For metrics where lower is better (like waiting time)
                        diff = current_value - best_value
                        if diff == 0:
                            print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} has the same performance")
                        else:
                            percent_diff = (diff / best_value) * 100
                            if percent_diff > 100:
                                # If more than double, express as "X times longer"
                                times = current_value / best_value
                                print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} takes {times:.2f}x longer")
                            else:
                                print(f"  {color.MAGENTA}•{color.RESET} {results[algo_id]['name']} takes {percent_diff:.2f}% longer")
    
    def export_results(self, results, processes, color):
        """Export comparison results to a file"""
        print(f"\n{color.CYAN}{color.BOLD}{'═' * 5} Export Results {'═' * 35}{color.RESET}")
        print(f"{color.YELLOW}Would you like to export the comparison results? (y/n){color.RESET}")
        
        choice = input(f"{color.BOLD}{color.BLUE}➜ {color.RESET}Your choice: {color.GREEN}").strip().lower()
        print(color.RESET, end="")
        
        if choice != 'y':
            return
        
        filename = input(f"{color.BOLD}{color.BLUE}➜ {color.RESET}Enter filename (default: comparison_results.txt): {color.GREEN}").strip() or "comparison_results.txt"
        print(color.RESET, end="")
        
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write("CPU SCHEDULING ALGORITHM COMPARISON\n")
                f.write("=================================\n\n")
                
                # Write process information
                f.write("PROCESSES USED FOR COMPARISON:\n")
                f.write("PID\tArrival\tBurst\tPriority\n")
                for p in processes:
                    priority = getattr(p, 'priority', 'N/A')
                    f.write(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{priority}\n")
                f.write("\n")
                
                # Write comparison table
                f.write("COMPARISON RESULTS:\n")
                table = self._create_comparison_table(results)
                f.write(table + "\n\n")
                
                # Write analysis
                f.write("ANALYSIS:\n")
                for metric in self.metrics_to_compare:
                    f.write(f"\n{self.metric_names[metric]}:\n")
                    
                    is_higher_better = metric == "cpu_utilization"
                    
                    # Get metric values for all algorithms
                    metric_values = [(algo_id, results[algo_id]['metrics'].get(metric, 0)) 
                                    for algo_id in results]
                    
                    # Check if all algorithms have the same value for this metric
                    all_same = len(set(value for _, value in metric_values)) == 1
                    if all_same:
                        value = metric_values[0][1]
                        unit = "%" if metric == "cpu_utilization" else ""
                        f.write(f"All algorithms have the same value ({value:.2f}{unit})\n")
                        continue
                    
                    # Skip analysis if all values are 0
                    if all(value == 0 for _, value in metric_values):
                        f.write(f"All algorithms have the same value (0.00)\n")
                        continue
                    
                    if is_higher_better:
                        best_algo_id = max(metric_values, key=lambda x: x[1])[0]
                        best_value = results[best_algo_id]['metrics'].get(metric, 0)
                        f.write(f"Best: {results[best_algo_id]['name']} ({best_value:.2f}%)\n")
                    else:
                        best_algo_id = min(metric_values, key=lambda x: x[1])[0]
                        best_value = results[best_algo_id]['metrics'].get(metric, 0)
                        f.write(f"Best: {results[best_algo_id]['name']} ({best_value:.2f})\n")
                    
                    for algo_id in results:
                        if algo_id != best_algo_id:
                            current_value = results[algo_id]['metrics'].get(metric, 0)
                            
                            # Handle case where values are the same
                            if abs(best_value - current_value) < 0.0001:  # Floating point comparison
                                f.write(f"- {results[algo_id]['name']} has the same value\n")
                                continue
                            
                            # Skip percentage calculation if one value is 0 (to avoid division by zero)
                            if best_value == 0 or current_value == 0:
                                if is_higher_better:
                                    better = best_value > current_value
                                    f.write(f"- {results[algo_id]['name']} performs {'worse' if better else 'better'}\n")
                                else:
                                    better = best_value < current_value
                                    f.write(f"- {results[algo_id]['name']} performs {'worse' if better else 'better'}\n")
                                continue
                                
                            # Calculate percentage difference with proper wording
                            if is_higher_better:
                                # For metrics where higher is better (like CPU utilization)
                                percent_diff = ((best_value - current_value) / current_value) * 100
                                if percent_diff > 0:
                                    f.write(f"- {results[algo_id]['name']} is {percent_diff:.2f}% lower\n")
                                else:
                                    f.write(f"- {results[algo_id]['name']} is {abs(percent_diff):.2f}% higher\n")
                            else:
                                # For metrics where lower is better (like waiting time)
                                diff = current_value - best_value
                                if diff == 0:
                                    f.write(f"- {results[algo_id]['name']} has the same performance\n")
                                else:
                                    percent_diff = (diff / best_value) * 100
                                    if percent_diff > 100:
                                        # If more than double, express as "X times longer"
                                        times = current_value / best_value
                                        f.write(f"- {results[algo_id]['name']} takes {times:.2f}x longer\n")
                                    else:
                                        f.write(f"- {results[algo_id]['name']} takes {percent_diff:.2f}% longer\n")
            
            print(f"{color.GREEN}✓ Results exported to {filename}{color.RESET}")
        except Exception as e:
            print(f"{color.RED}✗ Error exporting results: {e}{color.RESET}")

def run_algorithm_comparison(processes, color):
    """Main function to run the algorithm comparison"""
    comparator = AlgorithmComparison()
    
    # Select algorithms to compare
    selected_algorithms = comparator.select_algorithms_to_compare(color)
    
    # Get time quantum if needed
    quantum = comparator.get_quantum_if_needed(selected_algorithms, color)
    
    # Run comparison
    results = comparator.run_comparison(processes, selected_algorithms, quantum, color)
    
    # Display results
    comparator.display_comparison_results(results, color)
    
    # Export results
    comparator.export_results(results, processes, color)
    
    return results