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
