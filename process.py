class Process:
    def __init__(self, pid, arrival_time, burst_time,priority=0):
        # Unique process identifier
        self.pid = pid  
        
        # Time when the process arrives and is ready to be scheduled
        self.arrival_time = arrival_time  
        self.completion_time = 0
        # Priority level (unused in FCFS; useful for priority scheduling later)
        self.priority = priority 
        
        # Total CPU time required for the process to complete
        self.burst_time = burst_time  
        
        # Remaining CPU time (for preemptive schedulers; here starts equal to burst_time)
        self.remaining_time = burst_time  
        
        # Turnaround time = completion_time - arrival_time (compute after the process finishes)
        self.turnaround_time = 0  

        self.waiting_time = 0

    def __str__(self):
        return (f"Process ID: {self.pid}, "
                f"Arrival: {self.arrival_time}, "
                f"Burst: {self.burst_time}, "
                f"Remaining: {self.remaining_time}, "
                f"Turnaround: {self.turnaround_time}, "
                f"Priority: {self.priority},"
                f"Completion: {self.completion_time} ,"
                f"Waiting: {self.waiting_time}")
