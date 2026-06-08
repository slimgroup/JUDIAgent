# Third-Party Retrieval Corpora

`src/judiagent/rag/judi/` is retrieval material, not original JUDIAgent agent
implementation code. It is included so the agent can ground generated Julia in
real JUDI.jl documentation and example workflows.

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

## Distribution Notes

The Python package build excludes bulky notebook outputs and binary example data
from built artifacts. The source repository may still contain text examples and
documentation used to rebuild retrieval indexes.

Before creating a DOI or public archival release, review whether any included
notebooks, SEG-Y/HDF5 files, or field-data workflows should instead be replaced
with download instructions or git submodules that point to the upstream source.
