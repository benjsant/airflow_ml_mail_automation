#!/bin/bash
# run_airflow.sh - Run Airflow standalone (dev mode)

set -e  # exit on first error

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️ Virtual environment not found. Run init_airflow.sh first."
    exit 1
fi

# Set Airflow home directory
export AIRFLOW_HOME=$(pwd)/airflow
echo "📂 AIRFLOW_HOME set to $AIRFLOW_HOME"

# Run Airflow standalone
echo "🚀 Starting Airflow standalone..."
airflow standalone
