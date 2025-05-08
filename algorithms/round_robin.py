from collections import deque
from typing import List, Tuple
from process import Process


def round_robin(processes: List[Process], quantum: int = 4):
    """
    Round Robin scheduler with fixed time quantum.
    
    Args:
        processes: List of Process objects to be scheduled
        quantum: Maximum time slice given to each process
    
    Returns:
        completed: List of Process objects with final metrics
        schedule: Timeline of execution records
        stats: Performance metrics including averages and utilization
    """
    # Sort processes by arrival time for chronological processing
    processes = sorted(processes, key=lambda p: p.arrival_time)
    
    # Use deque for O(1) append/pop operations on ready queue
    ready_q: deque[Process] = deque()
    completed: List[Process] = []     # Store finished processes
    schedule: List[dict] = []         # Record execution timeline
    
    # Track system metrics
    clock = 0                         # Current simulation time
    idle_time = 0                     # Total CPU idle time
    response_times = {}               # Track when each process first gets CPU
    
    # Main scheduling loop - continue while we have:
    # - Processes yet to arrive
    # - Processes in ready queue
    while processes or ready_q:
        # Move newly arrived processes to ready queue
        while processes and processes[0].arrival_time <= clock:
            ready_q.append(processes.pop(0))
            
        # Handle CPU idle time
        if not ready_q:
            next_arrival = processes[0].arrival_time
            idle_time += next_arrival - clock
            clock = next_arrival
            continue
            
        # Select next process from ready queue
        current = ready_q.popleft()
        
        # Record response time ONLY if this is the first time the process gets CPU
        if current.pid not in response_times:
            response_times[current.pid] = clock - current.arrival_time
            
        # Calculate execution time for this quantum
        run_time = min(quantum, current.remaining_time)
        start = clock
        clock += run_time
        current.remaining_time -= run_time
        
        # Record this execution slice
        schedule.append({
            'pid': current.pid,
            'start': start,
            'finish': clock
        })
        
        # Handle process state after execution
        if current.remaining_time > 0:
            # Process not finished - handle new arrivals and re-queue
            while processes and processes[0].arrival_time <= clock:
                ready_q.append(processes.pop(0))
            ready_q.append(current)
        else:
            # Process completed - update its metrics
            current.completion_time = clock
            current.turnaround_time = clock - current.arrival_time
            current.waiting_time = current.turnaround_time - current.burst_time
            current.response_time = response_times[current.pid]
            completed.append(current)
    
    # Calculate final performance metrics
    n = len(completed)
    avg_wait = sum(p.waiting_time for p in completed) / n
    avg_tat = sum(p.turnaround_time for p in completed) / n
    avg_resp = sum(p.response_time for p in completed) / n
    cpu_util = 100 * (clock - idle_time) / clock
    
    stats = {
        "avg_waiting": avg_wait,
        "avg_turnaround": avg_tat,
        "avg_response": avg_resp,
        "cpu_utilisation": cpu_util
    }
    
    return completed, schedule, stats