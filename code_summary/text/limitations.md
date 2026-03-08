# Limitations

## 5.1 Current Constraints

### 5.1.1 Scope of Experimental Design

JUDIAgent currently focuses on **code generation and workflow automation** rather than **closed-loop optimization** of acquisition parameters. While the agent can:

- Generate acquisition geometries based on natural language specifications
- Validate code through execution
- Adapt configurations based on error feedback

It does **not** currently:

- Optimize source/receiver positions to maximize information-theoretic criteria
- Perform gradient-based design optimization through the wave equation
- Quantify uncertainty in design decisions

The agent assists in *configuring* experiments but does not *optimize* them in the mathematical sense.

### 5.1.2 Computational Overhead

Each agent iteration involves:

| Step | Typical Latency |
|------|-----------------|
| LLM inference | 1-5 seconds |
| RAG retrieval | 0.1-0.5 seconds |
| Julia linting | 5-30 seconds (package loading) |
| Forward modeling | 30-180 seconds (model-dependent) |

The Julia package loading time (particularly for JUDI/Devito) introduces significant latency in the feedback loop. For interactive use, this limits the number of refinement iterations that are practical.

**Mitigation:** JUDI supports precompilation and persistent Julia sessions, which could reduce startup overhead in future versions.

### 5.1.3 LLM Failure Modes

Despite prompt engineering, the LLM exhibits several failure modes:

1. **Syntax confusion:** Mixing Python and Julia syntax, especially for list comprehensions and ranges.

2. **API misuse:** Incorrect parameter types for JUDI constructors (e.g., passing a scalar instead of a tuple for grid dimensions).

3. **Incomplete imports:** Forgetting `using JUDI` or attempting to import individual types as modules.

4. **Hallucinated functions:** Inventing JUDI functions that do not exist.

The code validation pipeline catches many of these errors, but the agent may require multiple iterations to converge on correct code.

### 5.1.4 RAG Limitations

The retrieval system has several limitations:

1. **Fixed corpus:** The vector store is pre-populated with JUDI examples at installation time; it does not dynamically incorporate new examples from user sessions.

2. **Semantic mismatch:** The embedding model may not capture domain-specific semantics accurately, leading to retrieval of irrelevant examples.

3. **Chunking artifacts:** Document splitting may break logical code blocks, reducing the usefulness of retrieved fragments.

### 5.1.5 Scalability

Current limitations on problem scale:

| Dimension | Current Limit | Bottleneck |
|-----------|---------------|------------|
| 2D models | ~500 × 500 grid | RAM for wavefields |
| 3D models | ~200 × 200 × 100 grid | GPU memory |
| Number of sources | ~100 | Execution timeout (180s) |
| Recording time | ~5000 ms | Memory for time samples |

Larger problems require distributed computing or checkpointing, which the agent does not currently configure automatically.

## 5.2 Design Trade-offs

### 5.2.1 Subprocess vs. Embedded Julia

JUDIAgent executes Julia code via subprocess rather than embedded interpreters (e.g., PyJulia, juliacall). This choice has trade-offs:

**Advantages:**
- Process isolation prevents Python-Julia memory conflicts
- Clean error handling via stdout/stderr
- Works with any Julia environment

**Disadvantages:**
- Package loading overhead on each execution
- Cannot share state between calls
- No REPL-style incremental development

### 5.2.2 Validation Strictness

The evaluator-optimizer agent mandates code validation before finalization. This ensures correctness but:

- Increases latency (linting + execution)
- May reject valid code that triggers benign warnings
- Limits "exploration" of partially working code

The autonomous agent relaxes this constraint, trading correctness guarantees for flexibility.

### 5.2.3 Prompt Verbosity

The system prompt is extensive (~3000 tokens) to encode JUDI API conventions. This:

- Consumes context window budget
- May conflict with retrieved examples
- Requires maintenance as JUDI evolves

## 5.3 Known Issues

1. **Linter timeouts:** The Julia linter frequently times out during JUDI package loading, causing the agent to skip static analysis. This is benign for JUDI code but reduces error detection coverage.

2. **CondaPkg noise:** Conda-based Julia installations emit verbose logging to stderr, which the error parser must filter to avoid false positives.

3. **Rate limits:** OpenAI API rate limits can interrupt long agent sessions; exponential backoff is implemented but may delay responses.

4. **MCP stability:** The MCP server integration is experimental and may exhibit connection issues with VSCode.

## 5.4 Out-of-Scope Problems

The following are explicitly outside JUDIAgent's current scope:

1. **Field data processing:** Preprocessing of real seismic data (denoising, deghosting, deconvolution).

2. **Velocity model building:** Initial model construction from well logs or migration velocity analysis.

3. **Time-lapse monitoring:** 4D seismic analysis for reservoir monitoring.

4. **Elastic/anisotropic inversion:** Full elastic or TTI FWI workflows (partial support exists but is not emphasized).

5. **Uncertainty quantification:** Bayesian inversion or posterior sampling.

