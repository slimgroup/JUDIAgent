# Implementation

## 4.1 System Architecture

JUDIAgent is implemented as a Python package (`judiagent`) that orchestrates:

1. **LLM Backend:** OpenAI GPT-4.1 / DeepSeek / Anthropic (hosted) or Ollama (local)
2. **RAG System:** LangChain + ChromaDB/FAISS vector stores
3. **Julia Runtime:** JUDI.jl executed via subprocess
4. **State Management:** LangGraph for workflow orchestration

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JUDIAgent System                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌───────────────┐    ┌───────────────────────┐ │
│  │   User       │    │   LLM         │    │   Vector Store        │ │
│  │  Interface   │◄──►│  (GPT-4.1/    │◄──►│   (Chroma/FAISS)      │ │
│  │  (CLI/API)   │    │   DeepSeek)   │    │   JUDI Examples       │ │
│  └──────────────┘    └───────────────┘    └───────────────────────┘ │
│         │                   │                       │               │
│         │                   ▼                       │               │
│         │           ┌───────────────┐               │               │
│         │           │   LangGraph   │               │               │
│         │           │   Pipeline    │◄──────────────┘               │
│         │           │   Engine      │                               │
│         │           └───────────────┘                               │
│         │                   │                                       │
│         │         ┌─────────┴─────────┐                             │
│         │         ▼                   ▼                             │
│         │   ┌──────────────┐   ┌──────────────────┐                 │
│         │   │   Tools      │   │   Nodes          │                 │
│         │   │  - RAG       │   │ - code_validator  │                 │
│         │   │  - execute   │   │ - complete        │                 │
│         │   │  - lint      │   └──────────────────┘                 │
│         │   │  - file I/O  │                                        │
│         │   └──────────────┘                                        │
│         │         │                                                 │
│         ▼         ▼                                                 │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │                    Julia Runtime                            │   │
│   │  ┌─────────────────────────────────────────────────────┐   │   │
│   │  │                      JUDI.jl                         │   │   │
│   │  │  Model │ Geometry │ judiModeling │ judiJacobian     │   │   │
│   │  └─────────────────────────────────────────────────────┘   │   │
│   │                           │                                 │   │
│   │                    ┌──────┴──────┐                          │   │
│   │                    ▼             ▼                          │   │
│   │              ┌──────────┐  ┌──────────────┐                 │   │
│   │              │  Devito  │  │   HDF5/SEGY  │                 │   │
│   │              │  (PDE)   │  │   (I/O)      │                 │   │
│   │              └──────────┘  └──────────────┘                 │   │
│   └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 4.2 Key Components

### 4.2.1 Agent Classes

Two agent variants are implemented in `src/judiagent/agents/`:

**`IterativeCodeAgent` (Evaluator-Optimizer):**
- Pipeline: `user_input` → `llm` → `tool_executor` → `code_validator` → `complete`
- Includes automatic code validation via the `code_validator` node
- Suitable for code generation tasks with well-defined outputs

**`ReActAgent` (Autonomous):**
- Pipeline: `user_input` → `llm` ↔ `tool_executor` (ReAct loop)
- More flexible tool use without mandatory validation
- Suitable for exploratory tasks and complex workflows

Both inherit from `AgentCore`, which provides shared infrastructure for LLM invocation, tool binding, conversation trimming, and rate-limit resilient retries.

### 4.2.2 State Schema

```python
@dataclass
class AgentState:
    messages: Annotated[Sequence[AnyMessage], add_messages]
    error: bool = False
    error_message: str = ""
    iteration_count: int = 0
    code_block: JuliaCodeBlock = field(default_factory=JuliaCodeBlock)
    remaining_steps: int = 50
    is_last_step: bool = False
```

The `add_messages` annotation ensures append-only message history with ID-based merging.

### 4.2.3 Tool Implementations

**Retrieval Tools (`tools/retrieve.py`):**

```python
@tool("search_judi_examples")
def search_judi_examples(query: str, config: RunnableConfig) -> str:
    """Semantic search over JUDI.jl examples."""
    with make_retriever(config, spec=JUDI_EXAMPLES_SPEC) as rag_retriever:
        docs = rag_retriever.invoke(query)
    return format_examples(docs)
```

**Execution Tools (`tools/execution.py`):**

