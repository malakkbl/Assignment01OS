# ───────── interface/interface.py ─────────
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import importlib, json, pathlib, sys, os
import pandas as pd

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import main  # reuse helpers

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(16)            # for session

# --- algorithm map ----------------------------------------
from algorithms.sjf               import sjf
from algorithms.round_robin       import round_robin
from algorithms.priority_rr       import priority_round_robin
algos = {
    "fcfs"    : ("FCFS",                       main.fcfs_schedule,            False, False),
    "sjf"     : ("Shortest-Job-First",         sjf,                           False, False),
    "prio_np" : ("Priority (non-preemptive)",  main.priority_schedule,        True,  False),
    "rr"      : ("Round-Robin",                round_robin,                   False, True),
    "prio_rr" : ("Priority + Round-Robin",     priority_round_robin,          True,  True),
    "prio_p"  : ("Priority (preemptive)",      main.priority_preemptive_schedule, True, False),
}

# ---------------- routes ----------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect(url_for("config"))
    return render_template("welcome.html")

@app.route("/config", methods=["GET", "POST"])
def config():
    if "username" not in session:
        return redirect(url_for("welcome"))
    if request.method == "POST":
        session["payload"] = request.form.to_dict()
        return redirect(url_for("run"))
    return render_template("config.html",
                           algos=algos,
                           username=session["username"])

@app.route("/run")
def run():
    payload = session.pop("payload", None)
    if not payload:
        return redirect(url_for("config"))

    algo_key = payload["algorithm"]
    name, algo_fn, need_prio, need_q = algos[algo_key]

    # Build Process list
    plist_json = json.loads(payload["proc_json"])
    Process = importlib.import_module("process").Process
    plist = [Process(**p) for p in plist_json]

    extra = {}
    if need_q:
        extra["quantum"] = int(payload["quantum"])
        if "prio" in algo_key:
            extra["context_switch"] = int(payload.get("ctx", 0))

    completed, schedule, metrics = algo_fn(plist, **extra)
    
    # Serialize processes
    serialized_procs = [{
        'job': str(p.pid),
        'arrival_time': p.arrival_time,
        'burst_time': p.burst_time,
        'finish_time': p.completion_time,
        'turnaround_time': p.turnaround_time,
        'waiting_time': p.waiting_time,
        'pid': p.pid
    } for p in completed]

    # Process colors and mapping
    process_colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", 
        "#FFEEAD", "#FF9999", "#99CC99", "#FFCC99"
    ]
    
    # Create PID to color mapping
    pid_to_color = {}
    for idx, p in enumerate(completed):
        color_index = idx % len(process_colors)
        pid_to_color[p.pid] = process_colors[color_index]

    # Calculate averages
    total_turnaround = sum(p.turnaround_time for p in completed)
    total_waiting = sum(p.waiting_time for p in completed)
    num_procs = len(completed)
    metrics['avg_turnaround'] = total_turnaround / num_procs if num_procs > 0 else 0
    metrics['avg_waiting'] = total_waiting / num_procs if num_procs > 0 else 0

    return render_template("result.html",
        name=session.get("username", "User"),
        algo=name,
        schedule=schedule,
        metrics=metrics,
        procs=serialized_procs,
        total_time=max(p.completion_time for p in completed) if completed else 0,
        processColors=process_colors,
        pidToColor=pid_to_color
    )

@app.route('/upload_processes', methods=['POST'])
def upload_processes():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        if file.filename.endswith('.json'):
            processes = process_json_file(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            processes = process_excel_file(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        return jsonify({'processes': processes})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def process_json_file(file):
    try:
        data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of processes")
        
        processes = []
        for i, proc in enumerate(data, 1):
            pid = proc.get('pid', i)
            arrival_time = int(proc.get('arrival_time', 0))
            burst_time = int(proc.get('burst_time'))
            priority = int(proc.get('priority', 0))
            
            if burst_time <= 0:
                raise ValueError(f"Process {pid}: Burst time must be positive")
            if arrival_time < 0:
                raise ValueError(f"Process {pid}: Arrival time cannot be negative")
            
            processes.append({
                'pid': pid,
                'arrival_time': arrival_time,
                'burst_time': burst_time,
                'priority': priority
            })
        
        return processes
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def process_excel_file(file):
    try:
        df = pd.read_excel(file)
        required_columns = ['PID', 'Arrival Time', 'Burst Time']
        
        # Check for column names (case-insensitive)
        df.columns = df.columns.str.lower()
        column_mapping = {
            'pid': ['pid', 'process id', 'id'],
            'arrival_time': ['arrival time', 'arrival', 'at'],
            'burst_time': ['burst time', 'burst', 'bt'],
            'priority': ['priority', 'prio', 'pr']
        }
        
        # Map columns to standardized names
        for std_name, variations in column_mapping.items():
            for col in df.columns:
                if col in variations:
                    df = df.rename(columns={col: std_name})
                    break
        
        # Validate required columns
        missing_cols = [col for col in ['pid', 'arrival_time', 'burst_time'] 
                       if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Convert to list of dictionaries
        processes = []
        for i, row in df.iterrows():
            pid = int(row.get('pid', i + 1))
            arrival_time = int(row['arrival_time'])
            burst_time = int(row['burst_time'])
            priority = int(row.get('priority', 0))
            
            if burst_time <= 0:
                raise ValueError(f"Process {pid}: Burst time must be positive")
            if arrival_time < 0:
                raise ValueError(f"Process {pid}: Arrival time cannot be negative")
            
            processes.append({
                'pid': pid,
                'arrival_time': arrival_time,
                'burst_time': burst_time,
                'priority': priority
            })
        
        return processes
    except Exception as e:
        raise ValueError(f"Error processing Excel file: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)