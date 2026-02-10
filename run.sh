#!/bin/bash

# Script to run src/main.py with parameters
# Usage: ./run.sh <USERNAME> <PROFILE_NAME> <CONFIG>
# Optional: ./run.sh <USERNAME> <PROFILE_NAME> <CONFIG> <PDF_FILENAME>

# Check if minimum parameters are provided
if [ $# -lt 3 ]; then
    echo "Usage: $0 <USERNAME> <PROFILE_NAME> <CONFIG> [PDF_FILENAME]"
    echo "Example: $0 aleksandr Default default"
    echo "Example with PDF filename: $0 aleksandr Default default output.pdf"
    exit 1
fi

USERNAME=$1
PROFILE_NAME=$2
CONFIG=$3
PDF_FILENAME=${4:-result.pdf}  # Default to result.pdf if not provided

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Run the Python script with parameters
python "$SCRIPT_DIR/src/main.py" --username "$USERNAME" --profile-name "$PROFILE_NAME" --config "$CONFIG" --pdf-filename "$PDF_FILENAME"

# Deactivate virtual environment
deactivate