```python
@tool("execute_julia_snippet")
def execute_julia_snippet(code: str) -> str:
    """Execute Julia code via subprocess."""
    code = normalize_julia_imports(code)
    code = reduce_simulation_steps(code)
    report, failed = _run_code_execution(code)
    return report if failed else "Code executed successfully!"
```

### 4.2.4 RAG Pipeline

The RAG system uses LangChain's retriever abstractions:

```python
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma(
    embedding_function=embedding,
    persist_directory="retriever_store/",
    collection_name="judi_examples"
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 2, "fetch_k": 10, "lambda_mult": 0.5}
)
```

### 4.2.5 Julia Integration

Julia code is executed via subprocess to isolate the Python and Julia runtimes:

```python
def execute_julia_inline(code: str, project_dir: str | None = None):
    proc = subprocess.run(
        ["julia", f"--project={project_dir}", "-e", code],
        capture_output=True,
        text=True,
        timeout=180
    )
    return proc.stdout, proc.stderr
```

JUDI package loading can take 30-60 seconds; the timeout accommodates this.

## 4.3 Configuration

Configuration is managed via a dataclass with LangGraph-compatible schema:

```python
@dataclass
class BaseConfiguration:
    embedding_model: str = "openai:text-embedding-3-small"
    retriever_provider: Literal["faiss", "chroma"] = "chroma"
    examples_search_type: Literal["similarity", "mmr"] = "mmr"
    examples_search_kwargs: dict = {"k": 2, "fetch_k": 10, "lambda_mult": 0.5}
    agent_model: str = "deepseek:deepseek-chat"
    human_interaction: HumanInteraction = field(default_factory=HumanInteraction)
```

## 4.4 User Interfaces

### 4.4.1 Command-Line Interface (CLI)

```bash
uv run examples/agent.py              # Iterative code agent
uv run examples/autonomous_agent.py   # ReAct autonomous agent
```

The CLI provides a rich terminal interface with syntax-highlighted code, tool logging, and error highlighting.

### 4.4.2 API Interface

```python
from judiagent import react_agent

config = RunnableConfig(configurable={"autonomous_agent_model": "openai:gpt-4.1"})
result = react_agent.graph.invoke({
    "messages": [{"role": "user", "content": "Create a 2D FWI example"}]
}, config=config)
```

### 4.4.3 MCP Integration (VSCode)

JUDIAgent can be deployed as an MCP server for VSCode Copilot integration:

```json
{
  "servers": {
    "langgraph-judiagent": {
      "url": "http://localhost:2024/mcp"
    }
  }
}
```

## 4.5 Dependencies

| Category | Packages |
|----------|----------|
| Python (agent) | `langchain-core`, `langgraph`, `langchain-openai`, `langchain-ollama` |
| Python (RAG) | `langchain-chroma`, `faiss-cpu` |
| Python (CLI) | `rich`, `prompt-toolkit` |
| Julia (physics) | `JUDI.jl`, `Devito`, `SegyIO`, `HDF5` |

Installation is managed via `uv` (Python) and Julia's `Pkg` manager.

## 4.6 Repository Structure

```
JUDIAgent/
├── src/judiagent/
│   ├── agents/
│   │   ├── agent_base.py         # AgentCore abstract foundation
│   │   ├── agent.py              # IterativeCodeAgent (evaluator-optimizer)
│   │   └── autonomous_agent.py   # ReActAgent (autonomous)
│   ├── tools/
│   │   ├── execution.py          # execute_julia_snippet, lint_julia_code
│   │   ├── retrieve.py           # RAG tools
│   │   └── other.py              # File I/O tools
│   ├── nodes/
│   │   └── check_code.py         # Code validation pipeline node
│   ├── rag/
│   │   ├── judi/                 # JUDI.jl docs and examples
│   │   ├── retrieval.py          # Vector store management
│   │   └── retriever_specs.py
│   ├── julia/
│   │   └── julia_code_runner.py  # Julia subprocess execution layer
│   ├── prompts.py                # System prompts
│   ├── state.py                  # AgentState, JuliaCodeBlock
│   └── configuration.py          # BaseConfiguration
├── examples/
│   ├── agent.py
│   └── autonomous_agent.py
├── Project.toml                  # Julia dependencies
├── pyproject.toml                # Python dependencies
└── README.md
```
