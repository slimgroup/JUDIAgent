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

- Figure path: `code_summary/figures/basic_2d_forward_shot_paper.png`; `code_summary/figures/basic_2d_forward_model_paper.png`
- Data path: `outputs/data/basic_2d_forward_data.jld2`
- Log path: interactive CLI output plus `outputs/data/basic_2d_forward_model_20260324_031831_run.json`
- Script path: `scripts/basic_2d_forward_model_20260324_031831.jl` and redraw helper `scripts/redraw_paper_figures.jl`

## Scientific Interpretation

This case demonstrates that JUDIAgent can produce a scientifically meaningful end-to-end 2D forward-modeling workflow, not just a syntactically valid Julia snippet. The generated shot gather contains a strong direct arrival and a weaker later reflection, which is consistent with the requested two-layer velocity model and confirms that the acquisition geometry, source wavelet, and forward operator are working together coherently. The workflow also saved a reusable synthetic data object and a model-setup visualization, which makes the result easier to inspect and reproduce. For the paper bundle, the figure set was redrawn into cleaner publication-style versions while keeping the original benchmark outputs unchanged; the shot-gather figure remains the stronger scientific artifact, while the velocity-model figure serves as a compact setup panel.

## Paper-Ready Caption

**Case Study 2.** JUDIAgent generated and validated a complete 2D JUDI.jl forward-modeling workflow on a PACE compute node, producing a physically plausible shot gather plus publication-style setup and result figures for a two-layer acoustic model.

## Notes for Experiments Section

- Did retrieval help? yes; the plotting and operator choices aligned more closely with JUDI examples after the prompt/context rules were tightened around local RAG examples
- Did dual validation catch anything correctness-only checks would have missed? yes; runtime validation remained decisive when Julia linting timed out, and the saved figures made it easier to judge whether the workflow was scientifically plausible rather than merely executable
- Which metric signals would be reusable for SFT or RLHF? execution success, artifact creation, physically plausible shot-gather structure, and benchmark-specific output completeness are all reusable signals for this task family


---

# Filled Example: rtm_basic

## Case Metadata

- Prompt ID: `rtm_basic`
- Category: imaging / RTM
- Difficulty: medium
- Agent mode: iterative
- Runtime environment: PACE compute node
- Date: 2026-03-24

## User Prompt

```text
Write a basic RTM (Reverse Time Migration) example using JUDI.jl with a compact validation-scale setup, a simple two-layer true model, a slightly smoother migration model, synthetic observed data, RTM formed with the adjoint of the Jacobian operator, one main RTM script, an RTM figure saved to outputs/figures/rtm_basic_image.png, and the migrated image or main imaging artifact saved to outputs/data/rtm_basic_image.jld2. Keep the RTM figure close to JUDI/SLIM style: gray colormap, physical extents, tighter symmetric clipping that reveals reflector-scale structure, and no unnecessary extra visualizations.
```

## Generated Julia Workflow

```julia
using JUDI, JLD2, PythonPlot, LinearAlgebra

n = (151, 76)
d = (12.5f0, 12.5f0)
o = (0f0, 0f0)

v_true = ones(Float32, n) .* 1.5f0
for iz = 1:n[2], ix = 1:n[1]
    interface_depth = 40 + div(ix, 4)
    if iz >= interface_depth
        v_true[ix, iz] = 2.0f0
    end
end

v_mig = copy(v_true)
for iz = 2:n[2]-1, ix = 2:n[1]-1
    v_mig[ix, iz] = 0.2f0 * v_true[ix, iz] +
                    0.2f0 * (v_true[ix-1, iz] + v_true[ix+1, iz] +
                            v_true[ix, iz-1] + v_true[ix, iz+1])
end

model_true = Model(n, d, o, (1f0 ./ v_true).^2)
model_mig = Model(n, d, o, (1f0 ./ v_mig).^2)

nsrc = 4
nrec = 80
source_depth = 25f0
receiver_depth = 30f0
recording_time = 1500f0
dt = 4f0

xsrc = convertToCell(collect(150f0 .+ 300f0 .* Float32.(0:nsrc-1)))
ysrc = convertToCell(fill(0f0, nsrc))
zsrc = convertToCell(fill(source_depth, nsrc))
src_geometry = Geometry(xsrc, ysrc, zsrc; dt=fill(dt, nsrc), t=fill(recording_time, nsrc))

xrec = collect(range(0f0, step=15f0, length=nrec))
yrec = fill(0f0, nrec)
zrec = fill(receiver_depth, nrec)
rec_geometry = Geometry(xrec, yrec, zrec; dt=dt, t=recording_time, nsrc=nsrc)

q = judiVector(src_geometry, ricker_wavelet(recording_time, dt, 0.015f0))
d_obs = judiModeling(model_true, src_geometry, rec_geometry) * q
J = judiJacobian(judiModeling(model_mig, src_geometry, rec_geometry), q)
rtm = adjoint(J) * d_obs
rtm_image = reshape(rtm, n)

jldsave("outputs/data/rtm_basic_image.jld2"; rtm_image=rtm_image, model_true=(1f0 ./ v_true).^2, model_mig=(1f0 ./ v_mig).^2, n=n, d=d, o=o)
```

## Validation Summary

- Correctness validation result: passed via runtime execution on a PACE compute node in 101.73 s
- Domain-quality review result: successful compact RTM workflow with a true model, smoother migration model, synthetic observed data, Jacobian-adjoint imaging path, saved RTM artifact, and saved RTM figure
- Metric bundle used: `image_residual_norm`, `illumination_balance`
- Key diagnostics or repair notes: earlier RTM attempts failed due to Julia syntax issues, oversized scripts, and an overly short runtime budget; after tightening the prompt defaults and extending heavy-task timeouts, the compact RTM benchmark became stable

## Output Artifacts

- Figure path: `code_summary/figures/rtm_basic_image_paper.png`
- Data path: `outputs/data/rtm_basic_image.jld2`
- Log path: interactive CLI output plus `outputs/data/rtm_basic_image_20260324_023452_run.json`
- Script path: `scripts/rtm_basic_image_20260324_023452.jl` and redraw helper `scripts/redraw_paper_figures.jl`

## Scientific Interpretation

This case shows that JUDIAgent can assemble and validate a complete compact RTM workflow rather than stopping at forward modeling. The resulting migrated image is not yet a strong final imaging result, but it is scientifically meaningful as a proof-of-capability benchmark because it preserves the full RTM chain: true model, migration model, synthetic data generation, and adjoint-Jacobian imaging. The paper-style redraw tightens the display clip and removes a thin shallow strip from the displayed image to reduce source imprint, which makes the deeper reflector-scale structure easier to inspect without altering the saved RTM artifact itself. This makes the case appropriate for a methods or experiments section that emphasizes successful workflow generation under constrained compute settings.

## Paper-Ready Caption

**Case Study 3.** JUDIAgent generated and validated a compact JUDI.jl RTM workflow on a PACE compute node, then produced a paper-style RTM figure from the saved imaging artifact to reduce shallow source imprint and highlight reflector-scale structure.

## Notes for Experiments Section

- Did retrieval help? yes; the agent converged only after the prompting rules explicitly anchored RTM structure and plotting conventions to JUDI examples
- Did dual validation catch anything correctness-only checks would have missed? yes; runtime validation surfaced Julia syntax issues, workflow bloat, and timeout problems that would not have been obvious from static prompting alone
- Which metric signals would be reusable for SFT or RLHF? execution success, artifact completeness, compact-yet-complete imaging workflow structure, and improved figure readability after redraw are useful signals for this task family
