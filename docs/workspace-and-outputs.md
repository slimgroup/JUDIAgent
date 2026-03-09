# Where generated scripts and data go

The **prompts** in `src/judiagent/prompts.py` do **not** store any generated data. They only contain **instructions** that tell the LLM where to write files when it generates code or saves results.

At runtime, the agent is instructed to place:

| Content | Location (relative to project root) | Ignored by git |
|--------|--------------------------------------|----------------|
| Generated Julia scripts | `scripts/` (e.g. `scripts/forward_2layer.jl`) | Yes (`.gitignore`) |
| Figures / plots | `outputs/figures/` | Yes |
| Numerical data (.jld2, .segy) | `outputs/data/` | Yes |

So: **prompt-generated scripts** go under **`scripts/`**; **saved data and figures** go under **`outputs/figures/`** and **`outputs/data/`**. These paths are defined in the “WORKSPACE & OUTPUT MANAGEMENT” section of `prompts.py` and are intentionally not tracked by git.
