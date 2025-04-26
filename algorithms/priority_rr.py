# algorithms/priority_rr.py
from collections import deque
from typing import List, Dict, Tuple
from process import Process


def priority_round_robin(processes: List[Process],
                         quantum: int = 4,
                         context_switch: int = 0
                        ) -> Tuple[List[Process], List[dict], Dict[str, float]]:
    """
    Multilevel-queue scheduler:
        • Lower numeric value  → higher priority
        • Among equal priorities →  classic Round-Robin with common quantum
        • Pre-emptive: arrival of *any* higher-priority job pre-empts the running one.
    Returns (completed, schedule, metrics)
    """

    # Chronological arrival list
    arrival = sorted(processes, key=lambda p: p.arrival_time)

    # One ready-queue (deque) per priority value
    ready: Dict[int, deque[Process]] = {}

    completed: List[Process] = []
    schedule : List[dict]    = []
    first_resp: Dict[str, int] = {}

    clock     = 0
    idle_time = 0

    current   = None      # running process
    slice_end = None      # when the current quantum expires

    # Main loop
    while arrival or ready or current:

        # ─── A. Move every process that has just arrived ────────────────────
        while arrival and arrival[0].arrival_time <= clock:
            p = arrival.pop(0)
            ready.setdefault(p.priority, deque()).append(p)

            # If a higher-priority job appears, pre-empt immediately
            if current and p.priority < current.priority:
                # record partial slice
                schedule.append({
                    'pid':   current.pid,
                    'start': current.last_start,
                    'finish': clock,
                    'turnaround': None
                })
                current.remaining_time -= clock - current.last_start
                # put the interrupted process at *head* of its queue
                ready.setdefault(current.priority, deque()).appendleft(current)
                current = None

        # ─── B. If CPU idle choose next ready process (highest priority) ────
        if not current and ready:
            prio      = min(ready.keys())          # smallest number wins
            current   = ready[prio].popleft()
            if not ready[prio]:
                del ready[prio]

            current.last_start = clock             # custom attr: slice start

            if current.pid not in first_resp:
                first_resp[current.pid] = clock - current.arrival_time

            slice_end = clock + min(quantum, current.remaining_time)

        # ─── C. If still idle, fast-forward to next arrival ─────────────────
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - clock
                clock      = arrival[0].arrival_time
            continue

        # ─── D. Decide the next “interesting” time instant ─────────────────
        next_arr  = arrival[0].arrival_time if arrival else float('inf')
        next_tick = min(slice_end, next_arr)       # either slice expires or arrival happens
        run_time  = next_tick - clock

        current.remaining_time -= run_time
        clock = next_tick

        # Case 1: slice expired (quantum used up) and process still alive
        if clock == slice_end and current.remaining_time > 0:
            schedule.append({
                'pid':    current.pid,
                'start':  current.last_start,
                'finish': clock,
                'turnaround': None
            })
            # context-switch overhead
            clock += context_switch
            # new arrivals may have shown up during the overhead
            while arrival and arrival[0].arrival_time <= clock:
                p = arrival.pop(0)
                ready.setdefault(p.priority, deque()).append(p)
            # push to tail of its own queue
            ready.setdefault(current.priority, deque()).append(current)
            current = None
            continue

        # Case 2: process finished (within or at end of slice)
        if current.remaining_time == 0:
            schedule.append({
                'pid':        current.pid,
                'start':      current.last_start,
                'finish':     clock,
                'turnaround': clock - current.arrival_time
            })
            current.completion_time = clock
            current.turnaround_time = clock - current.arrival_time
            current.waiting_time    = current.turnaround_time - current.burst_time
            completed.append(current)
            current = None
            # context-switch cost only if more work remains
            if ready or arrival:
                clock += context_switch

    # ─── E. metrics ─────────────────────────────────────────────────────────
    n = len(completed)
    avg_wait = sum(p.waiting_time    for p in completed) / n
    avg_tat  = sum(p.turnaround_time for p in completed) / n
    avg_resp = sum(first_resp[p.pid] for p in completed) / n
    cpu_util = 100 * (clock - idle_time) / clock

    return completed, schedule, {
        'avg_waiting'    : avg_wait,
        'avg_turnaround' : avg_tat,
        'avg_response'   : avg_resp,
        'cpu_utilisation': cpu_util
    }
