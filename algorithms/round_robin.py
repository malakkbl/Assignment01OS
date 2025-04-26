from collections import deque
from typing import List, Tuple
from process import Process


def round_robin(processes: List[Process],
                quantum: int = 4
               ):

    # Sort the processes in chronological order of arrival time
    processes = sorted(processes, key=lambda p: p.arrival_time)
    ready_q   : deque[Process] = deque()
    completed : List[Process]  = []
    schedule  : List[dict]     = []   # NEW timeline list  (one entry per slice)

    clock          = 0
    idle_time      = 0
    first_response = {}        # The first time the process accesses the CPU 

    while processes or ready_q:
        # In each iteration : move newly arrived jobs into ready_q + pick one ready process

        while processes and processes[0].arrival_time <= clock:
            ready_q.append(processes.pop(0))

        if not ready_q:                   # CPU idle
            next_arrival = processes[0].arrival_time
            idle_time   += next_arrival - clock
            clock        = next_arrival # fast forward to next arrival
            continue

        # pick next job (head of queue)
        current = ready_q.popleft()

        # record first response the process actually reaches the CPU
        if current.pid not in first_response:
            first_response[current.pid] = clock - current.arrival_time

        run_time = min(quantum, current.remaining_time)
        start    = clock                                # NEW start time for slice
        clock   += run_time
        current.remaining_time -= run_time

        # ---------- NEW ---------- store this CPU slice in the schedule
        schedule.append({
            'pid':   current.pid,
            'start': start,
            'finish': clock     # end of this slice
        })

        if current.remaining_time > 0:
            # not completed 
            while processes and processes[0].arrival_time <= clock:
                ready_q.append(processes.pop(0))
            ready_q.append(current)
        else:
            # completed
            current.completion_time = clock
            current.turnaround_time = clock - current.arrival_time
            current.waiting_time    = current.turnaround_time - current.burst_time
            completed.append(current)
            

    # Compute average stats for all the algorithm
    n         = len(completed)
    avg_wait  = sum(p.waiting_time    for p in completed) / n
    avg_tat   = sum(p.turnaround_time for p in completed) / n
    avg_resp  = sum(first_response[p.pid] for p in completed) / n
    cpu_util  = 100 * (clock - idle_time) / clock

    return completed, schedule, {
        "avg_waiting"     : avg_wait,
        "avg_turnaround"  : avg_tat,
        "avg_response"    : avg_resp,
        "cpu_utilisation" : cpu_util
    }
