
# Priority Round Robin CPU Scheduling Algorithm

from typing import List, Dict, Tuple
from process import Process
from algorithms.utility_functions import sort_by_arrival, init_current_time

def priority_round_robin(process_list: List[Process], quantum: int = 4, context_switch: int = 0):
    """
    Priority-based Round Robin scheduler implementation.
    
    Args:
        process_list: List of Process objects to be scheduled
        quantum: Maximum time slice given to each process
        context_switch: Time overhead when switching between processes
    
    Returns:
        completed: List of Process objects with final metrics
        schedule: Timeline of execution records (pid, start, finish)
        stats: Performance metrics including averages and utilization
    """
    # Sort processes by arrival time for chronological processing
    arrival = sort_by_arrival(process_list)

    # Priority-based ready queues - maps priority levels to their processes
    ready: Dict[int, List[Process]] = {}

    # Track execution timeline and metrics
    schedule = []         # Records when each process runs
    completed = []        # Stores finished processes
    idle_time = 0        # Tracks CPU idle periods
    first_response = {}  # When each process first gets CPU

    # Initialize simulation clock to earliest process arrival
    current_time = init_current_time(arrival)

    # Track current process execution state
    current = None          # Currently executing process
    last_start = None      # When current slice began
    slice_end = None       # When current quantum expires

    # Main scheduling loop - continues while we have:
    # - Future arrivals
    # - Ready processes at any priority
    # - Currently running process
    while arrival or ready or current:

        # Process new arrivals and handle preemption
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            if p.priority in ready:
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]

            # Preempt current process if new arrival has higher priority
            if current and p.priority < current.priority:
                schedule.append({
                    'pid': current.pid,
                    'start': last_start,
                    'finish': current_time
                })
                current.remaining_time -= current_time - last_start
                # Return interrupted process to front of its queue
                if current.priority in ready:
                    ready[current.priority].insert(0, current)
                else:
                    ready[current.priority] = [current]
                current = None

        # Select next process if CPU is idle
        if not current and ready:
            prio = min(ready)  # Lowest number = highest priority
            current = ready[prio].pop(0)
            if not ready[prio]:
                del ready[prio]  # Clean up empty queues

            last_start = current_time
            # Record first response time for this process
            if current.pid not in first_response:
                first_response[current.pid] = current_time - current.arrival_time

            slice_end = current_time + min(quantum, current.remaining_time)

        # Handle CPU idle periods
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue

        # Determine next event (arrival vs quantum expiry)
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        next_tick = min(slice_end, next_arrival)
        run_time = next_tick - current_time
        
        # Execute process for this time segment
        current.remaining_time -= run_time
        current_time = next_tick

        # Handle quantum expiry with remaining work
        if current_time == slice_end and current.remaining_time > 0:
            schedule.append({
                'pid': current.pid,
                'start': last_start,
                'finish': current_time
            })
            # Re-queue the current process before handling new arrivals
            if current.priority in ready:
                ready[current.priority].append(current)
            else:
                ready[current.priority] = [current]
            current = None
            
            # Process any arrivals that occurred exactly at slice end
            while arrival and arrival[0].arrival_time <= current_time:
                p = arrival.pop(0)
                if p.priority in ready:
                    ready[p.priority].append(p)
                else:
                    ready[p.priority] = [p]
                    
            continue

        # Handle process completion
        if current.remaining_time == 0:
            turnaround = current_time - current.arrival_time
            schedule.append({
                'pid': current.pid,
                'start': last_start,
                'finish': current_time
            })
            current.completion_time = current_time
            current.turnaround_time = turnaround
            current.waiting_time = turnaround - current.burst_time
            completed.append(current)
            current = None

    # Calculate final performance metrics
    n = len(completed)
    avg_wait = sum(p.waiting_time for p in completed) / n
    avg_tat = sum(p.turnaround_time for p in completed) / n
    avg_resp = sum(first_response[p.pid] for p in completed) / n
    cpu_util = 100 * (current_time - idle_time) / current_time if current_time else 0

    stats = {
        'avg_waiting': avg_wait,
        'avg_turnaround': avg_tat,
        'avg_response': avg_resp,
        'cpu_utilisation': cpu_util
    }

    return completed, schedule, stats

    p2 = Process('B', arrival_time=1,  burst_time=4, priority=1)
    p3 = Process('C', arrival_time=12, burst_time=9, priority=3)
    p4 = Process('D', arrival_time=6,  burst_time=5, priority=1)

    completed, timeline, metrics = priority_round_robin(
        [p1, p2, p3, p4], quantum=4
    )

    for seg in timeline:
        print(f"{seg['pid']} : {seg['start']} → {seg['finish']}")

    print("\nMetrics:", metrics)