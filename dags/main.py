# File: dags/airflow_lab2_dag.py
from __future__ import annotations
import pendulum
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
        to=Variable.get("airflow_email_recipient", default_var="your_email@example.com"),
        subject=subject,
        html_content=html_content,
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
        to=Variable.get("airflow_email_recipient", default_var="your_email@example.com"),
        subject=subject,
        html_content=html_content,
    )

# ---------- Default args ----------
default_args = {
    "start_date": pendulum.datetime(2024, 1, 1, tz="UTC"),
    "retries": 0,
}

# ---------- DAG ----------
dag = DAG(
    dag_id="Airflow_Lab2",
    default_args=default_args,
    description="Airflow-Lab2 ML DAG",
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

# ---------- Dependencies ----------
load_data_task >> data_preprocessing_task >> separate_data_outputs_task
separate_data_outputs_task >> build_model_task >> evaluate_model_task
