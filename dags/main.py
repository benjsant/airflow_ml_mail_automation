# File: main.py
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.models import Variable # New import for Airflow Variables
from airflow.utils.email import send_email_smtp # New import for sending emails

def on_success_callback(context):
    """
    Callback function for DAG success.
    """
    subject = f"Airflow DAG {context['dag'].dag_id} Succeeded!"
    html_content = f"""
    <h3>DAG Succeeded</h3>
    <p>DAG: {context['dag'].dag_id}</p>
    <p>Run ID: {context['run_id']}</p>
    <p>Logical Date: {context['logical_date']}</p>
    """
    send_email_smtp(to=Variable.get("airflow_email_recipient", default_var="rey.mhmmd@gmail.com"), subject=subject, html_content=html_content)

def on_failure_callback(context):
    """
    Callback function for DAG failure.
    """
    subject = f"Airflow DAG {context['dag'].dag_id} Failed!"
    html_content = f"""
    <h3>DAG Failed</h3>
    <p>DAG: {context['dag'].dag_id}</p>
    <p>Run ID: {context['run_id']}</p>
    <p>Logical Date: {context['logical_date']}</p>
    <p>Task: {context['task_instance'].task_id}</p>
    <p>Log URL: {context['task_instance'].log_url}</p>
    """
    send_email_smtp(to=Variable.get("airflow_email_recipient", default_var="rey.mhmmd@gmail.com"), subject=subject, html_content=html_content)

from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.task.trigger_rule import TriggerRule

from src.model_development import (
    load_data,
    data_preprocessing,
    separate_data_outputs,
    build_model,
    load_model,
    evaluate_model, # New import
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
    description="Airflow-Lab2 DAG Description",
    schedule="@daily",
    catchup=False,
    tags=["example"],
    owner_links={"Ramin Mohammadi": "https://github.com/raminmohammadi/MLOps/"},
    max_active_runs=1,
    on_success_callback=on_success_callback, # New: DAG success callback
    on_failure_callback=on_failure_callback, # New: DAG failure callback
)

# ---------- Tasks ----------
owner_task = BashOperator(
    task_id="task_using_linked_owner",
    bash_command="echo 1",
    owner="Ramin Mohammadi",
    dag=dag,
)



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

build_save_model_task = PythonOperator(
    task_id="build_save_model_task",
    python_callable=build_model,
    op_args=[separate_data_outputs_task.output, "model.sav"],
    dag=dag,
)

evaluate_model_task = PythonOperator(
    task_id="evaluate_model_task",
    python_callable=evaluate_model,
    op_args=[separate_data_outputs_task.output, "model.sav"], # Uses output from preprocessing and model filename
    dag=dag,
)

load_model_task = PythonOperator(
    task_id="load_model_task",
    python_callable=load_model,
    op_args=[separate_data_outputs_task.output, "model.sav"],
    dag=dag,
)

# Fire-and-forget trigger so this DAG can finish cleanly.
trigger_dag_task = TriggerDagRunOperator(
    task_id="my_trigger_task",
    trigger_dag_id="Airflow_Lab2_Flask",
    conf={"message": "Data from upstream DAG"},
    reset_dag_run=False,
    wait_for_completion=False,          # don't block
    trigger_rule=TriggerRule.ALL_DONE,  # still run even if something upstream fails
    dag=dag,
)

# ---------- Dependencies ----------
owner_task >> load_data_task >> data_preprocessing_task >> \
    separate_data_outputs_task >> build_save_model_task >> evaluate_model_task >> \
    load_model_task >> trigger_dag_task


