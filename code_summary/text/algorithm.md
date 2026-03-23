# Algorithm

## Algorithm 1: Iterative JUDIAgent validation loop

**Input:** user request `q`, configuration `C`, iteration budget `K`

**Output:** validated Julia workflow or structured failure report

1. Initialize graph state with the user request and empty code artifact.
2. Retrieve relevant JUDI examples, documentation, and local code context.
3. Ask the LLM to generate Julia code conditioned on the retrieved context.
4. Extract the candidate Julia block from the model response.
5. If human pre-check is enabled, let the user accept, edit, or reject the candidate before validation.
6. Run correctness validation:
   - normalize imports and lightweight execution settings
   - run lint/static checks
   - run runtime execution checks
7. If correctness validation fails, attach diagnostics to the message history and return to Step 3.
8. If correctness validation succeeds, run domain-quality review.
9. Score whether the workflow includes the expected scientific components for the inferred or benchmark-specified task family.
10. Attach task-aware metric guidance to the review report.
11. If the domain review fails, return structured findings to the LLM and go back to Step 3.
12. Otherwise, return the validated workflow.

## Algorithm 2: Domain-quality review

**Input:** Julia code block `x`, optional benchmark task identifier `t`

**Output:** domain score, findings, metric plan

1. Determine whether domain review is active based on configuration.
2. Infer the workflow family from the code and task context, unless a benchmark task ID is already given.
3. Check for required scientific components such as model setup, geometry, operators, objectives, and diagnostics.
4. Compute a lightweight scientific-readiness score.
5. Query the metric planner for a task-aware metric bundle.
6. If the score is below threshold, emit a `domain_quality` finding and recommended metrics.
7. Otherwise, return a passing domain assessment.

## Algorithm 3: Autonomous ReAct loop

**Input:** user goal `g`, tool set `T`, stop condition `S`

**Output:** final answer, code artifact, or tool-grounded explanation

1. Initialize the conversation state with the user goal.
2. Ask the LLM to reason about the next step.
3. If the model requests tools, execute the requested tool calls.
4. Append tool outputs to the state.
5. Ask the LLM to observe the results and decide the next action.
6. Repeat until the stop condition is met.
7. Return the final answer.

## Interpretation

The iterative agent emphasizes validated code delivery. The autonomous agent emphasizes flexible tool use. Together they form a two-mode system: one for strict scientific code generation and one for broader interactive assistance.
