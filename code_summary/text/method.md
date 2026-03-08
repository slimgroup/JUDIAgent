# Method

## 2.1 Problem Formulation

### 2.1.1 The Forward Problem

Let $\Omega \subset \mathbb{R}^d$ ($d \in \{2, 3\}$) denote the computational domain with boundary $\partial\Omega$. The acoustic wave equation governs pressure wavefield propagation:

$$
\frac{1}{c^2(\mathbf{x})} \frac{\partial^2 u}{\partial t^2} - \nabla^2 u = q(\mathbf{x}, t), \quad \mathbf{x} \in \Omega, \, t \in [0, T]
$$

where $u(\mathbf{x}, t)$ is the pressure field, $c(\mathbf{x})$ is the spatially varying sound speed, and $q(\mathbf{x}, t)$ represents the source term. JUDI expresses this forward map abstractly as:

$$
\mathbf{d} = \mathbf{P}_r \mathbf{A}^{-1} \mathbf{P}_s^{\top} \mathbf{q}
$$

where:
- $\mathbf{A}$ is the discretized wave equation operator
- $\mathbf{P}_s$ is the source injection operator (projecting sources onto the grid)
- $\mathbf{P}_r$ is the receiver sampling operator (extracting data at receiver locations)
- $\mathbf{q}$ is the source wavelet vector
- $\mathbf{d}$ is the recorded seismic data

### 2.1.2 The Inverse Problem

Given observed data $\mathbf{d}_{\text{obs}}$, the inverse problem seeks model parameters $\mathbf{m} = 1/c^2$ (squared slowness) minimizing a misfit functional:

$$
\min_{\mathbf{m}} \mathcal{J}(\mathbf{m}) = \frac{1}{2} \| \mathbf{F}(\mathbf{m}) - \mathbf{d}_{\text{obs}} \|_2^2 + \mathcal{R}(\mathbf{m})
$$

where $\mathbf{F}(\mathbf{m})$ is the forward operator (implicitly depending on the acquisition geometry) and $\mathcal{R}$ is a regularization term.

### 2.1.3 The Experimental Design Problem

Let $\boldsymbol{\theta} \in \Theta$ denote the acquisition design variables:

$$
\boldsymbol{\theta} = (\mathbf{x}_s^{(1)}, \ldots, \mathbf{x}_s^{(N_s)}, \mathbf{x}_r^{(1)}, \ldots, \mathbf{x}_r^{(N_r)}, \Delta t, T, f_0, \ldots)
$$

including source positions $\mathbf{x}_s^{(i)}$, receiver positions $\mathbf{x}_r^{(j)}$, sampling interval $\Delta t$, recording time $T$, and wavelet parameters (e.g., peak frequency $f_0$).

An ideal experimental design maximizes the "informativeness" of the resulting data:

$$
\boldsymbol{\theta}^* = \arg\max_{\boldsymbol{\theta} \in \Theta} \mathcal{I}(\boldsymbol{\theta})
$$

where $\mathcal{I}$ might measure Fisher information, illumination coverage, or image resolution. This optimization is intractable via gradient methods due to the discrete, combinatorial nature of many design variables and the expense of each function evaluation.

## 2.2 Agent-Based Reformulation

Instead of solving the above optimization directly, JUDIAgent reformulates experimental design as an **interactive decision-making problem**. The agent operates in a loop:

1. **Observation:** Receive a task description (natural language) and system state.
2. **Reasoning:** Plan the next action based on retrieved knowledge and prior context.
3. **Action:** Generate code, retrieve documentation, or request clarification.
4. **Feedback:** Observe execution results (success, error, runtime diagnostics).
5. **Adaptation:** Refine the approach based on feedback.

### 2.2.1 State Space

The agent's state $\mathcal{S}$ includes:

- **Message history:** Prior user queries, agent responses, and tool outputs.
- **Code block:** Currently generated Julia code (imports + main body).
- **Error flag:** Whether the last execution encountered an error.
- **Iteration count:** Number of refinement cycles.
- **Retrieved context:** Documentation and examples from RAG.

### 2.2.2 Action Space

The agent can invoke the following tools:

| Tool | Description |
|------|-------------|
| `retrieve_judi_examples` | Semantic search over JUDI.jl code examples |
| `retrieve_function_documentation` | Look up function signatures |
| `run_julia_code` | Execute Julia code and return output/errors |
| `run_julia_linter` | Static analysis for syntax/type errors |
| `read_from_file` / `write_to_file` | File I/O operations |
| `grep_search` | Pattern-based search in documentation |
| `execute_terminal_command` | Run shell commands |

### 2.2.3 Policy

The agent's policy $\pi$ is implemented via a large language model (GPT-4.1 or local models via Ollama) guided by a system prompt that encodes:

- JUDI.jl API conventions (Model, Geometry, judiVector, judiModeling)
- Julia syntax rules (distinguishing from Python)
- Workflow strategy (analyze → retrieve → generate → validate → refine)

The prompt emphasizes **retrieval before generation**: the agent must query `retrieve_judi_examples` before writing any JUDI code to ensure correct API usage.

## 2.3 Two-Agent Architecture

JUDIAgent provides two agent variants optimized for different use cases:

### 2.3.1 Evaluator-Optimizer Agent

The simpler agent follows an **evaluator-optimizer** pattern:

1. **Generate:** Produce Julia code based on the task.
2. **Evaluate:** Run linter and code execution.
3. **Optimize:** If errors occur, feed them back to the LLM for correction.
4. **Finalize:** Upon success, return the validated code.

This agent is suitable for well-defined tasks (e.g., "set up a 2D simulation with 10 sources").

### 2.3.2 Autonomous Agent

The autonomous agent has additional capabilities:

- Terminal command execution
- More sophisticated tool chaining
- Proactive exploration of the codebase

This agent operates in a more "Copilot-like" mode, suitable for complex, open-ended tasks requiring multi-step exploration.

## 2.4 Integration with JUDI

JUDI provides high-level linear operator abstractions that JUDIAgent leverages:

```
┌─────────────────────────────────────────────────────────────┐
│                     JUDI Abstractions                        │
├─────────────────────────────────────────────────────────────┤
│  Model(n, d, o, m)        →  Physical model (grid + slowness)│
│  Geometry(x, y, z; dt, t) →  Source/receiver positions       │
│  judiVector(geom, wavelet)→  Source/data containers          │
│  judiModeling(model)      →  Forward wave equation operator  │
│  judiProjection(geom)     →  Source/receiver projection      │
│  judiJacobian(F, q)       →  Linearized (Born) operator      │
└─────────────────────────────────────────────────────────────┘
```

The agent generates code that composes these operators:

```julia
# Example generated code
d_obs = Pr * F * Ps' * q   # Forward modeling
rtm = J' * d_obs           # Reverse-time migration
grad = fwi_objective(m, q, d_obs)  # FWI gradient
```

This operator algebra maps directly to the mathematical formulation, enabling the agent to produce readable, mathematically grounded code.

