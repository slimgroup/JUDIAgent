#!/bin/bash
# Launch script for JUDIAgent Tutorial

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Check if Jupyter is installed
if ! command -v jupyter &> /dev/null; then
    echo "ERROR: Jupyter not found. Install with: pip install jupyter"
    exit 1
fi

# Launch Jupyter
echo "Launching Jupyter Notebook..."
jupyter notebook judiagent_tutorial.ipynb

