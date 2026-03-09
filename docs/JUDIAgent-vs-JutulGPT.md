# JUDIAgent vs JutulGPT – Differentiation Summary

This document summarizes how JUDIAgent differs from [JutulGPT](https://github.com/SINTEF-agentlab/JutulGPT) to support clear attribution and avoid any risk of plagiarism. JUDIAgent is inspired by JutulGPT’s agent architecture and is cited accordingly; the codebase and domain are distinct.

## 1. Domain and purpose

| Aspect | JutulGPT | JUDIAgent |
|--------|----------|-----------|
| **Target stack** | JutulDarcy (reservoir/geothermal simulation) | JUDI.jl (seismic modeling and inversion) |
| **RAG content** | JutulDarcy docs and examples | JUDI.jl docs and examples (`rag/judi/`) |
| **Prompts** | JutulDarcy-specific (e.g. Fimbul, GLMakie, reservoir) | JUDI.jl-specific (Model, Geometry, judiVector, judiModeling, acquisition, FWI/RTM) |

The system prompts in `src/judiagent/prompts.py` (geometry rules, golden template, debug playbook, workspace management) are **original to JUDIAgent** and have no counterpart in JutulGPT.

## 2. Naming and structure (code-level)

- **Agent layer**: `BaseAgent` → `AgentCore`; `Agent` → `IterativeCodeAgent`; `AutonomousAgent` → `ReActAgent`.
- **State**: `State` → `AgentState`; `CodeBlock` → `JuliaCodeBlock` (with `body` instead of `code`, `is_blank()` instead of `is_empty()`, `to_string()` instead of `get_full_code()`).
- **Graph nodes**: `agent` → `llm`, `tools` → `tool_executor`, `check_code` → `code_validator`, `finalize` → `complete`, `get_user_input` → `user_input`, `mcp_input` → `mcp_adapter`.
- **Tools**: All tool names differ (e.g. `run_julia_code` → `execute_julia_snippet`, `grep_search` → `search_codebase`, `retrieve_judi_examples` → `search_judi_examples`, etc.).
- **Methods**: 60+ renames across agents, utils, julia, nodes (e.g. `build_graph` → `construct_workflow`, `call_model` → `generate_response`, `invoke_model` → `_execute_llm_call`, and many helpers).

## 3. Implementation differences

- **Julia execution**: JUDIAgent uses a `JuliaExecutionResult` dataclass and distinct function names (`execute_julia_script`, `execute_julia_inline`, `execute_and_capture`, `format_runtime_error`); CondaPkg filtering and timeouts are implemented differently.
- **Retry logic**: Rate-limit retry is in dedicated helpers (`_invoke_with_rate_limit_retry`, `_is_rate_limit_error`, `_compute_backoff`) rather than inline in a single `invoke_model`.
- **Configuration**: JutulGPT uses `jutulgpt.toml` and a richer context/summarization stack; JUDIAgent uses `BaseConfiguration` from code/env only and a simpler trimming path.
- **Workspace management**: JUDIAgent adds a full workspace/output management section in prompts (`scripts/`, `outputs/figures/`, `outputs/data/`, naming conventions); JutulGPT has no equivalent.

## 4. What remains conceptually similar

- Use of LangGraph for the agent graph, with a base agent class and two concrete agents (evaluator–optimizer vs autonomous).
- General flow: user input → LLM ↔ tools, with an optional code-validation node for the iterative agent.
- Use of RAG (vector store + retriever), human-in-the-loop hooks, and MCP for VSCode.

These are common patterns in agent frameworks; the **implementation, naming, and domain content** are sufficiently different to treat JUDIAgent as an independent project that acknowledges JutulGPT as inspiration.

## 5. Publication and attribution

- **Your contributions** (domain, RAG content, JUDI-specific prompts, workspace rules, naming and structural refactor, Julia execution and retry implementation) are **substantial and original**. They are more than “cosmetic”: they change what the system does (JUDI vs JutulDarcy) and how it is implemented.
- **To avoid plagiarism concerns**: Always **cite JutulGPT** (SINTEF-agentlab) as the inspiration or base architecture for the agent framework. In the paper, state clearly that JUDIAgent adapts/extends that architecture for JUDI.jl and describe your own contributions (domain adaptation, RAG, prompts, refactor, evaluation, etc.).
- **Whether it is “enough” for a paper** depends on the venue and how you frame it. A paper that positions JUDIAgent as *“an AI assistant for JUDI.jl”* with clear novelty (workflow design, retrieval, prompts, integration, and possibly benchmarks or case studies) and honest attribution to JutulGPT is standard practice. If the bulk of the narrative and experiments are about JUDI workflows and your design choices (not about re-publishing JutulGPT’s ideas as yours), you are in a defensible position. When in doubt, disclose more rather than less and give JutulGPT explicit credit.
