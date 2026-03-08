# Quick Start Guide

## For First-Time Users

### 1. Setup (One-time)

```bash
cd judiagent_tutorial
chmod +x setup.sh  # Make executable (first time only)
./setup.sh
```

### 2. Launch Tutorial

```bash
chmod +x launch.sh  # Make executable (first time only)
./launch.sh
```

**Important**: In Jupyter, select kernel: **Kernel → Change Kernel → Python (judiagent_tutorial)**

Or manually:
```bash
source .venv/bin/activate
jupyter notebook judiagent_tutorial.ipynb
```

## For Returning Users

```bash
cd judiagent_tutorial
source .venv/bin/activate
jupyter notebook judiagent_tutorial.ipynb
```

## Requirements

- Python 3.12+
- Julia 1.11+
- JUDIAgent installed (via `pip install -e ../`)

## Troubleshooting

- **"Command not found"**: Make scripts executable: `chmod +x setup.sh launch.sh`
- **"Module not found"**: Run setup again: `./setup.sh` or install manually: `pip install -e ../`
- **"Kernel not found"**: Re-run setup script or register manually: `python -m ipykernel install --user --name judiagent_tutorial`
- **"Julia error"**: Run `julia -e 'import Pkg; Pkg.activate("."); Pkg.instantiate()'`
- **"Python version error"**: Ensure Python 3.12+ is installed: `python3 --version`

See README.md for detailed instructions.
