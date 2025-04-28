# First-Come, First-Served (FCFS) Scheduling Algorithm
from typing import List, Tuple, Dict
from process import Process

def fcfs_schedule(process_list: List[Process]) -> Tuple[List[Process], List[dict], Dict[str, float]]:
    """
    First-Come-First-Served scheduler.
    Returns:
        completed (List[Process]),
        schedule (List[dict]): each entry has pid, start, finish, turnaround
        stats (dict): avg_waiting, avg_turnaround, avg_response, cpu_utilisation
    """
    procs = sorted(process_list, key=lambda p: p.arrival_time)
    schedule = []
    completed = []
    idle_time = 0
    first_response: Dict[str, float] = {}

    clock = procs[0].arrival_time if procs else 0

    for proc in procs:
        start = max(clock, proc.arrival_time)
        # account for idle gap
        if start > clock:
            idle_time += start - clock
        # record response time
        first_response[proc.pid] = start - proc.arrival_time

        finish = start + proc.burst_time
        proc.turnaround_time = finish - proc.arrival_time
        proc.waiting_time = proc.turnaround_time - proc.burst_time
        proc.completion_time = finish

        schedule.append({
            'pid':        proc.pid,
            'start':      start,
            'finish':     finish,
        })
        completed.append(proc)
        clock = finish

    # compute statistics
    n = len(completed)
    avg_wait = sum(p.waiting_time for p in completed) / n if n else 0
    avg_tat = sum(p.turnaround_time for p in completed) / n if n else 0
    avg_resp = sum(first_response[p.pid] for p in completed) / n if n else 0
    cpu_util = 100 * (clock - idle_time) / clock if clock else 0

    stats = {
        "avg_waiting":     avg_wait,
        "avg_turnaround":  avg_tat,
        "avg_response":    avg_resp,
        "cpu_utilisation": cpu_util
    }

    return completed, schedule, stats


