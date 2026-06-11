# Changelog

## Unreleased

### Added
- **ImageGather.jl as a second retrieval corpus.** The agent can now ground
  generated Julia in ImageGather.jl alongside JUDI.jl.
  - Cloned `slimgroup/ImageGather.jl@ext_PhyParams` into
    `src/judiagent/rag/imagegather/` and trimmed it to the material needed
    for retrieval and attribution: `docs/src/*.md`, `examples/*.jl`, the
    upstream `LICENSE`, and the upstream `README.md` (which links to the
    upstream repo for the figures, notebooks, source code, and tests that
    were dropped from this snapshot).
  - Registered `imagegather/docs` (markdown) and `imagegather/examples`
    (Julia) in `RAG_CATALOG` (`src/judiagent/rag/catalog.py`), reusing the
    existing markdown and Julia-example chunkers.
  - New retrieval tool `search_imagegather_examples`
    (`src/judiagent/tools/retrieve.py`) built via the shared
    `_build_retrieval_tool` factory; wired into the iterative agent
    (`src/judiagent/agents/agent.py`), the autonomous ReAct agent
    (`src/judiagent/agents/autonomous_agent.py`), and the `tools` package
    `__init__`.
  - Updated `GATHER_INTELLIGENCE` in `src/judiagent/prompting/shared.py` to
    tell the model when to pick `search_imagegather_examples` over
    `search_judi_examples`.

### Changed
- `search_codebase` (`src/judiagent/tools/retrieve.py`) now greps both
  `rag/judi/` and `rag/imagegather/` in a single invocation. Tool description
  updated to reflect the broader scope.
- `src/judiagent/rag/THIRD_PARTY.md` now documents the ImageGather corpus
  alongside JUDI (repo, branch `ext_PhyParams`, MIT license, maintainer,
  citation pointers).
- ImageGather example scripts (`examples/layers_cig.jl`,
  `examples/layers_sscig.jl`, `examples/offset_map.jl`) annotated with
  JUDI-style `# # Heading` section markers so the Julia example chunker
  produces ~19 well-titled chunks instead of three whole-file blobs. Code
  itself is unchanged; only top-level prose lines were inserted between
  logical sections.

### Operational notes
- After pulling this change, delete any stale per-source caches so the index
  rebuilds with the new corpus on the next agent run:
  ```bash
  rm -f  src/judiagent/rag/loaded_store/loaded_judi_*.pkl \
         src/judiagent/rag/loaded_store/loaded_imagegather_*.pkl
  rm -rf src/judiagent/rag/retriever_store/retriever_judi_* \
         src/judiagent/rag/retriever_store/retriever_imagegather_*
  ```
  Do not remove the `__init__.py` files in those directories — they are
  package markers, not data.
