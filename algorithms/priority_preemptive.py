# priority_preemptive_simple.py

from process import Process

def priority_preemptive_schedule(process_list):
    """
    Preemptive priority scheduling (lower number = higher priority).
    If a newly arrived process has higher priority, it preempts the running one.
    Returns a list of dicts with keys:
      - 'pid'       : process ID
      - 'start'     : segment start time
      - 'finish'    : segment end time
      - 'turnaround': total turnaround time for completed segments, None for preempted segments
    Also sets each Process.turnaround_time when it fully completes.
    """
    # 1) Sort all processes by arrival time so we can pop the earliest
    arrival = sorted(process_list, key=lambda p: p.arrival_time)

    # 2) ready: map from priority -> list of waiting processes (FIFO per priority)
    ready = {}

    # 3) schedule: will collect all execution segments
    schedule = []

    # 4) Initialize clock to first arrival (or 0 if no processes)
    current_time = arrival[0].arrival_time if arrival else 0

    # 5) Track the currently running process and when it began its current segment
    current = None
    last_start = None

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

            # if there's a running process and the newcomer outranks it...
            if current and p.priority < current.priority:
                # record the segment up to preemption, with no turnaround
                schedule.append({
                    'pid':       current.pid,
                    'start':     last_start,
                    'finish':    current_time,
                    'turnaround': None
                })
                # put the interrupted process back onto the front of its ready list
                ready.setdefault(current.priority, []).insert(0, current)
                current = None

        # 6b) If CPU is free and someone is ready, dispatch the highest-priority process
        if not current and ready:
            # pick the lowest numeric key (= highest priority)
            prio = min(ready.keys())
            current = ready[prio].pop(0)  # FIFO within same priority
            if not ready[prio]:
                del ready[prio]
            # mark when this new segment starts
            last_start = current_time

        # 6c) If still idle, advance clock to next arrival
        if not current:
            if arrival:
                current_time = arrival[0].arrival_time
            continue

        # 6d) Decide next event: arrival or current finishing
        next_arrival = arrival[0].arrival_time if arrival else float('inf')
        finish_time  = current_time + current.remaining_time

        if next_arrival < finish_time:
            # will be preempted at next_arrival
            run_dur = next_arrival - current_time
            current.remaining_time -= run_dur
            current_time = next_arrival
        else:
            # run current to completion
            current_time = finish_time
            # record the final segment with actual turnaround
            turnaround = current_time - current.arrival_time
            schedule.append({
                'pid':        current.pid,
                'start':      last_start,
                'finish':     current_time,
                'turnaround': turnaround
            })
            # update the Process object’s turnaround_time
            current.turnaround_time = turnaround
            current = None

    return schedule


# ───────── Example Usage ─────────
if __name__ == '__main__':
    # define some processes: pid, arrival_time, burst_time, priority
    p1 = Process('A', arrival_time=0, burst_time=8, priority=2)
    p2 = Process('B', arrival_time=1, burst_time=4, priority=1)
    p3 = Process('C', arrival_time=12, burst_time=9, priority=3)
    p4 = Process('D', arrival_time=14, burst_time=5, priority=2)

    procs = [p1, p2, p3, p4]
    result = priority_preemptive_schedule(procs)

    # print all execution segments
    for seg in result:
        print(f"{seg['pid']} → {seg['start']} to {seg['finish']} (TAT={seg['turnaround']})")
