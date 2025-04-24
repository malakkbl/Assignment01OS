# algorithms/round_robin.py
from collections import deque
from typing import List, Tuple
from process import Process


def round_robin(processes: List[Process],
                quantum: int = 4,
                context_switch: int = 0
               ) -> Tuple[List[Process], dict]:

    # ----- prepare containers -------------------------------------------------
    processes = sorted(processes, key=lambda p: p.arrival_time)   # event list
    ready_q   : deque[Process] = deque()
    completed : List[Process]  = []

    clock          = 0
    idle_time      = 0
    first_response = {}        # pid → response time

    # ----- simulation loop ----------------------------------------------------
    while processes or ready_q:

        # bring newly-arrived jobs into ready_q
        while processes and processes[0].arrival_time <= clock:
            ready_q.append(processes.pop(0))

        if not ready_q:                   # CPU idle
            next_arrival = processes[0].arrival_time
            idle_time   += next_arrival - clock
            clock        = next_arrival
            continue

        # pick next job (head of queue)
        current = ready_q.popleft()

        # record first response if not already
        if current.pid not in first_response:
            first_response[current.pid] = clock - current.arrival_time

        # ----- execute for ≤ quantum -----------------------------------------
        run_time = min(quantum, current.remaining_time)
        clock   += run_time
        current.remaining_time -= run_time

        # add context-switch overhead **after** the slice, except if we finish
        if current.remaining_time > 0:
            clock += context_switch
        else:
            # completed
            current.completion_time = clock
            current.turnaround_time = clock - current.arrival_time
            current.waiting_time    = current.turnaround_time - current.burst_time
            completed.append(current)

        # push back if not finished
        if current.remaining_time > 0:
            # new arrivals may have appeared during the run-time
            while processes and processes[0].arrival_time <= clock:
                ready_q.append(processes.pop(0))
            ready_q.append(current)

    # ----- metrics -----------------------------------------------------------
    n         = len(completed)
    avg_wait  = sum(p.waiting_time    for p in completed) / n
    avg_tat   = sum(p.turnaround_time for p in completed) / n
    avg_resp  = sum(first_response[p.pid] for p in completed) / n
    cpu_util  = 100 * (clock - idle_time) / clock

    return completed, {
        "avg_waiting"     : avg_wait,
        "avg_turnaround"  : avg_tat,
        "avg_response"    : avg_resp,
        "cpu_utilisation" : cpu_util
    }
