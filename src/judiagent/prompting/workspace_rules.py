"""Prompt fragments that define JUDIAgent output and workspace behavior."""

VISUALIZATION_SECTION = """
---

## Visualization And Plotting

For seismic plots, prefer:

### SlimPlotting
```julia
using SlimPlotting
plot_velocity(reshape(m, n)', (d[1], d[2]); name="Velocity Model")
plot_sdata(dobs.data[1]; name="Shot Gather")
plot_simage(rtm; name="RTM Image")
```

### Plots.jl
```julia
using Plots
heatmap(v', xlabel="X (grid)", ylabel="Z (grid)", title="Velocity Model", color=:seismic)
heatmap(dobs.data[1], xlabel="Receiver", ylabel="Time Sample", title="Shot Gather")
savefig("outputs/figures/example_velocity.png")
```

### PyPlot
```julia
using PyPlot
imshow(v', aspect="auto", cmap="seismic", origin="upper")
savefig("outputs/figures/example_velocity.png")
close()
```

CondaPkg setup messages for plotting backends are normal on first use.
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
- Avoid generic names like `output.png` or `result.jld2`.
"""
