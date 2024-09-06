#!/bin/bash
# Activate virtual environment
source /home/ubuntu/SocialMediaAutopilot_EC2/venv/bin/activate

# Change to the main project directory
cd /home/ubuntu/SocialMediaAutopilot_EC2

# Function to source all .env files in a directory and its subdirectories
source_env_files() {
    local dir="$1"
    while IFS= read -r -d '' env_file; do
        echo "Sourcing: $env_file"
        source "$env_file"
    done < <(find "$dir" -type f -name ".env" -print0)
}

# Source all .env files in the project directory and its subdirectories
source_env_files "."

# Run the Python script
python main.py

# Deactivate the virtual environment
deactivate

