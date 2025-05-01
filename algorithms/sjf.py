from typing import List, Tuple # backward compatibility + static clarity
from process import Process

def sjf(processes: List[Process]):
    # Simulates a non pre-emptive shortest-job-first CPU scheduler when supplied with a list of process objects. 
    """
    Non-pre-emptive Shortest Job First scheduler.
    Returns:
        completed  – list of Process objects with stats filled in
        schedule   – list of dicts {pid, start, finish}
        metrics    – dict with averages and CPU utilisation
    """

    # Chronological event list
    processes.sort(key=lambda p: p.arrival_time)

    ready_q: List[Process] = []  # Stores the processes that are ready to run
    completed: List[Process] = []  # Stores the processes that have completed
    schedule:  List[dict]    = []  # just to simulate a timeline for visualization purposes
    first_response = {}  # Track when each process first gets CPU time

    clock = 0  # The simulated time
    idle_time = 0  # Accumulates gaps when CPU is idle

    while processes or ready_q:
        # In each iteration : move newly arrived jobs into ready_q + pick one ready process
        
        while processes and processes[0].arrival_time <= clock:
            ready_q.append(processes.pop(0))

        if not ready_q:          # CPU is idle > we travel in time to the next arrival
            next_arrival = processes[0].arrival_time
            idle_time += next_arrival - clock
            clock = next_arrival
            continue

        #  Choose the next process to run from the ready queue
        ready_q.sort(key=lambda p: p.burst_time) # This is where the property of our algorithm appears
        current = ready_q.pop(0)
        
        #  Compute individual stats for the current process
        start = clock
        # Record first response time if not already recorded
        if current.pid not in first_response:
            first_response[current.pid] = start - current.arrival_time

        clock += current.burst_time  # Simulate the process running : run it to completion
        current.completion_time  = clock
        current.waiting_time     = start  - current.arrival_time
        current.turnaround_time  = clock - current.arrival_time
        current.remaining_time   = 0

        completed.append(current)

        # Update the schedule with the current process's stats
        schedule.append({
            'pid':        current.pid,
            'start':      start,
            'finish':     clock
        })

    # Compute average stats for all the algorithm
    n = len(completed)
    avg_wait   = sum(p.waiting_time    for p in completed) / n
    avg_tat    = sum(p.turnaround_time for p in completed) / n
    avg_resp   = sum(first_response[p.pid] for p in completed) / n
    cpu_util   = 100 * (clock - idle_time) / clock

    return completed, schedule, {
        'avg_waiting'    : avg_wait,
        'avg_turnaround' : avg_tat,
        'avg_response'   : avg_resp,
        'cpu_utilisation': cpu_util
    }
