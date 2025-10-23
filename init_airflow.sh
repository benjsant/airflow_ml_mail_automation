#!/bin/bash
# dev_setup.sh - Install MailCatcher and initialize Airflow (dev standalone)

set -e  # exit on first error

# -----------------------
# Install MailCatcher
# -----------------------
sudo apt update
sudo apt install -y ruby ruby-dev build-essential libsqlite3-dev graphviz
sudo gem install mailcatcher

# Run MailCatcher in background
mailcatcher &
echo "📬 MailCatcher running on http://localhost:1080"

# -----------------------
# Setup Airflow
# -----------------------
# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set AIRFLOW_HOME
export AIRFLOW_HOME=$(pwd)/airflow

# Initialize Airflow database
airflow db init

# Import Airflow variables if file exists
if [ -f "dags/data/variables.json" ]; then
    airflow variables import dags/data/variables.json
    echo "✅ Airflow variables imported"
else
    echo "⚠️ variables.json not found, skipping import"
fi

echo "✅ Airflow and MailCatcher initialization complete."
