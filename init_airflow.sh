#!/bin/bash
# init_airflow.sh - Install MailCatcher and initialize Airflow (dev standalone)
# Description:
#   This script installs and configures a local Apache Airflow environment in standalone mode.
#   It also installs MailCatcher to test email notifications locally via SMTP (port 1025).

set -e  # Exit immediately on error

echo "🚀 Starting Airflow + MailCatcher initialization..."

# -----------------------
# Install system dependencies and MailCatcher
# -----------------------
sudo apt update
sudo apt install -y ruby ruby-dev build-essential libsqlite3-dev graphviz python3-venv crudini
sudo gem install mailcatcher

# Run MailCatcher in background (port 1080 for UI, 1025 for SMTP)
mailcatcher &
echo "📬 MailCatcher running on http://localhost:1080"

# -----------------------
# Setup Python virtual environment
# -----------------------
if [ ! -d ".venv" ]; then
    echo "🧱 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# -----------------------
# Setup Airflow directories and environment variables
# -----------------------
export AIRFLOW_HOME="$(pwd)/airflow"
mkdir -p "$AIRFLOW_HOME"
mkdir -p "$AIRFLOW_HOME/logs"

echo "📁 AIRFLOW_HOME set to: $AIRFLOW_HOME"

# -----------------------
# Initialize Airflow (DB + config)
# -----------------------
if [ ! -f "$AIRFLOW_HOME/airflow.cfg" ]; then
    echo "⚙️ Initializing Airflow to generate configuration..."
    airflow db migrate
else
    echo "ℹ️ airflow.cfg already exists — skipping initialization."
fi

# -----------------------
# Configure airflow.cfg with CRUDINI
# -----------------------
if [ -f "$AIRFLOW_HOME/airflow.cfg" ]; then
    echo "🧩 Updating airflow.cfg with local parameters..."
    
        # --- Core section ---
    crudini --set "$AIRFLOW_HOME/airflow.cfg" core dags_folder "$(pwd)/dags"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" core base_log_folder "$(pwd)/airflow/logs"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" core executor "LocalExecutor"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" core simple_auth_manager_users "admin:admin,airflow:admin"

    # --- SMTP section (MailCatcher) ---
    crudini --set "$AIRFLOW_HOME/airflow.cfg" smtp smtp_host "localhost"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" smtp smtp_port "1025"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" smtp smtp_mail_from "airflow@example.com"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" smtp smtp_starttls "False"
    crudini --set "$AIRFLOW_HOME/airflow.cfg" smtp smtp_ssl "False"

    echo "✅ airflow.cfg successfully updated with SMTP and path settings."
else
    echo "⚠️ airflow.cfg not found — skipping CRUDINI configuration."
fi

# -----------------------
# Import Airflow variables
# -----------------------
if [ -f "dags/data/variables.json" ]; then
    airflow variables import dags/data/variables.json
    echo "✅ Airflow variables imported from dags/data/variables.json"
else
    echo "⚠️ variables.json not found — skipping import"
fi

# -----------------------
# ✅ Done
# -----------------------
echo ""
echo "🎉 Airflow and MailCatcher initialization complete!"
echo "📬 MailCatcher UI: http://localhost:1080"
echo ""
