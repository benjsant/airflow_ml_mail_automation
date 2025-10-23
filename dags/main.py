# File: dags/main.py
from __future__ import annotations
import pendulum
import requests
from airflow import DAG
from airflow.models import Variable
from airflow.utils.email import send_email_smtp
from airflow.providers.standard.operators.python import PythonOperator

from src.model_development import (
    load_data,
    data_preprocessing,
    separate_data_outputs,
    build_model,
    evaluate_model,
)

# ---------- Callbacks ----------
def on_success_callback(context):
    subject = f"DAG {context['dag'].dag_id} Succeeded!"
    html_content = f"""
    <h3>DAG Succeeded ✅</h3>
    <p>DAG: {context['dag'].dag_id}</p>
    <p>Run ID: {context['run_id']}</p>
    <p>Logical Date: {context['logical_date']}</p>
    """
    send_email_smtp(
        to=Variable.get("airflow_email_recipient", default_var="test@example.com"),
        subject=subject,
        html_content=html_content,
        mailhost="localhost",
        port=1025,
    )


def on_failure_callback(context):
    subject = f"DAG {context['dag'].dag_id} Failed!"
    html_content = f"""
    <h3>DAG Failed ❌</h3>
    <p>DAG: {context['dag'].dag_id}</p>
    <p>Run ID: {context['run_id']}</p>
    <p>Task: {context['task_instance'].task_id}</p>
    <p>Log URL: {context['task_instance'].log_url}</p>
    """
    send_email_smtp(
        to=Variable.get("airflow_email_recipient", default_var="test@example.com"),
        subject=subject,
        html_content=html_content,
        mailhost="localhost",
        port=1025,
    )


# ---------- Flask notification ----------
def notify_flask():
    """Notify the Flask API that the DAG has finished running."""
    flask_url = "http://localhost:5555/health"
    try:
        response = requests.get(flask_url, timeout=5)
        print(f"✅ Flask API responded with: {response.text}")
    except Exception as e:
        print(f"❌ Could not contact Flask API: {e}")


# ---------- Task to test failure ----------
def test_task_failure():
    """
    Task to force failure if Airflow Variable `force_failure` is set to "true".
    """
    force_fail = Variable.get("force_failure", default_var="false")
    if force_fail.lower() == "true":
        raise RuntimeError("💥 Forced failure for testing!")
    print("✅ Test task succeeded normally.")


# ---------- Default args ----------
default_args = {
    "start_date": pendulum.datetime(2024, 1, 1, tz="UTC"),
    "retries": 0,
}


# ---------- DAG ----------
dag = DAG(
    dag_id="Airflow_Lab2",
    default_args=default_args,
    description="Airflow-Lab2 ML DAG with Flask integration",
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    on_success_callback=on_success_callback,
    on_failure_callback=on_failure_callback,
)


# ---------- Tasks ----------
load_data_task = PythonOperator(
    task_id="load_data_task",
    python_callable=load_data,
    dag=dag,
)

data_preprocessing_task = PythonOperator(
    task_id="data_preprocessing_task",
    python_callable=data_preprocessing,
    op_args=[load_data_task.output],
    dag=dag,
)

separate_data_outputs_task = PythonOperator(
    task_id="separate_data_outputs_task",
    python_callable=separate_data_outputs,
    op_args=[data_preprocessing_task.output],
    dag=dag,
)

build_model_task = PythonOperator(
    task_id="build_model_task",
    python_callable=build_model,
    op_args=[separate_data_outputs_task.output, "model.sav"],
    dag=dag,
)

evaluate_model_task = PythonOperator(
    task_id="evaluate_model_task",
    python_callable=evaluate_model,
    op_args=[separate_data_outputs_task.output, "model.sav"],
    dag=dag,
)

# Task pour tester failure
test_failure_task = PythonOperator(
    task_id="test_failure_task",
    python_callable=test_task_failure,
    dag=dag,
)

notify_flask_task = PythonOperator(
    task_id="notify_flask_task",
    python_callable=notify_flask,
    dag=dag,
)

# ---------- Dependencies ----------
load_data_task >> data_preprocessing_task >> separate_data_outputs_task
separate_data_outputs_task >> build_model_task >> evaluate_model_task >> test_failure_task >> notify_flask_task
