# File: Flask_API.py
from __future__ import annotations

import os
import time
import requests
from flask import Flask, redirect, render_template

# ---------- Config ----------
WEBSERVER = os.getenv("AIRFLOW_WEBSERVER", "http://localhost:8080")
AF_USER = os.getenv("AIRFLOW_USERNAME", "airflow")
AF_PASS = os.getenv("AIRFLOW_PASSWORD", "airflow25")
TARGET_DAG_ID = os.getenv("TARGET_DAG_ID", "Airflow_Lab2")

# ---------- Flask app ----------
app = Flask(__name__, template_folder="templates")

def get_latest_run_info():
    """Query Airflow API to get the latest DAG run status."""
    url = f"{WEBSERVER}/api/v2/dags/{TARGET_DAG_ID}/dagRuns?order_by=-logical_date&limit=1"
    try:
        r = requests.get(url, auth=(AF_USER, AF_PASS), timeout=5)
        r.raise_for_status()
    except Exception as e:
        return False, {"note": f"API call failed: {e}"}

    runs = r.json().get("dag_runs", [])
    if not runs:
        return False, {"note": "No DAG runs found yet."}

    run = runs[0]
    state = run.get("state")
    info = {
        "state": state,
        "run_id": run.get("dag_run_id"),
        "logical_date": run.get("logical_date"),
        "start_date": run.get("start_date"),
        "end_date": run.get("end_date"),
        "note": "",
    }
    return state == "success", info

# ---------- Routes ----------
@app.route("/")
def index():
    ok, _ = get_latest_run_info()
    return redirect("/success" if ok else "/failure")

@app.route("/success")
def success():
    _, info = get_latest_run_info()
    return render_template("success.html", **info)

@app.route("/failure")
def failure():
    _, info = get_latest_run_info()
    return render_template("failure.html", **info)

@app.route("/health")
def health():
    return "ok", 200

# ---------- Start Flask ----------
def start_flask_app():
    """Run Flask dev server and keep it alive indefinitely."""
    print("Starting Flask on 0.0.0.0:5555 ...", flush=True)
    app.run(host="0.0.0.0", port=5555, use_reloader=False)
    while True:
        time.sleep(60)

# ---------- CLI ----------
if __name__ == "__main__":
    start_flask_app()
