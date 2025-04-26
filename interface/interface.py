# ───────── interface/interface.py ─────────
from flask import Flask, render_template, request
import importlib, json
import pathlib, sys

# make top-level imports (process, algorithms, main) work
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import main  # reuse choose_algorithm, read_processes helpers

app = Flask(__name__, template_folder="templates")

# ----- helpers -------------------------------------------------------------
ALGO_FUNCS = {
    "fcfs":                ("FCFS",                       main.fcfs_schedule,            False, False),
    "sjf":                 ("Shortest-Job-First",         importlib.import_module("algorithms.sjf").sjf, False, False),
    "priority_np":         ("Priority (non-preemptive)",  main.priority_schedule,        True,  False),
    "rr":                  ("Round-Robin",                importlib.import_module("algorithms.round_robin").round_robin, False, True),
    "priority_rr":         ("Priority + RR",             importlib.import_module("algorithms.priority_rr").priority_round_robin, True,  True),
    "priority_preemptive": ("Priority (preemptive)",      main.priority_preemptive_schedule,              True,  False),
}


# ----- routes --------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", algos=ALGO_FUNCS)


@app.route("/run", methods=["POST"])
def run():
    data       = request.form
    algo_key   = data["algorithm"]
    quantum    = int(data.get("quantum", 4))
    ctx_switch = int(data.get("ctx", 0))

    _, algo_fn, need_prio, need_q = ALGO_FUNCS[algo_key]

    # parse processes JSON hidden field
    plist_json = json.loads(data["proc_json"])
    Process = importlib.import_module("process").Process
    plist = [Process(**p) for p in plist_json]

    extra = {}
    if need_q:
        extra["quantum"] = quantum
        if "priority" in algo_key:
            extra["context_switch"] = ctx_switch

    completed, schedule, metrics = algo_fn(plist, **extra)
    return render_template("result.html",
                           schedule=schedule,
                           metrics=metrics,
                           algo_name=ALGO_FUNCS[algo_key][0])


if __name__ == "__main__":
    app.run(debug=True)
