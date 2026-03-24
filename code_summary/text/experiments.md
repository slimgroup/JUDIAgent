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


## 6. Concrete case studies from the current repo

Two validated benchmark cases are already strong enough to anchor the first paper draft.

- `basic_2d_forward` provides a complete forward-modeling workflow with saved data, a two-layer setup figure, and a central-shot gather. The shot gather is the stronger scientific result because it shows a clear direct arrival and a weaker later reflection consistent with the layered model.
- `rtm_basic` provides a compact RTM workflow with a true model, a smoother migration model, synthetic observed data, Jacobian-adjoint imaging, a saved imaging artifact, and a saved migrated image figure. The resulting RTM figure is best described as a compact validation result rather than a final high-end migration image, but it is still valuable because it demonstrates that the full imaging path can be generated and validated on a PACE compute node.

For the paper bundle, these cases now have publication-style figure copies under `code_summary/figures/`. In particular, `basic_2d_forward_shot_paper.png` is the clearest forward-modeling result figure, `basic_2d_forward_model_paper.png` is a cleaner setup panel than the earlier benchmark output, and `rtm_basic_image_paper.png` is a display-improved RTM figure generated from the saved imaging artifact without overwriting the original benchmark image.
