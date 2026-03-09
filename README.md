# JUDIAgent

JUDIAgent is a seismic coding copilot for JUDI.jl. It combines retrieval,
Julia code generation, validation, and a JUDI-specific workflow contract so
that generated code is grounded in the package's actual APIs and examples.

![JUDIAgent CLI](media/judiagent_cli.svg "JUDIAgent CLI")

## Overview

JUDIAgent is an intelligent coding assistant specialized in helping users work with the JUDI.jl (Julia Devito Inversion) package. It leverages large language models combined with retrieval-augmented generation (RAG) to provide accurate, context-aware code generation for seismic modeling and inversion tasks.

**Key Features**
- Retrieval-augmented code generation using JUDI.jl examples
- Automatic code validation (linting + execution)
- Human-in-the-loop refinement workflow
- Multiple interfaces: CLI and VSCode integration via LangGraph/MCP

## Getting Started

### Prerequisites

This project requires both **Python** and **Julia**, along with some system-level dependencies:

- `git`: See [git downloads](https://git-scm.com/downloads)
- `Python3 >=3.12`: See [Download Python](https://www.python.org/downloads/)
- `Julia`: Package tested on version 1.11.6. See [Installing Julia](https://julialang.org/install/)
- `build-essential`
- `graphviz` and `graphviz-dev`: See [Graphviz download](https://graphviz.org/download/)

Optional:

- `uv`: Recommended package manager. See [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)
- `ollama`: For running local models. See [Download Ollama](https://ollama.com/download)

> NOTE: See [Installing python](https://docs.astral.sh/uv/guides/install-python/) for installing Python using `uv`.

### Step 1: Python Setup

Clone the repository and set up the Python environment:

```bash
# Clone the repository
git clone https://github.com/haoyunl2/JUDIAgent.git
cd JUDIAgent/
```

If you are using `uv`, initialize the environment:

```bash
# Initialize the environment
uv venv
source .venv/bin/activate

# Install packages
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

### Step 2: Julia Setup

Set up the Julia project with JUDI.jl dependencies:

```bash
julia
# In Julia REPL
julia> import Pkg; Pkg.activate("."); Pkg.instantiate()
```

This will install all necessary packages listed in `Project.toml`.

### Step 3: Environment Configuration

Generate and configure the `.env` file:

```bash
cp .env.example .env
```

Edit `.env` to provide:
- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGSMITH_API_KEY`: Required for UI/debugging features

The agent will create `scripts/`, `outputs/figures/`, and `outputs/data/`
on demand when it saves generated Julia code or artifacts. Those paths are
treated as runtime outputs rather than tracked source directories.

### Step 4: Test the Installation

Run the agent to verify everything works:

```bash
uv run examples/agent.py
```

To run the autonomous agent instead:

```bash
uv run examples/autonomous_agent.py
```

## Usage

JUDIAgent provides two agent variants optimized for different use cases:

### Standard Agent

The standard agent follows an evaluator-optimizer workflow where code is first generated and then validated. Recommended for smaller models or specific tasks like simulation setup.

![Iterative workflow](media/iterative_workflow.svg "Iterative workflow")

```bash
uv run examples/agent.py
```

### Autonomous Agent

The autonomous agent has extended tool access and can interact with the environment more freely. Provides a Copilot-like experience with sufficiently capable LLMs.

![Autonomous workflow](media/react_workflow.svg "Autonomous workflow")

```bash
uv run examples/autonomous_agent.py
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
