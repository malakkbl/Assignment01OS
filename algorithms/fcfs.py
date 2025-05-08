# First-Come, First-Served (FCFS) Scheduling Algorithm

from typing import List, Tuple, Dict
from process import Process

def fcfs_schedule(process_list: List[Process]) -> Tuple[List[Process], List[dict], Dict[str, float]]:
    """
    First-Come-First-Served scheduler.
    
    Args:
        process_list: List of Process objects to be scheduled
    
    Returns:
        completed: List of Process objects after execution
        schedule: Timeline of process execution (pid, start, finish)
        stats: Performance metrics including averages and utilization
    """
    # Sort processes by arrival time for chronological processing
    procs = sorted(process_list, key=lambda p: p.arrival_time)
    
    # Track execution timeline and metrics
    schedule = []        # Records when each process runs
    completed = []       # Collects finished processes
    idle_time = 0       # Tracks CPU idle periods
    first_response = {} # Records when processes first get CPU
    
    # Start clock at 0
    clock =  0
    
    # Process each job in arrival order
    for proc in procs:
        # Determine when this process can start
        start = max(clock, proc.arrival_time)
        
        # Track any idle gap before this process
        if start > clock:
            idle_time += start - clock
            
        # Record first response time (same as start in FCFS)
        first_response[proc.pid] = start - proc.arrival_time
        
        # Execute process and calculate metrics
        finish = start + proc.burst_time
        proc.turnaround_time = finish - proc.arrival_time
        proc.waiting_time = proc.turnaround_time - proc.burst_time
        proc.completion_time = finish
        
        # Record execution in schedule
        schedule.append({
            'pid': proc.pid,
            'start': start,
            'finish': finish,
        })
        completed.append(proc)
        
        # Advance clock to process completion
        clock = finish
    
    # Calculate final performance metrics
    n = len(completed)
    avg_wait = sum(p.waiting_time for p in completed) / n if n else 0
    avg_tat = sum(p.turnaround_time for p in completed) / n if n else 0
    avg_resp = sum(first_response[p.pid] for p in completed) / n if n else 0
    cpu_util = 100 * (clock - idle_time) / clock if clock else 0
    
    stats = {
        "avg_waiting": avg_wait,
        "avg_turnaround": avg_tat,
        "avg_response": avg_resp,
        "cpu_utilisation": cpu_util
    }
    
    return completed, schedule, stats


