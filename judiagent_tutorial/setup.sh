#!/bin/bash
# Setup script for JUDIAgent Tutorial
# This script sets up both Python and Julia environments

set -e  # Exit on error

echo "=========================================="
echo "JUDIAgent Tutorial Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.12+"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Validate Python version (3.12+)
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 12 ]); then
    echo "ERROR: Python 3.12+ required. Found: $python_version"
    exit 1
fi

# Check Julia
echo "Checking Julia..."
if command -v julia &> /dev/null; then
    julia_version=$(julia --version | awk '{print $3}')
    echo "Julia version: $julia_version"
else
    echo "ERROR: Julia not found. Please install Julia 1.11+"
    exit 1
fi

# Setup Python environment
echo ""
echo "=========================================="
echo "Setting up Python environment..."
echo "=========================================="

# Check if uv is available (faster alternative)
# Can be overridden with USE_UV environment variable: USE_UV=true ./setup.sh
USE_UV=${USE_UV:-false}
if [ "$USE_UV" != "true" ] && command -v uv &> /dev/null; then
    # Auto-detect in non-interactive mode, prompt in interactive mode
    if [ -t 0 ]; then
        echo "Found uv (faster package installer). Use it? [Y/n]"
        read -t 5 -r response || response="y"
        if [[ "$response" =~ ^[Yy]$ ]] || [ -z "$response" ]; then
            USE_UV=true
            echo "Using uv for faster installation..."
        fi
    else
        # Non-interactive: use uv if available
        USE_UV=true
        echo "Using uv for faster installation (non-interactive mode)..."
    fi
fi

if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Activating..."
    source .venv/bin/activate
else
    echo "Creating Python virtual environment..."
    if [ "$USE_UV" = true ]; then
        uv venv
    else
        python3 -m venv .venv
    fi
    source .venv/bin/activate
fi

echo "Upgrading pip..."
if [ "$USE_UV" = true ]; then
    uv pip install --upgrade pip
else
    pip install --upgrade pip
fi

echo "Installing Python dependencies..."
if [ "$USE_UV" = true ]; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

echo "Installing JUDIAgent package from parent directory..."
if [ -d "../src/judiagent" ]; then
    if [ "$USE_UV" = true ]; then
        uv pip install -e ../
    else
        pip install -e ../
    fi
    echo "✓ JUDIAgent installed from parent directory"
else
    echo "WARNING: JUDIAgent source not found. Install manually with: pip install -e ../"
fi

# Register Jupyter kernel
echo ""
echo "Registering Jupyter kernel..."
# Install ipykernel if not already installed
if ! python -c "import ipykernel" 2>/dev/null; then
    echo "Installing ipykernel..."
    if [ "$USE_UV" = true ]; then
        uv pip install ipykernel
    else
        pip install ipykernel
    fi
fi

if python -c "import ipykernel" 2>/dev/null; then
    python -m ipykernel install --user --name judiagent_tutorial --display-name "Python (judiagent_tutorial)" || true
    echo "✓ Jupyter kernel registered (refresh Jupyter to see it)"
else
    echo "Note: Could not register Jupyter kernel. Install manually: pip install ipykernel"
fi

# Setup Julia environment
echo ""
echo "=========================================="
echo "Setting up Julia environment..."
echo "=========================================="

echo "Installing Julia packages..."
julia -e 'import Pkg; Pkg.activate("."); Pkg.instantiate(); println("✓ Julia packages installed")'

# Check for .env file
echo ""
echo "=========================================="
echo "Environment Configuration"
echo "=========================================="

if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found."
    echo "Create .env file with:"
    echo "  OPENAI_API_KEY=your_key_here"
    echo "  LANGSMITH_API_KEY=your_key_here  # Optional"
    if [ -f "../.env.example" ]; then
        echo "Copying .env.example from parent directory..."
        cp ../.env.example .env
        echo "✓ .env file created. Please edit it with your API keys."
    fi
else
    echo "✓ .env file found"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the tutorial:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Start Jupyter: jupyter notebook judiagent_tutorial.ipynb"
echo ""
echo "Or use the provided launch script: ./launch.sh"
echo ""
echo "In Jupyter, select kernel: Kernel → Change Kernel → Python (judiagent_tutorial)"
echo ""

