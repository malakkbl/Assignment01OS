# Priority Preemptive CPU Scheduling Algorithm

from process import Process

def priority_preemptive_schedule(process_list):
    """
    Preemptive priority scheduling (lower number = higher priority).
    
    Args:
        process_list: List of Process objects to be scheduled
        
    Returns
    -------
    completed : List[Process]
    schedule  : List[dict]  (pid, start, finish, turnaround per segment)
    stats     : dict        (avg_waiting, avg_turnaround, avg_response, cpu_utilisation)

    """
    # Sort processes by arrival time for chronological processing
    arrival = sorted(process_list, key=lambda p: p.arrival_time)

    # Map priority levels to their ready processes (FIFO within each priority)
    ready = {}

    # Track execution history and performance metrics
    schedule = []        # Records execution timeline
    completed = []       # Stores finished processes
    idle_time = 0       # Tracks CPU idle periods
    first_response = {} # Records when processes first get CPU

    current_time =  0

    # Track currently running process and its start time
    current = None      # Currently executing process
    last_start = None   # When current process began executing

    # Main scheduling loop - continues while we have:
    # - Processes yet to arrive (arrival)
    # - Processes in ready queues (ready)
    # - A process currently running (current)
    while arrival or ready or current:

        # Process all new arrivals at current time
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            if p.priority in ready:
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]

            # Check if new arrival should preempt current process
            if current and p.priority < current.priority:
                # Record execution segment of preempted process
                schedule.append({
                    'pid': current.pid,
                    'start': last_start,
                    'finish': current_time,
                    'turnaround': None  # None indicates preemption
                })
                # Return preempted process to front of its priority queue
                if current.priority in ready:
                    ready[current.priority].insert(0, current)
                else:
                    ready[current.priority] = [current]
                current = None

        # If CPU is idle, select highest priority ready process
        if not current and ready:
            prio = min(ready)  # Lowest number = highest priority
            current = ready[prio].pop(0)
            if not ready[prio]:
                del ready[prio]  # Clean up empty queues
            last_start = current_time
            # Track first time each process gets CPU for response time
            if current.pid not in first_response:
                first_response[current.pid] = last_start - current.arrival_time

        # Handle CPU idle periods by jumping to next arrival
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue

        # Determine next event: process arrival or completion
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        finish_time = current_time + current.remaining_time

        if next_arrival < finish_time:
            # Process runs until next arrival (partial execution)
            run_dur = next_arrival - current_time
            current.remaining_time -= run_dur
            current_time = next_arrival
        else:
            # Process runs to completion
            current_time = finish_time
            turnaround = current_time - current.arrival_time
            schedule.append({
                'pid': current.pid,
                'start': last_start,
                'finish': current_time,
            })
            # Update process completion metrics
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
        "avg_waiting": avg_wait,
        "avg_turnaround": avg_tat,
        "avg_response": avg_resp,
        "cpu_utilisation": cpu_util
    }

    return completed, schedule, stats


