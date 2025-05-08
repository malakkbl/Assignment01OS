# Implementation of Priority Non-Preemptive CPU Scheduling Algorithm

from typing import List
from process import Process

def priority_schedule(process_list: List[Process]):
    """
    Args:
        process_list: List of Process objects to be scheduled
    
    Returns:
        completed: List of Process objects after execution
        schedule: Timeline of process execution (pid, start, finish times)
        stats: Performance metrics including averages and CPU utilization
    """
    # Sort processes by arrival time for chronological processing
    arrival = sorted(process_list, key=lambda p: p.arrival_time)
    
    # Map priorities to their ready processes (FIFO queue per priority)
    ready = {}
    
    # Track execution timeline and statistics
    schedule = []        # Records when each process runs
    completed = []       # Collects finished processes
    idle_time = 0       # Tracks CPU idle periods
    first_response = {} # Records when processes first get CPU
    
    # Start clock at 0
    current_time =  0
    
    # Currently running process (None when CPU is idle)
    current = None
    
    # Main scheduling loop - continues while we have:
    # - Processes yet to arrive
    # - Processes in ready queues
    # - A process currently running
    while arrival or ready or current:
        # Move newly arrived processes to their priority queues
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            if p.priority in ready:
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]
        
        # If CPU is free, schedule highest priority ready process
        if ready:
            prio_to_run = min(ready)  # Lowest number = highest priority
            current = ready[prio_to_run].pop(0)
            if not ready[prio_to_run]:
                del ready[prio_to_run]
                
            # Track first time each process gets CPU
            if current.pid not in first_response:
                first_response[current.pid] = current_time - current.arrival_time
        
        # Handle CPU idle periods
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue
        
        # Execute current process to completion
        start = current_time
        finish = start + current.burst_time
        
        # Update process metrics
        turnaround = finish - current.arrival_time
        current.completion_time = finish
        current.turnaround_time = turnaround
        current.waiting_time = turnaround - current.burst_time
        
        # Record execution in schedule
        schedule.append({
            'pid': current.pid,
            'start': start,
            'finish': finish,
        })
        completed.append(current)
        
        # Update clock and free the CPU
        current_time = finish
        current = None
    
    # Calculate final performance metrics
    n = len(completed)
    avg_wait = sum(p.waiting_time for p in completed) / n
    avg_tat = sum(p.turnaround_time for p in completed) / n
    avg_resp = sum(first_response[p.pid] for p in completed) / n
    cpu_util = 100 * (current_time - idle_time) / current_time if current_time else 0
    
    stats = {
        "avg_waiting": avg_wait,
        "avg_turnaround": avg_tat,
        "avg_response": avg_resp,
        "cpu_utilisation": cpu_util
    }
    
    return completed, schedule, stats
