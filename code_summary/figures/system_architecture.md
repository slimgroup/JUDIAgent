# Figure: System Architecture

**Filename:** `system_architecture.png`

## Description

This figure provides a high-level overview of the JUDIAgent system architecture, showing the relationships between software components, data flows, and external dependencies.

## Visual Elements

### Layout
- **Layered architecture** with horizontal tiers
- **Top:** User interfaces
- **Middle:** Agent core (Python)
- **Bottom:** Physics engine (Julia/JUDI)

### Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          JUDIAGENT SYSTEM ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         USER INTERFACES                              │    │
│  │                                                                      │    │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐   │    │
│  │   │     CLI      │   │   REST API   │   │   VSCode Extension   │   │    │
│  │   │  (Terminal)  │   │  (HTTP/WS)   │   │   (MCP Protocol)     │   │    │
│  │   │              │   │              │   │                      │   │    │
│  │   │  • Rich UI   │   │  • JSON I/O  │   │  • Copilot Chat      │   │    │
│  │   │  • Streaming │   │  • Async     │   │  • Inline Suggest    │   │    │
│  │   └──────┬───────┘   └──────┬───────┘   └──────────┬───────────┘   │    │
│  │          │                  │                       │               │    │
│  └──────────┼──────────────────┼───────────────────────┼───────────────┘    │
│             │                  │                       │                     │
│             └──────────────────┼───────────────────────┘                     │
│                                │                                             │
│                                ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      AGENT ORCHESTRATION LAYER                       │    │
│  │                           (LangGraph)                                │    │
│  │                                                                      │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                      State Machine                           │   │    │
│  │   │                                                              │   │    │
│  │   │  ┌────────┐    ┌────────┐    ┌────────┐    ┌──────────┐    │   │    │
│  │   │  │ Input  │───▶│ Agent  │◀──▶│ Tools  │───▶│ Validate │    │   │    │
│  │   │  │ Node   │    │ Node   │    │ Node   │    │   Node   │    │   │    │
│  │   │  └────────┘    └────────┘    └────────┘    └──────────┘    │   │    │
│  │   │                     │                                        │   │    │
│  │   └─────────────────────┼────────────────────────────────────────┘   │    │
│  │                         │                                             │    │
│  │   ┌─────────────────────┼────────────────────────────────────────┐   │    │
│  │   │                     ▼                                         │   │    │
│  │   │              Configuration                                    │   │    │
│  │   │   • agent_model: "openai:gpt-4.1"                            │   │    │
│  │   │   • retriever_provider: "chroma"                             │   │    │
│  │   │   • search_type: "mmr"                                        │   │    │
│  │   │   • human_interaction: {...}                                  │   │    │
│  │   └───────────────────────────────────────────────────────────────┘   │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│             ┌────────────────────┬────────────────────┐                     │
│             │                    │                    │                     │
│             ▼                    ▼                    ▼                     │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐            │
│  │   LLM BACKEND    │ │   RAG SYSTEM     │ │   TOOL EXECUTORS │            │
│  │                  │ │                  │ │                  │            │
│  │ ┌──────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │            │
│  │ │   OpenAI     │ │ │ │  Embeddings  │ │ │ │  Retrieval   │ │            │
│  │ │  GPT-4.1     │ │ │ │  (OpenAI /   │ │ │ │  - examples  │ │            │
│  │ │              │ │ │ │   Ollama)    │ │ │ │  - docs      │ │            │
│  │ └──────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │            │
│  │                  │ │        │         │ │                  │            │
│  │ ┌──────────────┐ │ │        ▼         │ │ ┌──────────────┐ │            │
│  │ │    Ollama    │ │ │ ┌──────────────┐ │ │ │  Execution   │ │            │
│  │ │  (Local LLM) │ │ │ │ Vector Store │ │ │ │  - julia run │ │            │
│  │ │  qwen2.5:7b  │ │ │ │  (Chroma /   │ │ │ │  - linter    │ │            │
│  │ │              │ │ │ │    FAISS)    │ │ │ │  - terminal  │ │            │
│  │ └──────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │            │
│  │                  │ │                  │ │                  │            │
│  └──────────────────┘ └──────────────────┘ │ ┌──────────────┐ │            │
│                                             │ │  File I/O    │ │            │
│                                             │ │  - read      │ │            │
│                                             │ │  - write     │ │            │
│                                             │ │  - grep      │ │            │
│                                             │ └──────────────┘ │            │
│                                             └──────────────────┘            │
│                                                      │                      │
│  ════════════════════════════════════════════════════╪══════════════════   │
│                               SUBPROCESS BOUNDARY     │                      │
│  ════════════════════════════════════════════════════╪══════════════════   │
│                                                      │                      │
│                                                      ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         JULIA RUNTIME                                │   │
│  │                                                                      │   │
│  │   ┌─────────────────────────────────────────────────────────────┐   │   │
│  │   │                        JUDI.jl                               │   │   │
│  │   │                                                              │   │   │
│  │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │   │
│  │   │  │  Model   │  │ Geometry │  │judiVector│  │judiModel │    │   │   │
│  │   │  │  struct  │  │  struct  │  │  struct  │  │ operator │    │   │   │
│  │   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │   │
│  │   │                                                              │   │   │
│  │   │  ┌────────────────────────────────────────────────────────┐ │   │   │
│  │   │  │                    Linear Algebra                       │ │   │   │
│  │   │  │  d = Pr * A_inv * Ps' * q    (Forward Modeling)        │ │   │   │
│  │   │  │  J = judiJacobian(F, q)      (Linearized Operator)     │ │   │   │
│  │   │  │  g = J' * r                   (Migration / Gradient)   │ │   │   │
│  │   │  └────────────────────────────────────────────────────────┘ │   │   │
│  │   │                              │                               │   │   │
│  │   └──────────────────────────────┼───────────────────────────────┘   │   │
│  │                                  │                                    │   │
│  │                                  ▼                                    │   │
│  │   ┌────────────────────────────────────────────────────────────────┐ │   │
│  │   │                         DEVITO                                  │ │   │
│  │   │              (Symbolic PDE to Optimized C/CUDA)                 │ │   │
│  │   │                                                                 │ │   │
│  │   │   Wave Equation ──▶ Stencil Code ──▶ CPU/GPU Execution         │ │   │
│  │   │                                                                 │ │   │
│  │   └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │   │   SegyIO     │  │     HDF5     │  │ LinearAlgebra│              │   │
│  │   │  (SEGY I/O)  │  │  (Model I/O) │  │   (Solvers)  │              │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

