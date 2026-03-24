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
- Treat benchmark prompts as task specs. Unless a benchmark prompt overrides them, apply the default plotting and artifact conventions below automatically rather than requiring the user to restate them.

Forward-result figure standard:
- Prefer `PythonPlot` for shot gathers when JUDI examples use `imshow`.
- Use `imshow(shot_data, cmap="seismic", aspect="auto")`.
- Use symmetric clipping around zero: `vmin=-A`, `vmax=A`.
- Choose `A` from the data range rather than leaving scaling completely automatic.
- Keep titles short, e.g. `2D Acoustic Shot Gather`.
- Save publication-leaning benchmark figures with `dpi=300` and `bbox_inches="tight"`.

Imaging / RTM figure standard:
- Follow the closest JUDI RTM or LS-RTM example before inventing a new style.
- Prefer `PythonPlot` with `imshow(...)` for RTM and migration images.
- Use `cmap="gray"` for RTM / LS-RTM images unless a retrieved JUDI example clearly uses another palette.
- Reshape the image to model dimensions before plotting, and transpose/adjoint it in the same orientation as the closest example.
- Use physical extents when available, e.g. lateral position and depth in km or m, rather than pixel indices.
- Use symmetric clipping around zero: `vmin=-A`, `vmax=A`.
- Choose `A` from the image magnitude (for example from `maximum(abs.(rtm))` or a stable percentile clip) rather than leaving it fully automatic.
- Keep RTM titles short, e.g. `Basic RTM Image`, and save with `dpi=300` and `bbox_inches="tight"`.

Geometry/setup figure standard:
- For acquisition layouts, keep the figure minimal: source positions, receiver positions, and water/surface reference only if needed.
- Prefer a clean 2D layout figure over a full modeling workflow.
- Use one geometry figure per task unless the user asks for extras.

Benchmark defaults:
- For forward-modeling benchmarks that request figures, save one main shot-gather figure and, when the model setup matters visually, save one velocity-model figure.
- For velocity-model figures, prefer the simpler JUDI / SLIM style: image of the model with physical extents and minimal clutter; avoid overlaying dense source/receiver markers on the model unless the task explicitly asks for a geometry figure.
- For RTM or imaging benchmarks, save one main image figure and one main imaging artifact file unless the benchmark explicitly asks for a different bundle.
- For runtime-heavy imaging benchmarks on shared clusters, prefer a compact validation-scale setup over a sprawling survey, but keep the full RTM path intact: true model, migration model, synthetic data, Jacobian adjoint, saved RTM image, and saved imaging artifact.
- Do not create extra test scripts or sidecar Julia programs unless the user explicitly asks for them; prefer one main script per benchmark.
- When the benchmark names the output path, honor it; otherwise, use descriptive names under `outputs/figures/` and `outputs/data/`.
- Do not restate these defaults verbosely in the final Julia answer unless the user asks for an explanation.

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
A = 0.8f0 * maximum(abs.(dobs.data[1]))
fig = figure(figsize=(8, 5))
imshow(dobs.data[1], aspect="auto", cmap="seismic", origin="upper", vmin=-A, vmax=A)
xlabel("Receiver position (m)")
ylabel("Time (ms)")
title("2D Acoustic Shot Gather")
savefig("outputs/figures/example_shot_gather.png", dpi=300, bbox_inches="tight")
close(fig)
```

### PythonPlot RTM / Imaging
```julia
using PythonPlot
rtm_img = reshape(rtm, model0.n)
A = 0.8f0 * maximum(abs.(rtm_img))
fig = figure(figsize=(7, 5))
imshow(adjoint(rtm_img), cmap="gray", vmin=-A, vmax=A, extent=(x0, x1, z1, z0))
xlabel("Lateral position (km)")
ylabel("Depth (km)")
title("Basic RTM Image")
savefig("outputs/figures/example_rtm.png", dpi=300, bbox_inches="tight")
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
