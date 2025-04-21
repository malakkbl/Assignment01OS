# Process class definition

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid 
        self.arrival_time = arrival_time
        self.burst_time = burst_time  
        self.remaining_time = burst_time  
        self.turnaround_time = 0  
        self.priority = 0  # default is 0

    def __str__(self):
        return f"Process ID: {self.pid}, Arrival Time: {self.arrival_time}, Burst Time: {self.burst_time}, Remaining Time: {self.remaining_time}, Turnaround Time: {self.turnaround_time}, Priority: {self.priority}"
    
    
    