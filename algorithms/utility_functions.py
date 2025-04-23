
from typing import List, Dict, Any
from collections import deque

def sort_by_arrival(process_list: List[Any]) -> List[Any]:
    """Return a new list of processes sorted by arrival_time."""
    return sorted(process_list, key=lambda p: p.arrival_time)

def init_current_time(process_list: List[Any]) -> int:
    """
    Bootstrap the clock to the earliest arrival, or 0 if empty.
    """
    if not process_list:
        return 0
    return min(p.arrival_time for p in process_list)

def run_to_completion(proc: Any, current_time: int) -> tuple[int, int]:
    """
    Simulate running `proc` non-preemptively from max(current_time, arrival).
    Sets proc.turnaround_time, and returns (start, finish).
    """
    start = max(current_time, proc.arrival_time)
    finish = start + proc.burst_time
    proc.turnaround_time = finish - proc.arrival_time
    return start, finish

def pick_highest_priority(ready: Dict[int, deque]) -> int:
    """
    Given a dict priority→deque, return the highest priority key.
    """
    return max(ready.keys())

def fast_forward(current_time: int, next_arrivals: List[int]) -> int:
    """
    If CPU is idle, jump current_time to the soonest arrival in next_arrivals.
    """
    return min(next_arrivals)
