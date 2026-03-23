# JUDIAgent

JUDIAgent is a seismic coding copilot for JUDI.jl. It combines retrieval,
Julia code generation, validation, and a JUDI-specific workflow contract so
that generated code is grounded in the package's actual APIs and examples.

![JUDIAgent CLI](media/judiagent_cli.svg "JUDIAgent CLI")

## Overview

JUDIAgent is an intelligent coding assistant specialized in helping users work with the JUDI.jl (Julia Devito Inversion) package. It leverages large language models combined with retrieval-augmented generation (RAG) to provide accurate, context-aware code generation for seismic modeling and inversion tasks.

**Key Features**
- Retrieval-augmented code generation using JUDI.jl examples
- Dual-stage validation: code correctness plus JUDI-specific scientific review
- Human-in-the-loop refinement workflow
- Multiple interfaces: CLI and VSCode integration via LangGraph/MCP

## Getting Started

### Prerequisites

This project requires both **Python** and **Julia**, along with some system-level dependencies:

- `git`: See [git downloads](https://git-scm.com/downloads)
- `Python3 >=3.12`: See [Download Python](https://www.python.org/downloads/)
- `Julia`: Package tested on version 1.11.x. See [Installing Julia](https://julialang.org/install/)
- `build-essential`
- `graphviz` and `graphviz-dev`: See [Graphviz download](https://graphviz.org/download/)

Optional:

- `uv`: Recommended package manager. See [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)
- `ollama`: For running local models. See [Download Ollama](https://ollama.com/download)

> NOTE: See [Installing python](https://docs.astral.sh/uv/guides/install-python/) for installing Python using `uv`.

For **shared clusters / login-node development** (e.g. PACE): how to keep fast tests and syncing off expensive allocations is documented in [docs/devel-pace.md](docs/devel-pace.md).

For **Codex-based development** in this repository: repo-local agent guidance lives in [AGENTS.md](AGENTS.md), and reusable setup notes live in [docs/codex-setup.md](docs/codex-setup.md).

### Choose Your Environment

JUDIAgent supports two common setup modes.

#### Option A: PACE or another shared cluster

Use this when you are working over SSH on a login node plus interactive compute allocations.

1. On the login node, do the cheap setup only:

```bash
git clone https://github.com/haoyunl2/JUDIAgent.git
cd JUDIAgent
uv venv
source .venv/bin/activate
uv sync
source env/pace-local.sh
cp .env.example .env
./.venv/bin/python -m pytest tests/integration_tests/test_entrypoints.py
```

2. When you are ready for Julia/JUDI initialization or a real agent run, move to an interactive compute node:

```bash
salloc ...
srun --pty bash
cd /path/to/JUDIAgent
source .venv/bin/activate
export JUDIAgent_PACE_SHARED_DEPOT=off
source env/pace-local.sh
module load julia/1.11.3
julia --project=. -e 'import Pkg; Pkg.Registry.update(); Pkg.instantiate()'
./.venv/bin/python examples/agent.py
```

Notes:

- `env/pace-local.sh` uses a dedicated persistent depot at `~/julia-depot-judiagent`, reuses `~/julia-depot` as a fallback layer when present, keeps the JUDIAgent CondaPkg environment at `~/condapkg-env-judiagent`, and still stores uv downloads in `.uv-cache/`.
- This is useful on shared systems where home-directory quota is limited or where you want all JUDI-related state to stay with the clone.
- Avoid running the first heavy `Pkg.instantiate()` or large `Pkg.precompile()` pass on the login node; that work belongs on an interactive compute node.

#### Option B: Desktop or workstation with Julia installed directly

Use this on your laptop, desktop, or a dedicated machine where `julia` is already on `PATH`.

```bash
git clone https://github.com/haoyunl2/JUDIAgent.git
cd JUDIAgent
uv venv
source .venv/bin/activate
uv sync
source env/desktop-local.sh
cp .env.example .env
julia --project=. -e 'import Pkg; Pkg.instantiate()'
./.venv/bin/python -m pytest tests/integration_tests/test_entrypoints.py
```

Notes:

- `env/desktop-local.sh` uses the same repo-local `.julia-depot/`, `.condapkg-env/`, and `.uv-cache/` layout, but does not assume a cluster module system.
- If you prefer to use your default global Julia depot on a personal machine, you can skip sourcing `env/desktop-local.sh`.

### Python Setup

The project Python environment is expected to live in `.venv/`.

```bash
uv venv
source .venv/bin/activate
uv sync
```

If encountering an error due to the `pygraphviz` package, try:

```bash
# Note: Adjust for your OS/package manager
brew install graphviz  # macOS
uv add --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz
```

### Julia Setup

The Julia project should be initialized from the repository root:

```bash
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

This installs the Julia packages from `Project.toml`. In this repository, JUDI may also trigger CondaPkg-managed Python-side dependencies. On PACE, `env/pace-local.sh` stores them in `~/condapkg-env-judiagent` and uses a dedicated `~/julia-depot-judiagent`. If an old shared depot causes registry conflicts, set `JUDIAgent_PACE_SHARED_DEPOT=off` before sourcing the helper.

On a desktop or workstation, running this directly is fine. On PACE or another shared cluster, do the first heavy Julia/JUDI initialization on an interactive compute node rather than on the login node.

### Environment Configuration

Generate and configure the `.env` file:

```bash
cp .env.example .env
```

Edit `.env` to provide:

- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGSMITH_API_KEY`: Required for GUI/debugging features; can be left blank for CLI-only usage
- `LANGSMITH_PROJECT`: Optional tracing project name
- `LANGSMITH_TRACING_V2`: Enable if you want LangSmith tracing
- `EDITOR`: Your preferred CLI editor, such as `vim`, `nvim`, or `nano`

The agent will create `scripts/`, `outputs/figures/`, and `outputs/data/` on demand when it saves generated Julia code or artifacts. Those paths are treated as runtime outputs rather than tracked source directories.

### Verify the Installation

For a low-cost smoke check:

```bash
./.venv/bin/python -m pytest tests/integration_tests/test_entrypoints.py
```

For the standard agent:

```bash
./.venv/bin/python examples/agent.py
```

For the autonomous agent:

```bash
./.venv/bin/python examples/autonomous_agent.py
```

On PACE or another shared cluster, prefer running the full agent on an interactive compute allocation rather than on the login node. The login node should mainly be used for editing, syncing, and low-cost smoke checks.

## Usage

JUDIAgent provides two agent variants optimized for different use cases:

### Standard Agent

The standard agent follows a staged scientific coding workflow where code is first generated, then checked for technical correctness, and finally reviewed for JUDI-specific scientific completeness when the task looks like imaging or inversion. Recommended for smaller models or specific tasks like simulation setup.

![Iterative workflow](media/iterative_workflow.svg "Iterative workflow")

```bash
./.venv/bin/python examples/agent.py
```

### Autonomous Agent

The autonomous agent has extended tool access and can interact with the environment more freely. Provides a Copilot-like experience with sufficiently capable LLMs.

![Autonomous workflow](media/react_workflow.svg "Autonomous workflow")

```bash
./.venv/bin/python examples/autonomous_agent.py
```

## Configuration

Agent settings are defined in `src/judiagent/configuration.py`:

```python
# Core settings
cli_mode: bool = True  # Enable CLI interface

# Model selection
LOCAL_MODELS = False  # Use local Ollama models instead of OpenAI
LLM_MODEL_NAME = "ollama:qwen3:14b" if LOCAL_MODELS else "openai:gpt-4.1"
EMBEDDING_MODEL_NAME = (
    "ollama:nomic-embed-text" if LOCAL_MODELS else "openai:text-embedding-3-small"
)
```

### Advanced Configuration

The `BaseConfiguration` class provides additional runtime settings:

| Parameter | Description |
|-----------|-------------|
| `human_interaction` | Enable human-in-the-loop controls |
| `embedding_model` | Embedding model for RAG |
| `retriever_provider` | Vector store backend (chroma/faiss) |
| `examples_search_type` | Search strategy (similarity/mmr) |
| `examples_search_kwargs` | Search parameters (k, fetch_k, etc.) |
| `agent_model` | LLM for code generation |
| `agent_prompt` | System prompt for the agent |

## Interfaces

### CLI Mode

Enable CLI mode in `src/judiagent/configuration.py`:

```python
cli_mode = True
```

The CLI provides an interactive interface for:
- Asking questions about JUDI.jl
- Generating and validating code
- Reading and writing files

### VSCode Integration (MCP)

For VSCode integration via Model Context Protocol:

1. Set configuration:
```python
cli_mode = False
mcp_mode = True
```

2. Start the LangGraph server:
```bash
source .venv/bin/activate
langgraph dev
```

3. Configure VSCode with an MCP server (see `.vscode.example/mcp.json`)

### GUI

JUDIAgent supports a web-based GUI through the companion [JUDIAgent-GUI](https://github.com/yourusername/JUDIAgent-GUI) project.

To use the GUI:

1. Disable CLI mode: `cli_mode = False`
2. Start the LangGraph server: `langgraph dev`
3. Start the GUI from the JUDIAgent-GUI directory: `pnpm dev`
4. Access at `http://localhost:3000/`

## Project Structure

```
JUDIAgent/
├── src/judiagent/
│   ├── agents/            # Agent variants and workflow graphs
│   ├── cli/               # Console views, menus, branding, streaming
│   ├── core/              # Shared runtime helpers
│   ├── julia/             # Python-Julia execution bridge
│   ├── nodes/             # Validation and graph nodes
│   ├── prompting/         # Prompt components and prompt composition
│   ├── rag/               # Retrieval and JUDI source material
│   ├── tools/             # Tool surface exposed to the agents
│   └── configuration.py   # Runtime settings
├── media/                 # README assets
├── examples/              # Launch scripts
├── judiagent_tutorial/    # Tutorial materials
└── tests/                 # Test suite
```

## Testing

Tests use [pytest](https://docs.pytest.org/en/stable/):

```bash
uv run pytest
```

## License

See [LICENSE](LICENSE) for details.

## Acknowledgments

- [JUDI.jl](https://github.com/slimgroup/JUDI.jl) - Julia Devito Inversion framework
- [Devito](https://www.devitoproject.org/) - Symbolic finite difference DSL
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration framework
- [JutulGPT](https://github.com/SINTEF-agentlab/JutulGPT) - upstream inspiration for the original agent framing
