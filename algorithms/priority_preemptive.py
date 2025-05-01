# priority_preemptive.py
from process import Process


def priority_preemptive_schedule(process_list):
    """
    Preemptive priority scheduling (lower number = higher priority).

    If a newly-arrived process has a *higher* priority (smaller number),
    it preempts the one that is currently running.

    Returns
    -------
    completed : List[Process]
    schedule  : List[dict]  (pid, start, finish, turnaround per segment)
    stats     : dict        (avg_waiting, avg_turnaround, avg_response, cpu_utilisation)

    The function also fills in completion_time, turnaround_time and waiting_time
    for every Process instance.
    """
    # 1)  future arrivals, sorted by arrival_time
    arrival = sorted(process_list, key=lambda p: p.arrival_time)

    # 2)  ready-queue:  {priority -> [Process, …]}   (FIFO for equal priority)
    ready = {}

    # 3)  bookkeeping containers
    schedule       = []
    completed      = []   # finished processes
    idle_time      = 0
    first_response = {}

    # 4)  start the clock
    current_time = arrival[0].arrival_time if arrival else 0

    # 5)  track the current process (if any) and when its slice began
    current     = None
    last_start  = None

    # 6)  main simulation loop
    while arrival or ready or current:

        # 6a) move any processes that arrive *now* into ready
        while arrival and arrival[0].arrival_time <= current_time:
            p = arrival.pop(0)
            if p.priority in ready:         # ← explicit insert (no setdefault)
                ready[p.priority].append(p)
            else:
                ready[p.priority] = [p]

            # preempt if newcomer outranks current
            if current and p.priority < current.priority:
                schedule.append({
                    'pid'      : current.pid,
                    'start'    : last_start,
                    'finish'   : current_time,
                    'turnaround': None
                })
                # put the pre-empted process back at the *front* of its queue
                if current.priority in ready:
                    ready[current.priority].insert(0, current)
                else:
                    ready[current.priority] = [current]
                current = None

        # 6b) dispatch if CPU is idle
        if not current and ready:
            prio    = min(ready)
            current = ready[prio].pop(0)
            if not ready[prio]:
                del ready[prio]
            last_start = current_time
            if current.pid not in first_response:
                first_response[current.pid] = last_start - current.arrival_time

        # 6c) CPU still idle? fast-forward to next arrival
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue

        # 6d) determine next event (arrival vs completion)
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        finish_time  = current_time + current.remaining_time

        if next_arrival < finish_time:
            # run only until the next arrival because 
            # we need to check if that arrival has a higher priority
            run_dur = next_arrival - current_time
            current.remaining_time -= run_dur
            current_time = next_arrival
        else:
            # current process finishes
            current_time = finish_time
            turnaround   = current_time - current.arrival_time
            schedule.append({
                'pid'       : current.pid,
                'start'     : last_start,
                'finish'    : current_time,
            })
            # update per-process stats
            current.completion_time = current_time
            current.turnaround_time = turnaround
            current.waiting_time    = turnaround - current.burst_time
            completed.append(current)
            current = None

    # 7) aggregate statistics
    n         = len(completed)
    avg_wait  = sum(p.waiting_time    for p in completed) / n
    avg_tat   = sum(p.turnaround_time for p in completed) / n
    avg_resp  = sum(first_response[p.pid] for p in completed) / n
    cpu_util  = 100 * (current_time - idle_time) / current_time if current_time else 0

    stats = {
        "avg_waiting"    : avg_wait,
        "avg_turnaround" : avg_tat,
        "avg_response"   : avg_resp,
        "cpu_utilisation": cpu_util
    }

    return completed, schedule, stats


