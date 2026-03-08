# Figure: Wave Equation Design Loop

**Filename:** `wave_design_loop.png`

## Description

This figure illustrates how the agent interfaces with JUDI's wave-equation solvers in an experimental design context, showing the flow from design parameters through physics simulation to data and back to design refinement.

## Visual Elements

### Layout
- **Circular/loop structure** emphasizing the iterative nature
- **Center:** Wave equation PDE
- **Outer ring:** Agent decision cycle

### Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WAVE-EQUATION DESIGN LOOP                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                         ┌───────────────────┐                           │
│                         │   AGENT DECIDES   │                           │
│                         │   - Source locs   │                           │
│                         │   - Receiver geom │                           │
│                         │   - Wavelet f₀    │                           │
│                         │   - Recording T   │                           │
│                         └─────────┬─────────┘                           │
│                                   │                                      │
│              ┌────────────────────┼────────────────────┐                │
│              │                    ▼                    │                │
│              │    ┌──────────────────────────────┐    │                │
│              │    │      JUDI CONFIGURATION       │    │                │
│              │    │                               │    │                │
│              │    │  Model(n, d, o, m)           │    │                │
│              │    │  src_geometry = Geometry(...) │    │                │
│              │    │  rec_geometry = Geometry(...) │    │                │
│              │    │  q = judiVector(src, wavelet) │    │                │
│              │    │                               │    │                │
│              │    └──────────────┬───────────────┘    │                │
│              │                   │                     │                │
│              │                   ▼                     │                │
│  ┌───────────┤    ┌──────────────────────────────┐    ├───────────┐   │
│  │           │    │      WAVE EQUATION SOLVE      │    │           │   │
│  │  DESIGN   │    │                               │    │   DATA    │   │
│  │  SPACE    │    │   1   ∂²u                     │    │           │   │
│  │           │    │  ─── ──── - ∇²u = q(x,t)     │    │   d_obs   │   │
│  │   θ ∈ Θ   │    │   c²  ∂t²                     │    │           │   │
│  │           │    │                               │    │           │   │
│  │  Sources  │    │  d = P_r · A⁻¹ · P_s' · q    │    │  Seismic  │   │
│  │  Receivers│    │                               │    │  Records  │   │
│  │  Timing   │    │        ┌─────────┐            │    │           │   │
│  │           │    │        │ DEVITO  │            │    │           │   │
│  │           │    │        │  (PDE)  │            │    │           │   │
│  │           │    │        └─────────┘            │    │           │   │
│  └───────────┤    └──────────────┬───────────────┘    ├───────────┘   │
│              │                   │                     │                │
│              │                   ▼                     │                │
│              │    ┌──────────────────────────────┐    │                │
│              │    │       QUALITY METRIC          │    │                │
│              │    │                               │    │                │
│              │    │  • Image resolution           │    │                │
│              │    │  • Illumination coverage      │    │                │
│              │    │  • SNR / data quality         │    │                │
│              │    │  • Execution time             │    │                │
│              │    │                               │    │                │
│              │    └──────────────┬───────────────┘    │                │
│              │                   │                     │                │
│              └───────────────────┼─────────────────────┘                │
│                                  │                                      │
│                                  ▼                                      │
│                         ┌───────────────────┐                           │
│                         │  AGENT EVALUATES  │                           │
│                         │                   │                           │
│                         │  "Illumination is │                           │
│                         │   poor in deep    │                           │
│                         │   section. Add    │                           │
│                         │   sources at far  │                           │
│                         │   offsets."       │                           │
│                         │                   │                           │
│                         └─────────┬─────────┘                           │
│                                   │                                      │
│                                   └──────────────▶ (loop back)          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Visual Elements

1. **Central PDE Block:**
   - Display the wave equation prominently
   - Show JUDI's operator notation: `d = Pr * A_inv * Ps' * q`
   - Include Devito logo/reference

2. **Design Space (Left):**
   - List configurable parameters (θ)
   - Show ranges/constraints

3. **Data Space (Right):**
   - Stylized seismic shot record
   - Time axis (vertical) vs receiver axis (horizontal)

4. **Agent Boxes (Top/Bottom):**
   - Natural language reasoning snippets
   - Show the feedback interpretation

5. **Arrows:**
   - Thick arrows for main data flow
   - Dashed arrows for feedback loop
   - Color-coded by direction (forward = blue, feedback = orange)

### Inset Figures

Include small insets showing:

1. **Velocity model** with source/receiver overlay
2. **Shot gather** (example seismic data)
3. **Illumination map** (coverage visualization)

### Color Scheme

- **Blue:** Physics/PDE components
- **Green:** Agent reasoning
- **Orange:** Data/observations
- **Gray:** Configuration/parameters

## Mathematical Annotations

$$
\text{Forward:} \quad \mathbf{d} = \mathbf{P}_r \mathbf{A}^{-1} \mathbf{P}_s^\top \mathbf{q}
$$

$$
\text{Design Objective:} \quad \boldsymbol{\theta}^* = \arg\max_{\boldsymbol{\theta}} \mathcal{I}(\boldsymbol{\theta})
$$

$$
\text{Agent Policy:} \quad \boldsymbol{\theta}_{k+1} = \pi(\boldsymbol{\theta}_k, \mathbf{d}_k, \text{feedback})
$$

## Suggested Tools

- **Inkscape** for vector graphics with equation support
- **Adobe Illustrator** for professional quality
- **Matplotlib** for programmatic generation with seismic data visualizations

