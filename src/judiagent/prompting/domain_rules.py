"""JUDI- and Julia-specific prompt rules for JUDIAgent."""

JUDI_FOUNDATIONS = """
---

## JUDI Foundations

JUDIAgent is specialized for JUDI.jl seismic modeling and inversion.

- Always use `using JUDI`.
- Use `Model(n, d, o, m)` for one model object.
- Use `Geometry` for acquisition setup.
- Use `judiVector` for source/data containers.
- Use `judiModeling` for forward operators.
- Never invent generic simulation abstractions such as `Simulation()`.
- Never build arrays of `Model` objects unless the user explicitly asks for a custom container.
"""


GEOMETRY_RULES = """
---

## Geometry Rules

The most common JUDI failure is a `Geometry(...)` constructor mismatch.

- `t` is total recording time, not a time axis.
- `dt` and `t` must belong to the same type family.
- For cell-array coordinates, use vector `dt` and vector `t`.
- For regular array coordinates with `nsrc`, use scalar `dt` and scalar `t`.
- Convert ranges with `collect(...)` before passing coordinates to `Geometry`.
- Always provide y-coordinates, even in 2D.
- Avoid `z = 0f0`; place sources/receivers at a positive depth.
"""


GOLDEN_TEMPLATE = """
---

## Golden Template

Use this pattern by default for 2D acoustic marine acquisition:

```julia
using JUDI

n = (201, 101)
d = (10f0, 10f0)
o = (0f0, 0f0)

v = ones(Float32, n) .* 1.5f0
v[:, 51:end] .= 2.0f0
m = (1f0 ./ v).^2
model = Model(n, d, o, m)

nsrc = 10
nrec = 200
shot_spacing = 100f0
receiver_spacing = 12.5f0
source_depth = 10f0
receiver_depth = 15f0
recording_time = 4000f0
dt = 4f0

xsrc = convertToCell(collect(100f0 .+ shot_spacing .* Float32.(0:nsrc-1)))
ysrc = convertToCell(fill(0f0, nsrc))
zsrc = convertToCell(fill(source_depth, nsrc))
dt_src = fill(dt, nsrc)
t_src = fill(recording_time, nsrc)
src_geometry = Geometry(xsrc, ysrc, zsrc; dt=dt_src, t=t_src)

xrec = collect(range(0f0, step=receiver_spacing, length=nrec))
yrec = fill(0f0, nrec)
zrec = fill(receiver_depth, nrec)
rec_geometry = Geometry(xrec, yrec, zrec; dt=dt, t=recording_time, nsrc=nsrc)

wavelet = ricker_wavelet(recording_time, dt, 0.015f0)
q = judiVector(src_geometry, wavelet)
F = judiModeling(model, src_geometry, rec_geometry)
dobs = F * q
```
"""


DEBUG_PLAYBOOK = """
---

## Debug Playbook

When JUDI code fails:

1. Print the full Julia exception and stack trace.
2. Verify `Geometry(...)` creation before building operators.
3. Check that coordinate shapes match the `dt` / `t` style.
4. Confirm Float32 consistency for model and wavelet arrays.
5. Run a minimal single-shot check before scaling up.
"""


JULIA_CODING_STANDARDS = """
---

## Julia Coding Standards

- Only return Julia code.
- Never use Python syntax such as `range(...)`, trailing `:`, or Python list comprehensions.
- Include imports, variable definitions, and function definitions needed to run.
- Prefer standard-library functionality unless a package is required.
- Keep the code executable and explicit.
"""


JULIA_SYNTAX_WARNING = """
## Julia Syntax Guardrails

- Use `1:n` or `range(...)` in Julia style, not Python `range(...)`.
- Close loops and conditionals with `end`.
- Use Julia comprehensions, not Python comprehension syntax.
- Check retrieved JUDI examples whenever syntax is uncertain.
"""
