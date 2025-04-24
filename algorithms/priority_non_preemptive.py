"""# priority_commented.py

from collections import deque  # collections.deque: double-ended queue for efficient pops on both ends
from typing import List         # typing.List: for type annotations of list of Process objects
from process import Process      # import the Process class definition
from utility_functions import (
    sort_by_arrival,        # helper: returns a list of processes sorted by arrival_time
    init_current_time,      # helper: initializes clock to earliest arrival or 0
    run_to_completion,      # helper: simulates running a process and sets turnaround_time
    pick_highest_priority,  # helper: picks the highest priority key from a dict
    fast_forward            # helper: advances time to next arrival if CPU is idle
)

def priority_schedule(process_list: List[Process]):
    
    Non-preemptive priority scheduler.
    Uses a dict: priority → deque of Process objects, each deque ordered by arrival_time.

    Returns:
        schedule (List[Dict]): list of dicts containing pid, start, finish, and turnaround times.
    
    # 1) Create buckets: group processes by their priority level
    #    sort_by_arrival ensures each bucket's processes are in ascending order of arrival_time
    ready: dict[int, deque[Process]] = {}  # mapping from priority to deque of processes
    for proc in sort_by_arrival(process_list):
        # setdefault: if proc.priority key is absent, initialize with an empty deque
        # then append the process to that priority's deque
        ready.setdefault(proc.priority, deque()).append(proc)

    # Initialize the final schedule list (to collect execution records)
    schedule = []
    # 2) Bootstrap the simulation clock
    #    init_current_time returns the smallest arrival_time among all processes or 0 if list is empty
    current_time = init_current_time(process_list)

    # 3) Main loop: continue until all processes have been scheduled and completed
    while ready:
        # a) Determine which priorities have at least one process that has already arrived
        available = [
            prio for prio, q in ready.items()
            if q and q[0].arrival_time <= current_time  # the first process in deque is the earliest arrival
        ]

        if not available:
            # If no process is ready at current_time,
            # collect the next arrival times from all non-empty deques
            next_arrivals = [q[0].arrival_time for q in ready.values() if q]
            # fast_forward jumps current_time to the earliest of those arrivals
            current_time = fast_forward(current_time, next_arrivals)
            # restart loop to re-evaluate available processes
            continue

        # b) From the available priorities, pick the highest one to schedule next
        #    pick_highest_priority simply returns max(available)
        prio = pick_highest_priority({p: ready[p] for p in available})
        queue = ready[prio]            # the deque for that priority level
        proc = queue.popleft()         # remove the first (earliest-arrived) process
        if not queue:
            # If that priority's deque is now empty, remove the key from the dict
            del ready[prio]

        # c) Run the selected process to completion
        #    run_to_completion returns the (start, finish) times and sets proc.turnaround_time
        start, finish = run_to_completion(proc, current_time)
        # record the execution details in the schedule
        schedule.append({
            'pid':        proc.pid,            # unique identifier of the process
            'start':      start,               # time when execution began
            'finish':     finish,              # time when execution completed
            'turnaround': proc.turnaround_time # total time from arrival to completion
        })
        # advance the simulation clock to the process's finish time
        current_time = finish

    # return the completed schedule for further analysis or display
    return schedule


# ─────── Example Usage ───────
if __name__ == "__main__":
    # Define a few processes to demonstrate edge cases:
    #  - A and B arrive at the same time but different priorities
    #  - C has zero burst time
    #  - There's an idle gap before D arrives
    procs = [
        Process('A', arrival_time=2,  burst_time=5, priority=1),  # low priority
        Process('B', arrival_time=2,  burst_time=3, priority=2),  # higher priority
        Process('C', arrival_time=4,  burst_time=0, priority=5),  # zero-length job
        Process('D', arrival_time=10, burst_time=2, priority=2),  # arrives after idle
    ]
    # Run the scheduler and print each process's timeline
    for entry in priority_schedule(procs):
        print(f"{entry['pid']} → {entry['start']}–{entry['finish']} (TAT={entry['turnaround']})")
"""
# priority.py

from typing import List
from process import Process
from algorithms.utility_functions import (
    sort_by_arrival,      # helper: returns processes sorted by arrival_time
    init_current_time,    # helper: picks earliest arrival or returns 0
    run_to_completion,    # helper: computes start, finish, and turnaround_time
    fast_forward          # helper: jumps time to next arrival when idle
)


def priority_schedule(process_list: List[Process]):
    """
    Non-preemptive priority scheduler where LOWER numeric values indicate HIGHER scheduling priority.
    Uses a dict: priority -> list of Process objects in arrival order.

    Returns:
        schedule (List[dict]): each entry has pid, start, finish, turnaround.
    """
    # 1) Sort all processes by arrival time to handle arrivals chronologically
    arrival = sort_by_arrival(process_list)

    # 2) Bucket processes by priority, preserving arrival order within each list
    ready: dict[int, List[Process]] = {}
    for proc in arrival:
        if proc.priority in ready:
            ready[proc.priority].append(proc)
        else:
            ready[proc.priority] = [proc]

    # 3) Initialize schedule and simulation clock
    schedule = []
    current_time = init_current_time(arrival)

    # 4) Continue scheduling until no processes remain
    while ready:
        # a) Identify priority levels that have a process ready at current_time
        available = [
            prio for prio, lst in ready.items()
            if lst and lst[0].arrival_time <= current_time
        ]

        # b) If none are ready, jump to the next earliest arrival across all priorities
        if not available:
            next_arrivals = [lst[0].arrival_time for lst in ready.values() if lst]
            current_time = fast_forward(current_time, next_arrivals)
            continue

        # c) Select the highest scheduling priority: the LOWEST numeric 'priority' value
        prio_to_run = min(available)

        # d) Remove the chosen process from its priority bucket (FIFO within same priority)
        proc = ready[prio_to_run].pop(0)
        if not ready[prio_to_run]:
            del ready[prio_to_run]  # clean up empty buckets

        # e) Execute the process to completion
        start, finish = run_to_completion(proc, current_time)

        # f) Record its execution details
        schedule.append({
            'pid':        proc.pid,            # process identifier
            'start':      start,               # time execution begins
            'finish':     finish,              # time execution ends
            'turnaround': proc.turnaround_time # total time from arrival to completion
        })

        # g) Advance the clock to when this process finished
        current_time = finish

    return schedule


# Example usage
if __name__ == '__main__':
    # Define test processes to illustrate behavior:
    # - simultaneous arrivals with different numeric priorities
    # - a zero-length burst job
    # - an idle gap before the last process arrives
    p1 = Process('A', arrival_time=2,  burst_time=5, priority=1)  # higher scheduling priority than p2
    p2 = Process('B', arrival_time=0,  burst_time=3, priority=2)
    p3 = Process('C', arrival_time=4,  burst_time=0, priority=5)
    p4 = Process('D', arrival_time=10, burst_time=2, priority=2)

    procs = [p1, p2, p3, p4]
    result = priority_schedule(procs)
    for entry in result:
        print(f"{entry['pid']} → {entry['start']}–{entry['finish']} (TAT={entry['turnaround']})")
