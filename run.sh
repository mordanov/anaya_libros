#!/bin/bash

# Script to run main.py with parameters
# Usage: ./run.sh <USERNAME> <PROFILE_NAME> <pdf_filename>

# Check if all parameters are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <USERNAME> <PROFILE_NAME> <pdf_filename>"
    echo "Example: $0 aleksandr Default output.pdf"
    exit 1
fi

USERNAME=$1
PROFILE_NAME=$2
PDF_FILENAME=$3

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Run the Python script with parameters
python "$SCRIPT_DIR/main.py" --username "$USERNAME" --profile-name "$PROFILE_NAME" --pdf-filename "$PDF_FILENAME"

# Deactivate virtual environment
deactivate