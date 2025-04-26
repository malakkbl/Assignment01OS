# ───────── interface/interface.py ─────────
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session
import importlib, json, pathlib, sys, os

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import main  # reuse helpers

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(16)            # for session

# --- algorithm map (same as before) ----------------------------------------
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
    if "username" not in session:                    # direct hit safeguard
        return redirect(url_for("welcome"))

    if request.method == "POST":
        session["payload"] = request.form.to_dict()  # store raw for /run
        return redirect(url_for("run"))
    return render_template("config.html", algos=algos)

@app.route("/run")
def run():
    payload = session.pop("payload", None)
    if not payload:
        return redirect(url_for("config"))

    algo_key   = payload["algorithm"]
    name, algo_fn, need_prio, need_q = algos[algo_key]

    # build Process list from hidden json
    plist_json = json.loads(payload["proc_json"])
    Process = importlib.import_module("process").Process
    plist = [Process(**p) for p in plist_json]

    extra = {}
    if need_q:
        extra["quantum"] = int(payload["quantum"])
        if "prio" in algo_key:
            extra["context_switch"] = int(payload.get("ctx", 0))

    completed, schedule, metrics = algo_fn(plist, **extra)
    return render_template("result.html",
                           name=session.get("username", "User"),
                           algo=name,
                           schedule=schedule,
                           metrics=metrics,
                           procs=completed)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
