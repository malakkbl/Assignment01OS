# Main program to run the simulation
from process import Process
from algorithms.fcfs import fcfs_schedule
from algorithms.priority_non_preemptive import priority_schedule
from algorithms.priority_preemptive import priority_preemptive_schedule
from algorithms.sjf       import sjf               
from algorithms.round_robin  import round_robin        


# ---------------- MENU -----------------
def choose_algorithm():
    """Return (algo_name, algo_function) chosen by the user."""
    algos = {
    "1": ("FCFS",                       fcfs_schedule),
    "2": ("Priority (non-preemptive)",  priority_schedule),
    "3": ("Priority (preemptive)",      priority_preemptive_schedule),
    "4": ("Shortest-Job-First (SJF)",   sjf),         
    "5": ("Round-Robin",                round_robin), 
}

    while True:
        print("\nSelect the scheduling algorithm:")
        for k, (name, _) in algos.items():
            print(f"  {k}) {name}")
        choice = input("Your choice : ").strip()
        if choice in algos:
            return algos[choice]
        print("⚠️  Invalid option – try again.")


# ------------- DATA ENTRY --------------
def read_processes(need_priority: bool = False):
    """
    Interactively build a list of Process objects.
    PIDs are auto-generated as 1, 2, 3, … (no user input).
    """
    n = int(input("\nNumber of processes ➜ "))
    processes = []

    for i in range(1, n + 1):
        print(f"\nProcess #{i}  (PID will be {i})")
        arrival = int(input("  Arrival time: "))
        burst   = int(input("  Burst  time : "))

        if need_priority:
            # --- Priority with validation ---
            while True:
                prio = int(input("  Priority (lower value = higher priority) and it needs to be non-negative: "))
                if prio >= 0:
                    break
                print("⚠️  Negative priorities are reserved for kernel / "
                      "real-time system tasks. Please enter 0 or a positive "
                      "integer.")
            processes.append(Process(i, arrival, burst, prio))
        else:
            processes.append(Process(i, arrival, burst))

    return processes


# ------------- REPORTING ---------------
def print_schedule(tbl):
    """
    Pretty-print the schedule table.
    • If a segment's turnaround is None (it was pre-empted) we show "⟂".
    • For summary stats we treat those None values as 0, as requested.
    """
    print("\n────────── S C H E D U L E ──────────")
    print(f"{'PID':<6}{'Start':<8}{'Finish':<8}{'Turnaround'}")

    for row in tbl:
        tat_disp = "Preempted" if row['turnaround'] is None else str(row['turnaround'])
        print(f"{row['pid']:<6}{row['start']:<8}{row['finish']:<8}{tat_disp}")

        # ----- summary -----
    makespan = max(r['finish'] for r in tbl) if tbl else 0

    # collect final TATs (only rows that finished a process)
    tat_per_pid = {
        r['pid']: r['turnaround']
        for r in tbl
        if r['turnaround'] is not None
    }


# --------------- DRIVER ----------------
def main():
    algo_name, algo_fn = choose_algorithm()
    need_priority      = "Priority" in algo_name          # ask for priority only when needed
    processes          = read_processes(need_priority)
    if "Round-Robin" in algo_name:
        quantum = int(input("  Time quantum: "))
        list_processes , schedule_table , my_dict = algo_fn(processes, quantum)
    else:
        list_processes , schedule_table , my_dict  = algo_fn(processes)
    print(f"\nUsing {algo_name} algorithm")
    print_schedule(schedule_table)
    print("\nProcess statistics:")
    for proc in list_processes:
        print(f"  PID {proc.pid}: "
              f"Waiting time = {proc.waiting_time}, "
              f"Turnaround time = {proc.turnaround_time}, "
              f"Completion time = {proc.completion_time}")
    print("\nMetrics:")
    for key, value in my_dict.items():
        print(f"  {key.replace('_', ' ').title()}: {value:.2f}")


if __name__ == "__main__":
    main()