# priority_preemptive.py
from process import Process
from algorithms.utility_functions import (
    sort_by_arrival,      # helper: returns processes sorted by arrival_time
    init_current_time,    # helper: picks earliest arrival or returns 0
)

def priority_preemptive_schedule(process_list):
    """
    Preemptive priority scheduling (lower number = higher priority).
    If a newly arrived process has higher priority, it preempts the running one.
    Returns:
        completed (List[Process]),
        schedule (List[dict]): one per slice, keys pid, start, finish, turnaround
        stats (dict): avg_waiting, avg_turnaround, avg_response, cpu_utilisation
    Also sets each Process.completion_time, turnaround_time & waiting_time on completion.
    """
    # 1) Sort all processes by arrival time so we can pop the earliest
    arrival = sort_by_arrival(process_list)

    # 2) ready: map from priority -> list of waiting processes (FIFO per priority)
    ready = {}

    # 3) schedule: will collect all execution segments
    schedule = []
    completed      = []     # ← finished processes
    idle_time      = 0      # ← total CPU idle time
    first_response = {}     # ← record first CPU access per PID

    # 4) Initialize clock to first arrival (or 0 if no processes)
    current_time = init_current_time(arrival)

    # 5) Track the currently running process and when its segment began
    current = None
    last_start = None

    # 6) Loop until no arrivals, no ready, no running
    while arrival or ready or current:
        # 6a) Enqueue any processes that have arrived at current_time
        while arrival and arrival[0].arrival_time == current_time:
            p = arrival.pop(0)
            ready.setdefault(p.priority, []).append(p)
            # preempt if newcomer outranks current
            if current and p.priority < current.priority:
                schedule.append({
                    'pid':       current.pid,
                    'start':     last_start,
                    'finish':    current_time,
                    'turnaround': None
                })
                ready.setdefault(current.priority, []).insert(0, current)
                current = None

        # 6b) Dispatch if CPU idle
        if not current and ready:
            prio = min(ready)
            current = ready[prio].pop(0)
            if not ready[prio]:
                del ready[prio]
            last_start = current_time
            # record first response time
            if current.pid not in first_response:
                first_response[current.pid] = last_start - current.arrival_time

        # 6c) If still idle, fast-forward to next arrival
        if not current:
            if arrival:
                idle_time += arrival[0].arrival_time - current_time
                current_time = arrival[0].arrival_time
            continue

        # 6d) Compute next event: arrival vs. completion
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        finish_time = current_time + current.remaining_time

        if next_arrival < finish_time:
            run_dur = next_arrival - current_time
            current.remaining_time -= run_dur
            current_time = next_arrival
        else:
            # finish current
            current_time = finish_time
            turnaround = current_time - current.arrival_time
            schedule.append({
                'pid':        current.pid,
                'start':      last_start,
                'finish':     current_time,
                'turnaround': turnaround
            })
            # update the Process object’s metrics
            current.completion_time = current_time
            current.turnaround_time = turnaround
            current.waiting_time = turnaround - current.burst_time
            completed.append(current)
            current = None

    # 7) Compute aggregate statistics
    n = len(completed)
    avg_wait = sum(p.waiting_time for p in completed) / n
    avg_tat = sum(p.turnaround_time for p in completed) / n
    avg_resp = sum(first_response[p.pid] for p in completed) / n
    cpu_util = 100 * (current_time - idle_time) / current_time if current_time else 0

    stats = {
        "avg_waiting":     avg_wait,
        "avg_turnaround":  avg_tat,
        "avg_response":    avg_resp,
        "cpu_utilisation": cpu_util
    }

    return completed, schedule, stats

# ───────── Example Usage ─────────
if __name__ == '__main__':
    # define some processes: pid, arrival_time, burst_time, priority
    p1 = Process('A', arrival_time=0, burst_time=8, priority=2)
    p2 = Process('B', arrival_time=1, burst_time=4, priority=1)
    p3 = Process('C', arrival_time=12, burst_time=9, priority=3)
    p4 = Process('D', arrival_time=6, burst_time=5, priority=1)

    procs = [p1, p2, p3, p4]
    completed, result, stats = priority_preemptive_schedule(procs)

    # print completion time for each process
    for proc in completed:
        print(f"PID {proc.pid}: completion_time = {proc.completion_time}, turnaround = {proc.turnaround_time}, waiting = {proc.waiting_time}")