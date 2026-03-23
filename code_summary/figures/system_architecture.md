# Figure: System Architecture

**Recommended assets:** `../../media/iterative_workflow.svg`, `../../media/react_workflow.svg`, and the implementation description in `../text/implementation.md`

The architecture story should be presented as a layered system rather than as a generic agent box diagram.

## Architecture layers to describe

1. **User-facing entry points**
   - CLI
   - LangGraph entrypoints
   - IDE or MCP-facing integration
2. **Agent layer**
   - iterative validated agent
   - autonomous ReAct agent
3. **Validation layer**
   - correctness validation
   - domain-quality review
   - metric recommendation
4. **Retrieval layer**
   - JUDI examples
   - documentation and local code search
5. **Julia bridge layer**
   - subprocess execution
   - lint and doc lookup drivers
6. **Physics layer**
   - JUDI.jl and its modeling, imaging, and inversion abstractions

## Recommended caption

**Figure Y.** JUDIAgent system architecture. The framework combines a LangGraph-based agent layer with retrieval, correctness validation, domain-aware workflow validation, and a Julia bridge to JUDI.jl. The architecture supports both a strict iterative coding path and a more open-ended ReAct-style tool path.


## Asset note

Use the newer `paper_*.svg` files in this folder for the paper. The older PNG files are legacy exports kept for reference only.