**User Interface Layer:**
- CLI with rich terminal output (syntax highlighting, panels)
- REST API for programmatic access
- MCP server for VSCode Copilot integration

**Agent Orchestration Layer:**
- LangGraph state machine managing workflow
- Configurable via `BaseConfiguration` dataclass
- Nodes: input, agent (LLM call), tools, validate, finalize

**Service Layer:**
- **LLM Backend:** OpenAI (hosted) or Ollama (local)
- **RAG System:** Embeddings + vector store
- **Tool Executors:** Retrieval, execution, file I/O

**Julia Runtime Layer:**
- JUDI.jl for high-level seismic abstractions
- Devito for PDE compilation and execution
- Supporting libraries for I/O and linear algebra

### Data Flow Annotations

1. **User → CLI/API:** Natural language query or structured request
2. **CLI → LangGraph:** Message added to state
3. **LangGraph → LLM:** Prompt + context for inference
4. **LLM → Tools:** Tool call requests
5. **Tools → Julia:** Code execution via subprocess
6. **Julia → JUDI → Devito:** PDE compilation and execution
7. **Results → LangGraph:** Output/errors fed back
8. **LangGraph → User:** Final response with code/results

### Color Scheme

- **Blue:** User-facing components
- **Green:** Agent/orchestration
- **Yellow:** LLM/AI components
- **Orange:** RAG/knowledge components
- **Purple:** Execution/tools
- **Gray:** Julia/physics layer

## Suggested Tools

- **Lucidchart** for professional diagrams
- **draw.io** for editable exports
- **PlantUML** for text-based generation
- **Mermaid** for documentation integration

