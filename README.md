# CPU Scheduler Simulator

A comprehensive CPU scheduling simulator that implements multiple scheduling algorithms with both terminal and web interfaces.

### Authors
- Labzae Kawtar
- Kably Malak

### Supervised by
- Pr. Iraqi Youssef
- Pr. Abderrafi ABDEDDINE

## Project Structure

```
Assignment01OS/
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
  - Waiting Time
  - Turnaround Time
  - Response Time
  - CPU Utilization

## Setup Instructions

1. **Prerequisites**:
   - Python 3.9 or higher
   - pip (Python package installer)
   - Git (for cloning the repository)

2. **Getting the Code**:
   ```bash
   # Clone the repository
   git clone https://github.com/malakkbl/Assignment01OS.git
   cd Assignment01OS
   ```

3. **Installing Dependencies**:
   ```bash
   # Run the installation script
   python requirements_installation.py
   ```
   This will install all required packages:
   - Core: flask, pandas, numpy
   - Visualization: plotly
   - File handling: openpyxl
   - Documentation: jupyter, ipykernel
   - Terminal UI: tabulate, colorama

4. **Running the Simulator**:

   A. Terminal Interface:
   ```bash
   python main.py
   ```
   Features:
   - Text-based interactive menu
   - Support for single algorithm or comparison mode
   - Process input via JSON/Excel files or manual entry
   - Formatted table output with colors

   B. Web Interface:
   ```bash
   python interface/interface run
   ```
   Then open http://127.0.0.1:5000 in your web browser
   Features:
   - Interactive web UI
   - Drag-and-drop file upload
   - Real-time process management
   - Interactive Gantt charts
   - Detailed performance metrics

5. **Sample Data**:
   - Use files in `FileToUpload/` directory:
     - `test_processes.json`: JSON format sample
     - `test_processes.xlsx`: Excel format sample
   - Or enter process data manually through either interface

6. **Documentation**:
   ```bash
   jupyter notebook documentation/
   ```
   Access detailed documentation for each algorithm:
   - Theory and implementation details
   - Step-by-step execution flow
   - Performance characteristics
