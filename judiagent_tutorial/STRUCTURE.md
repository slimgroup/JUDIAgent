# JUDIAgent Tutorial Directory Structure

## Overview

This directory contains a self-contained, reproducible tutorial for JUDIAgent.

## Files

```
judiagent_tutorial/
├── Project.toml              # Julia dependencies (minimal set)
├── Manifest.toml             # Auto-generated: exact Julia package versions
├── requirements.txt          # Python dependencies
├── judiagent_tutorial.ipynb # Main tutorial notebook
├── README.md                 # User-facing setup guide
├── DEPLOYMENT.md             # Server deployment guide
├── QUICK_START.md            # Quick reference
├── setup.sh                  # Automated setup script
├── launch.sh                 # Launch script
├── .gitignore                # Git ignore rules
└── STRUCTURE.md              # This file
```

## File Descriptions

### Configuration Files

- **Project.toml**: Julia package dependencies (JUDI.jl, LinearAlgebra, etc.)
- **Manifest.toml**: Auto-generated after `Pkg.instantiate()`, contains exact versions
- **requirements.txt**: Python package dependencies (LangChain, Jupyter, etc.)

### Documentation

- **README.md**: Complete setup instructions for users
- **DEPLOYMENT.md**: Guide for deploying to server/multiple users
- **QUICK_START.md**: Quick reference for common tasks
- **STRUCTURE.md**: This file (directory structure explanation)

### Scripts

- **setup.sh**: Automated setup (creates venv, installs dependencies)
- **launch.sh**: Quick launch script for Jupyter

### Tutorial

- **judiagent_tutorial.ipynb**: Main tutorial notebook

## Dependencies

### Julia Packages (Project.toml)
- JUDI.jl: Seismic modeling and inversion
- LinearAlgebra: Standard library
- Random: Standard library  
- Statistics: Standard library

### Python Packages (requirements.txt)
- Core: langchain, langgraph, pydantic
- Jupyter: ipykernel, jupyter, notebook
- JUDIAgent: Must be installed separately (`pip install -e ../`)

## Setup Workflow

1. **First Time Setup**:
   ```bash
   ./setup.sh
   ```

2. **Launch Tutorial**:
   ```bash
   ./launch.sh
   ```

3. **For Reproducibility**:
   - Julia: `Manifest.toml` is auto-generated with exact versions
   - Python: Can generate `requirements-lock.txt` with `pip freeze`

## Notes

- Each tutorial directory is self-contained
- Julia environment is isolated via `Project.toml`
- Python environment is isolated via virtual environment
- JUDIAgent must be installed from parent directory or via pip
