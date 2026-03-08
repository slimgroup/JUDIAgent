# Deployment Guide for JUDIAgent Tutorial

This guide explains how to deploy the JUDIAgent tutorial to a server for use by multiple colleagues.

## Directory Structure

```
judiagent_tutorial/
├── Project.toml          # Julia dependencies (minimal)
├── Manifest.toml          # Auto-generated after Pkg.instantiate()
├── requirements.txt       # Python dependencies
├── README.md             # User-facing setup instructions
├── DEPLOYMENT.md         # This file (for administrators)
├── setup.sh              # Automated setup script
├── launch.sh             # Launch script
├── .gitignore            # Git ignore rules
└── judiagent_tutorial.ipynb  # Tutorial notebook
```

## For Server Deployment

### Step 1: Upload Files to Server

Upload the entire `judiagent_tutorial/` directory to your server:

```bash
# Example: Using scp
scp -r judiagent_tutorial/ user@server:/path/to/tutorials/

# Or using rsync
rsync -avz judiagent_tutorial/ user@server:/path/to/tutorials/judiagent_tutorial/
```

### Step 2: Initial Setup on Server

On the server, run the setup script:

```bash
cd /path/to/tutorials/judiagent_tutorial
chmod +x setup.sh launch.sh
./setup.sh
```

This will:
- Create Python virtual environment
- Install Python dependencies
- Install Julia packages
- Set up environment configuration

### Step 3: Generate Manifest.toml (for reproducibility)

After initial setup, generate the Julia Manifest.toml:

```bash
julia -e 'import Pkg; Pkg.activate("."); Pkg.instantiate(); Pkg.status()'
```

This creates `Manifest.toml` with exact package versions. **Commit this file** for reproducibility.

### Step 4: Create Shared Environment (Optional)

If multiple users will use the same server, consider:

#### Option A: Shared Virtual Environment (Recommended)

```bash
# Create shared venv in a common location
python3 -m venv /shared/judiagent_tutorial_venv
source /shared/judiagent_tutorial_venv/bin/activate
pip install -r requirements.txt
pip install -e /path/to/JUDIAgent  # Install JUDIAgent

# Users activate shared environment
source /shared/judiagent_tutorial_venv/bin/activate
```

#### Option B: User-Specific Environments

Each user runs `./setup.sh` in their own copy or home directory.

### Step 5: Configure Jupyter for Multiple Users

If using Jupyter on a server:

```bash
# Install Jupyter
pip install jupyter jupyterlab

# Configure Jupyter
jupyter notebook --generate-config

# Set password (optional, for security)
jupyter notebook password
```

For JupyterHub or shared access, see [JupyterHub documentation](https://jupyterhub.readthedocs.io/).

## For Individual Users (Colleagues)

### Quick Start

1. **Navigate to tutorial directory**:
   ```bash
   cd /path/to/tutorials/judiagent_tutorial
   ```

2. **Run setup** (first time only):
   ```bash
   ./setup.sh
   ```

3. **Launch tutorial**:
   ```bash
   ./launch.sh
   ```
   Or manually:
   ```bash
   source .venv/bin/activate
   jupyter notebook judiagent_tutorial.ipynb
   ```

### If Setup Already Done (Shared Environment)

If the environment is already set up:

```bash
# Activate environment
source .venv/bin/activate  # or shared venv path

# Launch
jupyter notebook judiagent_tutorial.ipynb
```

## Reproducibility

### Julia Environment

The `Project.toml` specifies package names, and `Manifest.toml` (generated) specifies exact versions.

**To ensure reproducibility:**
1. After `Pkg.instantiate()`, commit `Manifest.toml`
2. Users run `Pkg.instantiate()` to get exact versions

### Python Environment

The `requirements.txt` uses version constraints. For exact reproducibility:

```bash
# After setup, generate lock file
pip freeze > requirements-lock.txt

# Users can install exact versions
pip install -r requirements-lock.txt
```

**Note**: `requirements-lock.txt` should be generated on a clean environment.

## Troubleshooting

### Common Issues

1. **"JUDIAgent not found"**
   - Solution: Install JUDIAgent: `pip install -e /path/to/JUDIAgent`

2. **"Julia packages not found"**
   - Solution: Run `julia -e 'import Pkg; Pkg.activate("."); Pkg.instantiate()'`

3. **"Permission denied"**
   - Solution: Check file permissions: `chmod +x setup.sh launch.sh`

4. **"API key error"**
   - Solution: Create `.env` file with `OPENAI_API_KEY=your_key`

### Server-Specific Issues

1. **Port conflicts**: Change Jupyter port: `jupyter notebook --port 8889`
2. **Firewall**: Ensure Jupyter port is accessible
3. **Resource limits**: Check disk space and memory

## Best Practices

1. **Version Control**: Commit `Manifest.toml` for Julia reproducibility
2. **Documentation**: Keep README.md updated
3. **Testing**: Test setup on clean environment before deployment
4. **Backup**: Keep backup of working environment
5. **Updates**: Document any dependency updates

## Updating Dependencies

### Julia

```bash
julia -e 'import Pkg; Pkg.activate("."); Pkg.update(); Pkg.instantiate()'
# Review changes, then commit new Manifest.toml
```

### Python

```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
pip freeze > requirements-lock.txt  # Update lock file
```

## Notes

- The tutorial requires JUDIAgent to be installed (from parent directory or via pip)
- First-time Julia package compilation may take time
- Agent code generation requires API keys (OpenAI or Ollama)

