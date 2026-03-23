# Experiments

## 1. Experimental framing

A practical experiment section for the current repo should evaluate JUDIAgent as a **scientific coding system** rather than a pure numerical inversion engine. The right question is not “does the agent produce the best subsurface image?” The right question is closer to:

- can it produce executable JUDI workflows?
- can it produce scientifically complete workflows for the requested task?
- does domain-aware validation improve output quality over correctness-only validation?

## 2. Candidate evaluation axes

### 2.1 Correctness

Measure whether the generated code:

- passes lint or static checks
- executes successfully
- produces the expected output artifact

### 2.2 Scientific workflow completeness

Use the domain validator to score whether the generated workflow contains the required task ingredients.

### 2.3 Task-aware metric alignment

Check whether the generated workflow exposes the right quality signals for its task family.

Examples:

- RTM: image residual norm, illumination balance
- FWI: objective decrease, gradient update norm
- forward modeling: trace energy consistency, runtime budget

### 2.4 Ablations

The most useful ablations would be:

- no retrieval vs retrieval
- correctness-only validation vs dual validation
- benchmark-task-aware metric guidance vs generic validation feedback
- iterative agent vs autonomous agent

## 3. Benchmark source

The revised `benchmarks/prompts.yaml` is now a good starting point for a benchmark table because each prompt has:

- task category
- required components
- acceptance criteria
- metric bundle

That makes it much easier to report structured results instead of only anecdotal examples.

## 4. Example result table structure

| Task family | Success rate | Runtime pass rate | Domain pass rate | Metric-plan match |
|-------------|--------------|-------------------|------------------|-------------------|
| Forward modeling | ... | ... | ... | ... |
| Imaging | ... | ... | ... | ... |
| Inversion | ... | ... | ... | ... |
| Debugging | ... | ... | ... | ... |

## 5. Strong paper narrative

A strong claim for the current codebase would be:

> Dual validation improves the rate of scientifically complete JUDI workflows relative to correctness-only generation, especially for imaging and inversion tasks.

That is a more grounded and believable experimental claim than anything that would require proving globally optimal survey design.
