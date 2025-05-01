# Priority Round-Robin CPU Scheduling  (minimal patch – no mid-slice pre-emption)
# ------------------------------------------------------------------------------
#  Only two small changes to your original logic:
#  1)  We **removed** the block that yanked the CPU away when a higher-priority
#      job arrived mid-quantum.  The running process now keeps its slice.
#  2)  Added a clarifying docstring line and (optional) context-switch delay
#      right after a slice ends.  Everything else is exactly the same layout.

from typing import List, Dict, Tuple
from process import Process


def priority_round_robin(
    process_list: List[Process],
    quantum: int = 4,
    context_switch: int = 0
) -> Tuple[List[Process], List[dict], Dict[str, float]]:
    """
    Priority-based Round Robin scheduler.
    ✦ A running job is **not pre-empted inside its current quantum** when higher
      priority work shows up; it finishes that slice first.
    """

    # -------------------------------------------------------------------------
    #  Setup
    # -------------------------------------------------------------------------
    arrival = sorted(process_list, key=lambda p: p.arrival_time)
    ready: Dict[int, List[Process]] = {}

    schedule   = []
    completed  = []
    idle_time  = 0
    first_resp = {}

    current_time = arrival[0].arrival_time if arrival else 0
    current      = None
    last_start   = None
    slice_end    = None

    # -------------------------------------------------------------------------
    #  Main loop
    # -------------------------------------------------------------------------
    while arrival or ready or current:

        # Admit any processes that have arrived.
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            ready.setdefault(p.priority, []).append(p)
            # ---------------  PATCH: no more mid-slice pre-emption ---------------
            # (The four lines that used to interrupt 'current' were removed.)
            # ---------------------------------------------------------------------

        # If CPU is idle, pick next ready process.
        if not current and ready:
            prio   = min(ready)                # lower value ⇒ higher priority
            current = ready[prio].pop(0)
            if not ready[prio]:
                del ready[prio]

            last_start = current_time
            if current.pid not in first_resp:
                first_resp[current.pid] = current_time - current.arrival_time
            slice_end = current_time + min(quantum, current.remaining_time)

        # Nothing ready? Fast-forward to next arrival.
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue

        # Run until either slice finishes or a new job arrives.
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        next_tick    = min(slice_end, next_arrival)
        run_time     = next_tick - current_time

        current.remaining_time -= run_time
        current_time            = next_tick

        # Admit arrivals that happened exactly *now* (edge of slice).
        while arrival and arrival[0].arrival_time == current_time:
            p = arrival.pop(0)
            ready.setdefault(p.priority, []).append(p)

        # Slice finished?
        if current_time == slice_end:
            schedule.append({'pid': current.pid, 'start': last_start, 'finish': current_time})

            if current.remaining_time == 0:              # job done
                turnaround = current_time - current.arrival_time
                current.completion_time  = current_time
                current.turnaround_time  = turnaround
                current.waiting_time     = turnaround - current.burst_time
                completed.append(current)
            else:                                        # needs another slice
                ready.setdefault(current.priority, []).append(current)

            current   = None
            slice_end = None
            last_start = None

            # Optional context-switch overhead
            if context_switch:
                current_time += context_switch

    # -------------------------------------------------------------------------
    #  Aggregate metrics
    # -------------------------------------------------------------------------
    n = len(completed) or 1
    avg_wait = sum(p.waiting_time     for p in completed) / n
    avg_tat  = sum(p.turnaround_time  for p in completed) / n
    avg_resp = sum(first_resp[p.pid]  for p in completed) / n
    cpu_util = 100 * (current_time - idle_time) / current_time if current_time else 0

    stats = {
        'avg_waiting'    : avg_wait,
        'avg_turnaround' : avg_tat,
        'avg_response'   : avg_resp,
        'cpu_utilisation': cpu_util
    }

    return completed, schedule, stats
