# Third-Party Retrieval Corpora

`src/judiagent/rag/judi/` and `src/judiagent/rag/imagegather/` are retrieval
material, not original JUDIAgent agent implementation code. They are included
so the agent can ground generated Julia in real upstream documentation and
example workflows.

## JUDI.jl Material

The JUDI documentation and examples originate from the JUDI.jl project:

- Repository: <https://github.com/slimgroup/JUDI.jl>
- License: MIT, copyright SLIM group @ Georgia Institute of Technology and
  contributors. The upstream MIT license text is included in
  `src/judiagent/rag/judi/LICENSE`.
- Citation: Felix J. Herrmann, Philipp A. Witte, and Mathias Louboutin,
  "JUDI: An open-source software for seismic modeling and inversion",
  The Leading Edge, 2019.

Some examples contain additional author notes, publication references, and
dataset instructions. Keep those notices with the files when redistributing or
modifying the corpus.

## ImageGather.jl Material

The ImageGather documentation and examples originate from the ImageGather.jl
project:

- Repository: <https://github.com/slimgroup/ImageGather.jl>
- Branch: `ext_PhyParams` (extended physical parameters / extended Born
  modeling for subsurface offset common-image gathers).
- License: MIT, copyright (c) 2020 SLIM group @ Georgia Institute of
  Technology. The upstream MIT license text is included in
  `src/judiagent/rag/imagegather/LICENSE`.
- Maintainer / citation contact: Mathias Louboutin
  (<mlouboutin3@gatech.edu>). See `src/judiagent/rag/imagegather/README.md`
  for the referenced method papers (Giboli et al., SEG 2012; Dafni & Symes,
  GJI 2019) and the Zenodo DOI badge for software citation.

The example scripts at `src/judiagent/rag/imagegather/examples/` reference
figures under `docs/img/` and a notebook under `examples/notebooks/` that are
kept alongside the corpus for context but are not themselves ingested by the
retriever (the `imagegather` catalog entries only index `.md` files in
`docs/src/` and `.jl` files in `examples/`).

## Distribution Notes

The Python package build excludes bulky notebook outputs and binary example data
from built artifacts. The source repository may still contain text examples and
documentation used to rebuild retrieval indexes.

Before creating a DOI or public archival release, review whether any included
notebooks, SEG-Y/HDF5 files, or field-data workflows should instead be replaced
with download instructions or git submodules that point to the upstream source.
