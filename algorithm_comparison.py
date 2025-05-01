# Algorithm Comparison Module
#
# This module provides functionality to compare different CPU scheduling algorithms
# by running them on the same set of processes and displaying comparative results.
# It helps visualize the trade-offs between different scheduling approaches.

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
        """Ensure all required metrics exist and are valid"""
        # Validate/Create Waiting Time
        if 'avg_waiting_time' not in metrics or metrics['avg_waiting_time'] <= 0:
            waiting_times = [p.completion_time - p.arrival_time - p.burst_time 
                            for p in processes if hasattr(p, 'completion_time')]
            metrics['avg_waiting_time'] = sum(waiting_times)/len(waiting_times) if waiting_times else 0.0

        # Validate/Create Turnaround Time
        if 'avg_turnaround_time' not in metrics or metrics['avg_turnaround_time'] <= 0:
            turnaround_times = [p.completion_time - p.arrival_time 
                            for p in processes if hasattr(p, 'completion_time')]
            metrics['avg_turnaround_time'] = sum(turnaround_times)/len(turnaround_times) if turnaround_times else 0.0

        # Validate/Create Response Time
        if 'avg_response_time' not in metrics or metrics['avg_response_time'] <= 0:
            response_times = []
            for p in processes:
                if hasattr(p, 'response_time'):
                    rt = p.response_time
                elif hasattr(p, 'first_execution'):
                    rt = p.first_execution - p.arrival_time
                else:
                    rt = getattr(p, 'waiting_time', 0)
                response_times.append(rt)
            metrics['avg_response_time'] = sum(response_times)/len(response_times) if response_times else 0.0

        # Validate/Create CPU Utilization (with 100% cap)
        if 'cpu_utilization' not in metrics or metrics['cpu_utilization'] <= 0:
            try:
                if metrics.get('schedule'):
                    total_time = max(t['finish'] for t in metrics['schedule'])
                    busy_time = sum(t['finish'] - t['start'] for t in metrics['schedule'])
                    metrics['cpu_utilization'] = min((busy_time/total_time)*100, 100) if total_time > 0 else 0
                else:
                    total_burst = sum(p.burst_time for p in processes)
                    max_comp = max((p.completion_time for p in processes if hasattr(p, 'completion_time')), default=0)
                    metrics['cpu_utilization'] = min((total_burst/max_comp)*100, 100) if max_comp > 0 else 0
            except:
                metrics['cpu_utilization'] = 0

    def display_comparison_results(self, results, color):
        """Display comparison results with proper equal-value handling"""
        print(f"\n{color.CYAN}{color.BOLD}{'═'*5} Results {'═'*40}{color.RESET}")
        table = self._create_comparison_table(results)
        print(table)
        
        print(f"\n{color.CYAN}{color.BOLD}{'═'*5} Analysis {'═'*38}{color.RESET}")
        
        for metric in self.metrics_to_compare:
            print(f"\n{color.YELLOW}• {self.metric_names[metric]}{color.RESET}:")
            is_higher_better = metric == "cpu_utilization"
            
            # Get all values
            algo_data = [(a_id, results[a_id]['name'], results[a_id]['metrics'].get(metric,0)) 
                        for a_id in results]
            values = [x[2] for x in algo_data]
            
            # Check for identical values
            if len(set(values)) == 1:
                unit = "%" if is_higher_better else ""
                print(f"  {color.GREEN}All equal:{color.RESET} {values[0]:.2f}{unit}")
                continue
                
            # Find best and worst
            best_algo = max(algo_data, key=lambda x: x[2]) if is_higher_better else min(algo_data, key=lambda x: x[2])
            best_id, best_name, best_val = best_algo
            
            # Print best
            unit = "%" if is_higher_better else ""
            print(f"  {color.GREEN}Best:{color.RESET} {best_name} ({best_val:.2f}{unit})")
            
            # Compare others
            for a_id, a_name, a_val in algo_data:
                if a_id == best_id:
                    continue
                    
                if a_val == best_val:
                    print(f"  {color.MAGENTA}•{color.RESET} {a_name}: Equal performance")
                    continue
                    
                if is_higher_better:
                    # CPU Utilization comparisons
                    if best_val == 0 or a_val == 0:
                        comparison = "N/A"
                    else:
                        ratio = best_val / a_val
                        comparison = f"{ratio:.1f}x better" if ratio > 1 else f"{1/ratio:.1f}x worse"
                else:
                    # Time-based comparisons
                    if best_val == 0:
                        comparison = "N/A"
                    else:
                        ratio = a_val / best_val
                        comparison = f"{ratio:.1f}x longer"
                
                print(f"  {color.MAGENTA}•{color.RESET} {a_name}: {comparison}")

    def export_results(self, results, processes, color):
        """Export results with proper equal-value handling"""
        filename = input(f"{color.BLUE}➜ Filename (default: comparison.txt): {color.GREEN}").strip() or "comparison.txt"
        
        with open(filename, 'w') as f:
            # Write metrics table
            f.write("COMPARISON RESULTS\n")
            
            # Build table data
            headers = ["Metric"] + [results[a_id]['name'] for a_id in results]
            table_data = []
            
            for metric in self.metrics_to_compare:
                row = [self.metric_names[metric]]
                for a_id in results:
                    value = results[a_id]['metrics'].get(metric, 0)
                    row.append(f"{value:.2f}")
                table_data.append(row)
            
            f.write(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # Write analysis
            f.write("\n\nANALYSIS:\n")
            for metric in self.metrics_to_compare:
                f.write(f"\n{self.metric_names[metric]}:\n")
                is_higher_better = metric == "cpu_utilization"
                
                # Get all values
                values = [results[a_id]['metrics'].get(metric,0) for a_id in results]
                
                # Check for identical values
                if len(set(values)) == 1:
                    unit = "%" if is_higher_better else ""
                    f.write(f"All algorithms have the same value: {values[0]:.2f}{unit}\n")
                    continue
                    
                # Find best
                best_val = max(values) if is_higher_better else min(values)
                best_algo = [a_id for a_id in results 
                            if results[a_id]['metrics'].get(metric,0) == best_val][0]
                best_name = results[best_algo]['name']
                
                f.write(f"Best: {best_name} ({best_val:.2f})\n")
                
                # Write comparisons
                for a_id in results:
                    if a_id == best_algo:
                        continue
                        
                    a_name = results[a_id]['name']
                    a_val = results[a_id]['metrics'].get(metric,0)
                    
                    if is_higher_better:
                        if best_val == 0 or a_val == 0:
                            comparison = "N/A"
                        else:
                            ratio = best_val / a_val
                            comparison = f"{ratio:.1f}x better" if ratio > 1 else f"{1/ratio:.1f}x worse"
                    else:
                        if best_val == 0:
                            comparison = "N/A"
                        else:
                            ratio = a_val / best_val
                            comparison = f"{ratio:.1f}x longer"
                    
                    f.write(f"- {a_name}: {comparison}\n")
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