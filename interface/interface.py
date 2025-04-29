# ───────── interface/interface.py ─────────
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session
import importlib, json, pathlib, sys, os

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

if __name__ == "__main__":
    app.run(debug=True)