
import sys
import os
import subprocess
import importlib.util

# --- Configuration ---
AIRFLOW_HOME = os.path.join(os.path.dirname(__file__), 'airflow')

# --- Colors for output ---
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(message):
    print(f"\n{Colors.BOLD}--- {message} ---" + Colors.END)

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}" + Colors.END)

def print_warning(message):
    print(f"{Colors.YELLOW}! {message}" + Colors.END)

def print_error(message):
    print(f"{Colors.RED}✗ {message}" + Colors.END)

def print_instruction(message):
    print(f"  {Colors.YELLOW}➡️  {message}" + Colors.END)

def check_virtual_env():
    """Checks if the script is running in a virtual environment."""
    print_step("Checking for virtual environment")
    if sys.prefix == sys.base_prefix:
        print_error("Not running in a virtual environment.")
        print_instruction("Please create and activate a virtual environment first.")
        print_instruction("Example: python3 -m venv .venv && source .venv/bin/activate")
        return False
    print_success("Running in a virtual environment.")
    return True

def check_dependencies():
    """Checks if dependencies from requirements.txt are installed."""
    print_step("Checking Python dependencies")
    requirements_path = 'requirements.txt'
    if not os.path.exists(requirements_path):
        print_error(f"'{requirements_path}' not found.")
        return False

    all_installed = True
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle extras like 'dvc[gs]' -> 'dvc'
            package_name = line.split('[')[0].split('==')[0].split('>')[0].split('<')[0]
            
            spec = importlib.util.find_spec(package_name)
            if spec is None:
                if all_installed: # Print header only once
                    print_warning("Some packages are missing.")
                    all_installed = False
                print(f"  - {package_name}")

    if all_installed:
        print_success("All dependencies from requirements.txt are installed.")
        return True
    else:
        print_instruction(f"Please install the missing packages by running:")
        print_instruction(f"pip install -r {requirements_path}")
        return False

def check_airflow_config():
    """Checks if the Airflow configuration file exists."""
    print_step("Checking Airflow configuration")
    airflow_cfg_path = os.path.join(AIRFLOW_HOME, 'airflow.cfg')
    
    if not os.path.exists(airflow_cfg_path):
        print_error("Airflow configuration file not found.")
        print_warning(f"Looked for: {airflow_cfg_path}")
        print_instruction("You need to initialize the Airflow database.")
        print_instruction(f"First, ensure AIRFLOW_HOME is set: export AIRFLOW_HOME={AIRFLOW_HOME}")
        print_instruction("Then run: airflow db migrate")
        return False
        
    print_success("Airflow configuration file (airflow.cfg) found.")
    return True

def main():
    """Main function to run all checks."""
    print(f"{Colors.BOLD}🚀 Starting project initialization checks...{Colors.END}")
    
    if not check_virtual_env():
        sys.exit(1)
        
    if not check_dependencies():
        sys.exit(1)

    if not check_airflow_config():
        sys.exit(1)

    print_success("\n✅ All checks passed! Your environment seems ready.")
    print_instruction("You can now start the Airflow components (scheduler, webserver).")

if __name__ == "__main__":
    main()
