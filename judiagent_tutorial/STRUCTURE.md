# JUDIAgent Tutorial Directory Structure

## Overview

This directory contains the JUDIAgent tutorial notebook and helper scripts. It
uses the parent repository environment by default so the tutorial, package code,
lockfile, and retrieval corpus stay aligned.

## Files

```
judiagent_tutorial/
├── Project.toml              # Optional tutorial-local Julia project
├── requirements.txt          # Optional pip fallback notes
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

- **Project.toml**: Optional tutorial-local Julia package list. The public
  release path uses the root `Project.toml`.
- **requirements.txt**: Optional fallback notes for standalone pip-based use.
  The public release path uses the root `pyproject.toml` and `uv.lock`.

### Documentation

- **README.md**: Complete setup instructions for users
- **DEPLOYMENT.md**: Guide for deploying to server/multiple users
- **QUICK_START.md**: Quick reference for common tasks
- **STRUCTURE.md**: This file (directory structure explanation)

### Scripts

- **setup.sh**: Sets up the parent repository environment and registers a
  Jupyter kernel.
- **launch.sh**: Launches the notebook from the parent repository environment.

### Tutorial

- **judiagent_tutorial.ipynb**: Main tutorial notebook

## Dependencies

### Julia Packages (Project.toml)
- JUDI.jl: Seismic modeling and inversion
- LinearAlgebra: Standard library
- Random: Standard library  
- Statistics: Standard library

### Python Packages

Use the root `uv.lock` through `uv sync`. `requirements.txt` is only a fallback
for standalone tutorial copies.

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
   - Julia: root `Project.toml` with local `Manifest.toml` generated as needed
   - Python: root `uv.lock`

## Notes

- Keep the tutorial in the parent repository when possible.
- Do not commit tutorial `.env`, `.venv`, or generated notebook outputs.
- JUDIAgent is installed from the parent repository.
