# First-Come, First-Served (FCFS) Scheduling Algorithm
from process import Process

def fcfs_schedule(process_list):
    procs = sorted(process_list, key=lambda p: p.arrival_time)
    schedule = []
    current_time = procs[0].arrival_time if procs else 0

    for proc in procs:
        start = max(current_time, proc.arrival_time)
        finish = start + proc.burst_time
        proc.turnaround_time = finish - proc.arrival_time

        schedule.append({
            'pid':        proc.pid,
            'start':      start,
            'finish':     finish,
            'turnaround': proc.turnaround_time
        })
        current_time = finish

    return schedule

# ─────────── Example Usage ───────────

"""if __name__ == "__main__":
    # Tricky test case:
    # - CPU idle until t=3
    # - Two processes arriving at same time (B vs C)
    # - Zero-burst process (D)
    p1 = Process('A', arrival_time=0, burst_time=4)
    p2 = Process('B', arrival_time=0, burst_time=2)
    p3 = Process('C', arrival_time=0, burst_time=3)
    p4 = Process('D', arrival_time=0, burst_time=0)

    procs = [p1, p2, p3, p4]
    result = fcfs_schedule(procs)

    for entry in result:
        print(f"Process {entry['pid']} ran from t={entry['start']} "
              f"to t={entry['finish']} (TAT={entry['turnaround']})")
"""