
from typing import List, Tuple
from process import Process

def sjf(processes: List[Process]):
    # Make a copy to avoid modifying the original list
    processes = [p for p in processes]

    # Sort first by arrival time , then after by burst time
    processes.sort(key=lambda p: p.arrival_time)

    ready_q: List[Process] = []
    completed: List[Process] = []

    clock = 0
    idle_time = 0

    while processes or ready_q:
        # ───────────────────────────────────────────────────────────── ready-queue fill
        while processes and processes[0].arrival_time <= clock:
            ready_q.append(processes.pop(0))

        if not ready_q:          # CPU is idle → jump clock to next arrival
            next_arrival = processes[0].arrival_time
            idle_time += next_arrival - clock
            clock = next_arrival
            continue

        # ─────────────────────────────────────────────────────────── choose next job
        #  Smallest burst among ready-processes
        ready_q.sort(key=lambda p: p.burst_time)
        current = ready_q.pop(0)

        # ───────────────────────────────────────────────────────────── execute
        start = clock
        clock += current.burst_time              # run to completion
        current.completion_time  = clock
        current.waiting_time     = start  - current.arrival_time
        current.turnaround_time  = clock - current.arrival_time
        current.remaining_time   = 0

        completed.append(current)

    # ───────────────────────────────────────────────────────────────── metrics
    n = len(completed)
    avg_wait   = sum(p.waiting_time    for p in completed) / n
    avg_tat    = sum(p.turnaround_time for p in completed) / n
    cpu_util   = 100 * (clock - idle_time) / clock

    return completed, {
        'avg_waiting'    : avg_wait,
        'avg_turnaround' : avg_tat,
        'cpu_utilisation': cpu_util
    }
    

