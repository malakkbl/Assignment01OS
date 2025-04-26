# priority_non_preemptive.py

from typing import List
from process import Process
from algorithms.utility_functions import (
    sort_by_arrival,
    init_current_time
)

def priority_schedule(process_list: List[Process]):
    """
    Non-preemptive priority scheduler where LOWER numeric values indicate HIGHER scheduling priority.
    Restructured to match the preemptive scheduler's approach.
    
    Returns:
        completed (List[Process]), 
        schedule (List[dict]): each entry has pid, start, finish, turnaround,
        stats (dict): avg_waiting, avg_turnaround, avg_response, cpu_utilisation
    """
    # 1) Sort all processes by arrival time so we can pop the earliest
    arrival = sort_by_arrival(process_list)
    
    # 2) ready: map from priority -> list of waiting processes (FIFO per priority)
    ready = {}
    
    # 3) schedule: will collect all execution segments
    schedule = []
    completed      = []     # ← collect finished Process objects
    idle_time      = 0      # ← total CPU idle time
    first_response = {}     # ← record first CPU access per PID
    
    # 4) Initialize clock to first arrival (or 0 if no processes)
    current_time = init_current_time(arrival)
    
    # 5) Track the currently running process
    current = None
    
    # 6) Loop until there are no arrivals left, no ready processes, and no running process
    while arrival or ready or current:
        # 6a) Enqueue any processes that have arrived by now
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            if p.priority in ready:
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]
        
        # 6b) If CPU is free, dispatch the highest-priority process that has arrived
        if not current and ready:
            available = [
                prio for prio, lst in ready.items()
                if lst and lst[0].arrival_time <= current_time
            ]
            if available:
                prio_to_run = min(available)
                current = ready[prio_to_run].pop(0)
                if not ready[prio_to_run]:
                    del ready[prio_to_run]
                # record first response
                if current.pid not in first_response:
                    first_response[current.pid] = current_time - current.arrival_time
        
        # 6c) If still idle, advance clock to next arrival
        if not current:
            if arrival:
                idle_time     += arrival[0].arrival_time - current_time
                current_time   = arrival[0].arrival_time
            continue
        
        # 6d) Run the current process to completion (non-preemptive)
        start  = current_time
        finish = start + current.burst_time
        
        # Record the execution details
        turnaround = finish - current.arrival_time
        current.completion_time = finish
        current.turnaround_time = turnaround
        current.waiting_time    = turnaround - current.burst_time
        
        schedule.append({
            'pid':        current.pid,
            'start':      start,
            'finish':     finish,
            'turnaround': turnaround
        })
        completed.append(current)
        
        # Advance the clock and clear the CPU
        current_time = finish
        current = None
    
    # 7) Compute aggregate statistics
    n = len(completed)
    avg_wait = sum(p.waiting_time    for p in completed) / n
    avg_tat  = sum(p.turnaround_time for p in completed) / n
    avg_resp = sum(first_response[p.pid] for p in completed) / n
    cpu_util = 100 * (current_time - idle_time) / current_time if current_time else 0
    
    stats = {
        "avg_waiting"     : avg_wait,
        "avg_turnaround"  : avg_tat,
        "avg_response"    : avg_resp,
        "cpu_utilisation" : cpu_util
    }
    
    return completed, schedule, stats


"""# Example usage
if __name__ == '__main__':
    # Define test processes to illustrate behavior
    p1 = Process('A', arrival_time=2,  burst_time=5, priority=1)  # higher priority than p2
    p2 = Process('B', arrival_time=0,  burst_time=3, priority=2)
    p3 = Process('C', arrival_time=4,  burst_time=0, priority=5)
    p4 = Process('D', arrival_time=10, burst_time=2, priority=2)

    procs = [p1, p2, p3, p4]
    result = priority_schedule(procs)
    for entry in result:
        print(f"{entry['pid']} → {entry['start']}–{entry['finish']} (TAT={entry['turnaround']})")
"""