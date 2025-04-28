# priority_round_robin.py
from typing import List, Dict, Tuple
from process import Process
from algorithms.utility_functions import (
    sort_by_arrival,   # helper: returns processes sorted by arrival_time
    init_current_time  # helper: picks earliest arrival or returns 0
)

def priority_round_robin(
        process_list: List[Process],
        quantum: int = 4
    ) -> Tuple[List[Process], List[dict], dict]:
    """
    Multilevel-queue, pre-emptive, priority + round-robin scheduler.

      • Smaller priority value → higher priority
      • Within the same priority → classic Round-Robin with a common quantum
      • Any newly-arrived higher-priority process pre-empts the running one

    Returns
    -------
    completed : List[Process]
    schedule  : List[dict]   (pid, start, finish, turnaround per slice)
    stats     : dict         (avg_waiting, avg_turnaround, avg_response, cpu_utilisation)
    """

    # 1)  Future arrivals, sorted chronologically
    arrival = sort_by_arrival(process_list)

    # 2)  Ready-queue: {priority → [Process, …]}  FIFO for equal priority
    ready: Dict[int, List[Process]] = {}

    # 3)  Book-keeping containers
    schedule       = []
    completed      = []
    idle_time      = 0
    first_response = {}

    # 4)  Initialise the simulated clock
    current_time = init_current_time(arrival)

    # 5)  Track the currently running process
    current      = None          # type: Process | None
    last_start   = None          # slice start timestamp
    slice_end    = None          # when the current quantum expires

    # 6)  Main simulation loop
    while arrival or ready or current:

        # 6a)  Move every process that has arrived by now into ready
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            if p.priority in ready:
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]

            # Pre-empt if newcomer outranks the running process
            if current and p.priority < current.priority:
                schedule.append({
                    'pid'   : current.pid,
                    'start' : last_start,
                    'finish': current_time
                })
                current.remaining_time -= current_time - last_start
                # Put the interrupted job at the *head* of its own queue
                if current.priority in ready:
                    ready[current.priority].insert(0, current)
                else:
                    ready[current.priority] = [current]
                current = None

        # 6b)  Dispatch if CPU is idle
        if not current and ready:
            prio    = min(ready)                  # smallest number wins
            current = ready[prio].pop(0)
            if not ready[prio]:
                del ready[prio]

            last_start = current_time
            if current.pid not in first_response:
                first_response[current.pid] = current_time - current.arrival_time

            slice_end = current_time + min(quantum, current.remaining_time)

        # 6c)  CPU still idle?  Fast-forward to next arrival
        if not current:
            if arrival:
                idle_time  += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue

        # 6d)  Determine next event (arrival vs. slice end)
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        next_tick    = min(slice_end, next_arrival)
        run_time     = next_tick - current_time

        current.remaining_time -= run_time
        current_time            = next_tick

        # 6e)  Quantum expired but job not finished
        if current_time == slice_end and current.remaining_time > 0:
            schedule.append({
                'pid'   : current.pid,
                'start' : last_start,
                'finish': current_time
            })
            # Enqueue arrivals that landed exactly at this tick
            while arrival and arrival[0].arrival_time <= current_time:
                p = arrival.pop(0)
                if p.priority in ready:
                    ready[p.priority].append(p)
                else:
                    ready[p.priority] = [p]
            # Push job to tail of its own queue
            if current.priority in ready:
                ready[current.priority].append(current)
            else:
                ready[current.priority] = [current]
            current = None
            continue

        # 6f)  Job finished
        if current.remaining_time == 0:
            turnaround = current_time - current.arrival_time
            schedule.append({
                'pid'       : current.pid,
                'start'     : last_start,
                'finish'    : current_time
            })
            current.completion_time = current_time
            current.turnaround_time = turnaround
            current.waiting_time    = turnaround - current.burst_time
            completed.append(current)
            current = None

    # 7)  Aggregate statistics
    n         = len(completed)
    avg_wait  = sum(p.waiting_time    for p in completed) / n
    avg_tat   = sum(p.turnaround_time for p in completed) / n
    avg_resp  = sum(first_response[p.pid] for p in completed) / n
    cpu_util  = 100 * (current_time - idle_time) / current_time if current_time else 0

    stats = {
        'avg_waiting'    : avg_wait,
        'avg_turnaround' : avg_tat,
        'avg_response'   : avg_resp,
        'cpu_utilisation': cpu_util
    }

    return completed, schedule, stats


# ───────── Example usage ─────────
if __name__ == '__main__':
    p1 = Process('A', arrival_time=0,  burst_time=8, priority=2)
    p2 = Process('B', arrival_time=1,  burst_time=4, priority=1)
    p3 = Process('C', arrival_time=12, burst_time=9, priority=3)
    p4 = Process('D', arrival_time=6,  burst_time=5, priority=1)

    completed, timeline, metrics = priority_round_robin(
        [p1, p2, p3, p4], quantum=4
    )

    for seg in timeline:
        print(f"{seg['pid']} : {seg['start']} → {seg['finish']}")

    print("\nMetrics:", metrics)
