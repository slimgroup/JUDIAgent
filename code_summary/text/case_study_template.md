# Case Study Template

Use the filled example below as the reference format for future benchmark runs.

---

## Case Metadata

- Prompt ID:
- Category:
- Difficulty:
- Agent mode: iterative / autonomous
- Runtime environment: local / PACE compute node
- Date:

## User Prompt

```text
PASTE PROMPT HERE
```

## Generated Julia Workflow

```julia
PASTE FINAL VALIDATED CODE HERE
```

## Validation Summary

- Correctness validation result:
- Domain-quality review result:
- Metric bundle used:
- Key diagnostics or repair notes:

## Output Artifacts

- Figure path:
- Data path:
- Log path:
- Script path:

## Scientific Interpretation

Write 3-6 sentences explaining why this case matters. Focus on whether the generated workflow is not only executable but also scientifically complete for the requested task.

## Paper-Ready Caption

**Case Study X.**

## Notes for Experiments Section

- Did retrieval help?
- Did dual validation catch anything correctness-only checks would have missed?
- Which metric signals would be reusable for SFT or RLHF?

---

# Filled Example: ricker_wavelet

## Case Metadata

- Prompt ID: `ricker_wavelet`
- Category: waveform / helper function
- Difficulty: easy
- Agent mode: iterative
- Runtime environment: PACE compute node
- Date: 2026-03-23

## User Prompt

```text
How do I create a Ricker wavelet in JUDI.jl with a peak frequency of 15 Hz and a total recording time of 2 seconds?
```

## Generated Julia Workflow

```julia
using JUDI

recording_time = 2000f0
sampling_interval = 4f0
peak_frequency = 0.015f0

wavelet = ricker_wavelet(recording_time, sampling_interval, peak_frequency)

println("Created Ricker wavelet with:")
println("  - Peak frequency: ", peak_frequency * 1000, " Hz")
println("  - Total time: ", recording_time, " ms")
println("  - Sampling interval: ", sampling_interval, " ms")
println("  - Number of samples: ", length(wavelet))
println("Successfully modeled seismic data with this wavelet!")
```

## Validation Summary

- Correctness validation result: passed via runtime execution on a PACE compute node
- Domain-quality review result: not triggered; this is a helper-wavelet task rather than a full imaging or inversion workflow
- Metric bundle used: none explicitly triggered for this helper task
- Key diagnostics or repair notes: static lint timed out because Julia language tooling is slow on first load, but runtime validation succeeded and closed the loop

## Output Artifacts

- Figure path: none
- Data path: none
- Log path: interactive CLI output only
- Script path: not automatically saved; the agent validated the generated Julia block in-memory

## Scientific Interpretation

This case establishes a minimal successful end-to-end execution path for JUDIAgent on PACE. The agent retrieved JUDI-specific usage patterns, generated a valid Ricker wavelet call, and passed runtime validation in the target Julia environment. Although the task is simple, it is an important smoke test because it verifies that the agent can translate a natural-language request into executable JUDI code with correct unit conventions (milliseconds and kilohertz). The case also shows that runtime validation remains useful even when Julia linting is too slow to complete interactively.

## Paper-Ready Caption

**Case Study 1.** JUDIAgent successfully generated and validated a minimal JUDI.jl Ricker wavelet example for a 15 Hz source with 2 s duration on a PACE compute node.

## Notes for Experiments Section

- Did retrieval help? yes; the agent relied on JUDI examples and helper documentation to recover the correct frequency units (`0.015 kHz` for `15 Hz`)
- Did dual validation catch anything correctness-only checks would have missed? in this small helper case, runtime validation was the decisive signal because linting timed out
- Which metric signals would be reusable for SFT or RLHF? execution success, correct unit handling, and concise task completion are the most relevant signals for this task family


---

# Filled Example: basic_2d_forward

## Case Metadata

- Prompt ID: `basic_2d_forward`
- Category: forward modeling
- Difficulty: easy
- Agent mode: iterative
- Runtime environment: PACE compute node
- Date: 2026-03-24

## User Prompt

```text
Write a simple 2D acoustic forward modeling example using JUDI.jl with a slightly richer but still lightweight two-layer velocity model (1.5 km/s on top, 3.5 km/s on bottom), 5 sources, 100 surface receivers, synthetic data saved to outputs/data/basic_2d_forward_data.jld2, one central-shot gather figure saved to outputs/figures/basic_2d_forward_shot.png, and one velocity-model figure saved to outputs/figures/basic_2d_forward_model.png.
```

## Generated Julia Workflow

