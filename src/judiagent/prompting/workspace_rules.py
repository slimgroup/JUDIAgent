"""Prompt fragments that define JUDIAgent output and workspace behavior."""

VISUALIZATION_SECTION = """
---

## Visualization And Plotting

For seismic plots, always anchor the plotting style to retrieved JUDI examples first:

- Search the JUDI examples in RAG before choosing a plotting approach.
- Prefer the plotting package and calling pattern that appears in the closest matching JUDI examples.
- Default to `SlimPlotting` or `PythonPlot` for seismic figures when examples support them.
- Avoid `Plots` for seismic outputs unless the user explicitly asks for it or the closest JUDI examples use it.
- Keep benchmark plots minimal and reproducible: one main figure per requested artifact unless the user asks for extras.
- Use physical axis labels when available (`Time (ms)`, `Receiver position (m)`, `Depth (m)`) rather than generic sample indices.

Preferred JUDI-style plotting patterns:

### SlimPlotting
```julia
using SlimPlotting
plot_velocity(reshape(m, n)', (d[1], d[2]); name="Velocity Model")
plot_sdata(dobs.data[1]; name="Shot Gather")
plot_simage(rtm; name="RTM Image")
```

### PythonPlot
```julia
using PythonPlot
fig = figure(figsize=(8, 5))
imshow(dobs.data[1], aspect="auto", cmap="seismic", origin="upper")
xlabel("Receiver position (m)")
ylabel("Time (ms)")
savefig("outputs/figures/example_shot_gather.png", dpi=300, bbox_inches="tight")
close(fig)
```

Only use generic `Plots` recipes as a fallback of last resort.
CondaPkg setup messages for plotting backends are normal on first use.
"""


MINIMAL_TASKS_SECTION = """
---

## Minimal Tasks

For simple helper tasks such as creating a wavelet, computing a small geometry object, or demonstrating a single JUDI helper function:

- Prefer the smallest runnable Julia snippet that answers the question directly.
- Do not add plotting, file output, `JLD2`, `Plots`, `PythonPlot`, `SlimPlotting`, or directory creation unless the user explicitly asks for them.
- Even when optional plotting is requested, keep it minimal and consistent with retrieved JUDI examples rather than expanding into a larger workflow.
- Do not turn a helper-function question into a full seismic workflow.
- Avoid optional extras after the main answer when they increase validation risk.

Examples of minimal tasks:
- `ricker_wavelet(...)`
- creating a `Geometry(...)` object
- building a `judiVector(...)` from an existing wavelet and source geometry
"""


WORKSPACE_MANAGEMENT = """
---

## Workspace And Output Management

All generated artifacts must live under the project output layout:

```text
project_root/
├── scripts/
├── outputs/
│   ├── figures/
│   └── data/
```

At the top of generated Julia scripts, create the folders if needed:

```julia
for dir in ["scripts", "outputs/figures", "outputs/data"]
    isdir(dir) || mkpath(dir)
end
```

### Naming Convention

Use descriptive names:

```text
{task}_{model}[_{stage}]_{content}.{ext}
```

Examples:
- `scripts/forward_2layer.jl`
- `outputs/figures/fwi_marmousi_final_velocity.png`
- `outputs/data/forward_2layer_dobs.jld2`

### Rules

- Never write generated files into the project root.
- Default saved Julia scripts to `scripts/{task}_{model}.jl`.
- Save figures under `outputs/figures/`.
- Save `.jld2` and `.segy` data under `outputs/data/`.
- For benchmark-style runs, save at least one primary figure and save the main generated data object when feasible.
- Keep experiment settings recoverable from saved scripts and a metadata sidecar.
- Avoid generic names like `output.png` or `result.jld2`.
"""
