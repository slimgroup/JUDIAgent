# LaTeX Draft Snippets

## Method Section Draft

```tex
\section{Method}
\label{sec:method}

We present JUDIAgent, a JUDI-specific scientific coding agent for seismic modeling, imaging, and inversion workflows. The core idea is that code generation for scientific computing should be validated at two distinct levels. First, the generated Julia must be executable: imports, syntax, and runtime behavior must be consistent with the target JUDI environment. Second, the resulting script must be scientifically adequate for the requested task. In seismic workflows, executable code can still be incomplete if it omits key ingredients such as acquisition geometry, the imaging or inversion objective, or quality-control diagnostics. JUDIAgent therefore combines retrieval-grounded generation with a dual-validation pipeline.

Given a natural-language request, the agent first retrieves relevant JUDI documentation and example workflows. This retrieval step grounds generation in the actual operator vocabulary and reduces hallucinated API usage. The model then generates a candidate Julia workflow, which is passed to a correctness validator. This stage performs lightweight preprocessing, static checks, and runtime validation. Only candidates that survive executable correctness checks are passed to the second stage, a domain-quality reviewer that evaluates whether the workflow contains the ingredients expected for the inferred task family.

The domain-quality reviewer is task-aware. For example, migration-oriented prompts are expected to expose model setup, acquisition geometry, imaging operators, and image-oriented diagnostics, whereas inversion-oriented prompts are expected to distinguish observed data from the starting model, define an objective or misfit, and expose an optimization or update loop. The domain review also attaches a lightweight metric bundle to each task family. Typical examples include image residual norm and illumination balance for migration tasks, and objective decrease and gradient update norm for FWI tasks. These metrics provide structured guidance for iterative repair and create a bridge to future benchmark design, supervised fine-tuning, and reward modeling.

JUDIAgent supports two execution modes. The first is an iterative validated agent aimed at focused code-generation tasks, where the output should be a validated JUDI workflow. The second is an autonomous ReAct-style agent that can perform open-ended tool use over retrieval, execution, linting, shell interaction, and file operations. In this paper, we emphasize the iterative validated path because it gives the clearest scientific guarantee: code is not only executable, but also reviewed for workflow completeness in the seismic domain.
```

## Contributions Draft

```tex
\paragraph{Contributions.}
This work makes four main contributions. First, we introduce JUDIAgent as a JUDI-specific scientific coding agent for seismic workflows rather than a generic programming assistant. Second, we propose a dual-validation architecture that separates executable correctness from scientific workflow adequacy. Third, we design a domain-quality review stage that checks whether generated code contains the expected ingredients of modeling, migration, and inversion workflows. Fourth, we attach task-aware metric guidance to generated workflows, creating a practical foundation for benchmark design and future learning-based supervision.
```

## Experiments Section Draft

```tex
\section{Experiments}
\label{sec:experiments}

Our experiments evaluate JUDIAgent as a scientific coding system rather than as a standalone numerical inversion solver. The primary question is not whether the agent directly produces the best possible seismic image, but whether it can produce executable and scientifically complete JUDI workflows for representative task families.

We organize evaluation around three axes. The first is executable correctness, measured by whether generated code passes static checks, runtime validation, and expected artifact production. The second is scientific workflow completeness, measured by the domain validator and benchmark acceptance criteria. The third is task-aware metric alignment, measured by whether the generated workflow exposes the diagnostics or evaluation hooks expected for its task family, such as image residual and illumination balance for migration or objective decrease and gradient update norm for inversion.

We also recommend ablations that isolate the impact of the main architectural choices: retrieval versus no retrieval, correctness-only validation versus dual validation, and generic repair feedback versus task-aware metric guidance. The benchmark prompt catalog used in our study includes required components, acceptance criteria, and task-specific metric bundles, which enables structured evaluation beyond anecdotal examples. A central hypothesis for the present codebase is that dual validation improves the rate of scientifically complete JUDI workflows relative to correctness-only generation, especially for imaging and inversion tasks.

As concrete examples, the current repo already contains two validated benchmark case studies that are suitable for qualitative analysis. The first is a 2D forward-modeling case that produces a saved synthetic dataset, a layered-velocity setup panel, and a central-shot gather with physically plausible direct and reflected arrivals. The second is a compact RTM case that produces a saved imaging artifact and a migrated image from a true model, a smoother migration model, and synthetic observed data. In both cases, the benchmark outputs were preserved, and separate paper-style figure copies were generated for the manuscript under `code_summary/figures/`. These cases support the claim that the agent is capable of generating not only executable Julia scripts, but scientifically structured workflows with reusable artifacts for later inspection and reporting.
```
