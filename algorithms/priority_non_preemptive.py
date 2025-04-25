
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
        schedule (List[dict]): each entry has pid, start, finish, turnaround.
    """
    # 1) Sort all processes by arrival time so we can pop the earliest
    arrival = sort_by_arrival(process_list)
    
    # 2) ready: map from priority -> list of waiting processes (FIFO per priority)
    ready = {}
    
    # 3) schedule: will collect all execution segments
    schedule = []
    
    # 4) Initialize clock to first arrival (or 0 if no processes)
    current_time = init_current_time(arrival)
    
    # 5) Track the currently running process
    current = None
    
    # 6) Loop until there are no arrivals left, no ready processes, and no running process
    while arrival or ready or current:
        # 6a) Enqueue any processes that have arrived by now
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            # add to its priority list, creating one if necessary
            if p.priority in ready:
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]
        
        # 6b) If CPU is free, dispatch the highest-priority process that has arrived
        if not current and ready:
            # Find priority levels with processes that have already arrived
            available = [
                prio for prio, lst in ready.items()
                if lst and lst[0].arrival_time <= current_time
            ]
            
            if available:
                # Pick the highest priority (lowest number)
                prio_to_run = min(available)
                # Get the first process in that priority level
                current = ready[prio_to_run].pop(0)
                if not ready[prio_to_run]:
                    del ready[prio_to_run]  # clean up empty buckets
        
        # 6c) If still idle, advance clock to next arrival
        if not current:
            if arrival:
                current_time = arrival[0].arrival_time
            continue
        
        # 6d) Run the current process to completion (non-preemptive)
        start = current_time
        finish = start + current.burst_time
        
        # Record the execution details
        turnaround = finish - current.arrival_time
        current.turnaround_time = turnaround
        schedule.append({
            'pid': current.pid,
            'start': start,
            'finish': finish,
            'turnaround': turnaround
        })
        
        # Advance the clock and clear the CPU
        current_time = finish
        current = None
    
    return schedule

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