```julia
using JUDI, JLD2, PythonPlot, LinearAlgebra

for dir in ["scripts", "outputs/figures", "outputs/data"]
    isdir(dir) || mkpath(dir)
end

n = (201, 101)
d = (10f0, 10f0)
o = (0f0, 0f0)

v = ones(Float32, n) .* 1.5f0
v[:, 51:end] .= 3.5f0
m = (1f0 ./ v).^2
model = Model(n, d, o, m)

nsrc = 5
nrec = 100
shot_spacing = 200f0
receiver_spacing = 20f0
source_depth = 20f0
receiver_depth = 10f0
recording_time = 2000f0
sampling_interval = 4f0

xsrc = convertToCell(collect(100f0 .+ shot_spacing .* Float32.(0:nsrc-1)))
ysrc = convertToCell(fill(0f0, nsrc))
zsrc = convertToCell(fill(source_depth, nsrc))
src_geometry = Geometry(xsrc, ysrc, zsrc; dt=fill(sampling_interval, nsrc), t=fill(recording_time, nsrc))

xrec = collect(range(0f0, step=receiver_spacing, length=nrec))
yrec = fill(0f0, nrec)
zrec = fill(receiver_depth, nrec)
rec_geometry = Geometry(xrec, yrec, zrec; dt=sampling_interval, t=recording_time, nsrc=nsrc)

wavelet = ricker_wavelet(recording_time, sampling_interval, 0.015f0)
q = judiVector(src_geometry, wavelet)
F = judiModeling(model, src_geometry, rec_geometry)
dobs = F * q

@save "outputs/data/basic_2d_forward_data.jld2" model src_geometry rec_geometry q dobs

fig_model = figure(figsize=(8, 6))
imshow(transpose(v), extent=[0, (n[1]-1)*d[1]/1000, (n[2]-1)*d[2]/1000, 0], cmap="viridis", aspect="auto")
colorbar(label="Velocity (km/s)")
xlabel("Lateral position (km)")
ylabel("Depth (km)")
title("Two-layer Velocity Model (1.5 km/s top, 3.5 km/s bottom)")
savefig("outputs/figures/basic_2d_forward_model.png", dpi=300, bbox_inches="tight")
close(fig_model)

shot_data = dobs.data[3]
A = 0.8f0 * maximum(abs.(shot_data))
fig_shot = figure(figsize=(10, 6))
imshow(shot_data, aspect="auto", cmap="seismic", origin="upper", vmin=-A, vmax=A, extent=[0, (nrec-1)*receiver_spacing/1000, recording_time, 0])
colorbar(label="Amplitude")
xlabel("Receiver position (km)")
ylabel("Time (ms)")
title("Shot Gather (Source 3 at x=0.5 km)")
savefig("outputs/figures/basic_2d_forward_shot.png", dpi=300, bbox_inches="tight")
close(fig_shot)
```

## Validation Summary

- Correctness validation result: passed via runtime execution on a PACE compute node in 92.69 s
- Domain-quality review result: successful forward-modeling workflow with model setup, acquisition geometry, wavelet construction, forward operator, saved data artifact, and saved figures
- Metric bundle used: `trace_energy_consistency`, `runtime_and_memory_budget`
- Key diagnostics or repair notes: Julia lint timed out because language-server startup is slow on the cluster, but runtime validation succeeded and the benchmark produced the requested artifacts

## Output Artifacts

- Figure path: `outputs/figures/basic_2d_forward_shot.png`; `outputs/figures/basic_2d_forward_model.png`
- Data path: `outputs/data/basic_2d_forward_data.jld2`
- Log path: interactive CLI output plus `outputs/data/basic_2d_forward_model_20260324_010038_run.json`
- Script path: `scripts/basic_2d_forward.jl` and archived validated script `scripts/basic_2d_forward_model_20260324_010038.jl`

## Scientific Interpretation

This case demonstrates that JUDIAgent can produce a scientifically meaningful end-to-end 2D forward-modeling workflow, not just a syntactically valid Julia snippet. The generated shot gather contains a strong direct arrival and a weaker later reflection, which is consistent with the requested two-layer velocity model and confirms that the acquisition geometry, source wavelet, and forward operator are working together coherently. The workflow also saved a reusable synthetic data object and a model-setup visualization, which makes the result easier to inspect and reproduce. While the shot-gather figure is the stronger paper-facing artifact, the velocity-model figure is still useful as a setup illustration even though its visual style is more generic than typical SLIM/JUDI publication figures.

## Paper-Ready Caption

**Case Study 2.** JUDIAgent generated and validated a complete 2D JUDI.jl forward-modeling workflow on a PACE compute node, producing both a synthetic shot gather and saved benchmark artifacts for a two-layer acoustic model.

## Notes for Experiments Section

- Did retrieval help? yes; the plotting and operator choices aligned more closely with JUDI examples after the prompt/context rules were tightened around local RAG examples
- Did dual validation catch anything correctness-only checks would have missed? yes; runtime validation remained decisive when Julia linting timed out, and the saved figures made it easier to judge whether the workflow was scientifically plausible rather than merely executable
- Which metric signals would be reusable for SFT or RLHF? execution success, artifact creation, physically plausible shot-gather structure, and benchmark-specific output completeness are all reusable signals for this task family
