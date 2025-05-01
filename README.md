# CPU Scheduler Simulator

A comprehensive CPU scheduling simulator that implements multiple scheduling algorithms with both terminal and web interfaces.

## Project Structure

```
SourceCode/
├── algorithms/              # Scheduling algorithm implementations
│   ├── fcfs.py            # First-Come-First-Serve
│   ├── sjf.py             # Shortest Job First
│   ├── priority_non_preemptive.py
│   ├── priority_preemptive.py
│   ├── round_robin.py
│   └── priority_rr.py     # Priority Round Robin
├── documentation/          # Jupyter notebook documentation
│   ├── fcfs.ipynb
│   ├── sjf.ipynb
│   ├── priority_non_preemptive.ipynb
│   ├── priority_preemptive.ipynb
│   ├── round_robin.ipynb
│   └── priority_round_robin.ipynb
├── interface/             # Web interface components
│   ├── interface.py       # Flask application
│   └── templates/         # HTML templates
├── FileToUpload/         # Sample process data files
├── algorithm_comparison.py # Algorithm comparison utilities
├── main.py               # Terminal interface entry point
├── process.py            # Process class definition
└── requirements_installation.py  # Package installer
```

## Features

- Multiple scheduling algorithms:
  - First-Come-First-Serve (FCFS)
  - Shortest Job First (SJF)
  - Priority (Non-preemptive)
  - Priority (Preemptive)
  - Round Robin
  - Priority Round Robin

- Two interface options:
  1. Terminal interface with formatted tables
  2. Web interface with interactive visualizations

- Process input methods:
  - JSON file upload
  - Excel file upload
  - Manual process entry

- Performance metrics:
  - Average waiting time
  - Average turnaround time
  - CPU utilization
  - Context switches

## Setup Instructions

1. **Prerequisites**:
   - Python 3.9 or higher
   - pip (Python package installer)

2. **Installation**:
   ```bash
   # Clone or download the repository
   cd SourceCode
   python requirements_installation.py
   ```

3. **Running the Simulator**:

   A. Terminal Interface:
   ```bash
   python main.py
   ```
   
   B. Web Interface:
   ```bash
   python interface/interface run
   ```
   Then open http://127.0.0.1:5000 in your web browser

## Sample Data

Sample process files are provided in the `FileToUpload` directory:
- `test_processes.json`
- `test_processes.xlsx`

## Documentation

Detailed algorithm documentation is available in Jupyter notebooks under the `documentation` directory. To view:

```bash
jupyter notebook documentation/
```
