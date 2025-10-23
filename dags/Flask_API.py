# File: dags/Flask_API.py
from __future__ import annotations

import os
import time
import pendulum
import requests
from flask import Flask, redirect, render_template
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


# ---------- Config ----------
WEBSERVER = os.getenv("AIRFLOW_WEBSERVER", "http://localhost:8080")
AF_USER = os.getenv("AIRFLOW_USERNAME", "airflow")
AF_PASS = os.getenv("AIRFLOW_PASSWORD", "airflow25")
TARGET_DAG_ID = os.getenv("TARGET_DAG_ID", "Airflow_Lab2")


# ---------- Default args ----------
default_args = {
    "start_date": pendulum.datetime(2024, 1, 1, tz="UTC"),
    "retries": 0,
}


# ---------- Flask app ----------
app = Flask(__name__, template_folder="templates")


def get_latest_run_info():
    """
    Query Airflow REST API (v2) to fetch the most recent DAG run state.
    """
    url = f"{WEBSERVER}/api/v2/dags/{TARGET_DAG_ID}/dagRuns?order_by=-logical_date&limit=1"

    try:
        response = requests.get(url, auth=(AF_USER, AF_PASS), timeout=5)
    except Exception as e:
        return False, {"note": f"Error connecting to Airflow API: {e}"}

    if response.status_code != 200:
        snippet = response.text[:200].replace("\n", " ")
        return False, {"note": f"API returned {response.status_code}: {snippet}"}

    runs = response.json().get("dag_runs", [])
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


@app.route("/")
def index():
    """
    Redirect user to success or failure page depending on DAG state.
    """
    ok, _ = get_latest_run_info()
    return redirect("/success" if ok else "/failure")


@app.route("/success")
def success():
    ok, info = get_latest_run_info()
    return render_template("success.html", **info)


@app.route("/failure")
def failure():
    ok, info = get_latest_run_info()
    return render_template("failure.html", **info)


@app.route("/health")
def health():
    """
    Simple endpoint to confirm Flask API is alive.
    """
    return "ok", 200


def start_flask_app():
    """
    Start the Flask server (blocking) to display DAG run status.
    This function is executed by Airflow as a DAG task.
    """
    print("🚀 Starting Flask server on 0.0.0.0:5555 ...", flush=True)
    app.run(host="0.0.0.0", port=5555, use_reloader=False)
    # Keep the task alive forever
    while True:
        time.sleep(60)


# ---------- DAG ----------
flask_api_dag = DAG(
    dag_id="Airflow_Lab2_Flask",
    default_args=default_args,
    description="Flask API to visualize Airflow_Lab2 DAG status",
    schedule=None,  # Trigger manually after Airflow_Lab2
    catchup=False,
    is_paused_upon_creation=False,
    tags=["Flask_API"],
    max_active_runs=1,
)


start_flask_api = PythonOperator(
    task_id="start_flask_app",
    python_callable=start_flask_app,
    dag=flask_api_dag,
)

start_flask_api

if __name__ == "__main__":
    start_flask_app()
