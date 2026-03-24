# LaTeX Draft Snippets

## Abstract Draft

```tex
\begin{abstract}
We present JUDIAgent, a domain-grounded scientific coding agent for JUDI.jl workflows in seismic modeling, imaging, and inversion. Unlike generic code assistants, JUDIAgent is designed for a setting in which executable code is not enough: a usable seismic script must also encode a scientifically coherent workflow, including model construction, acquisition geometry, operator composition, and task-appropriate diagnostics or artifacts. JUDIAgent therefore combines retrieval-augmented generation with a dual-validation pipeline that separates software correctness from seismic workflow adequacy.

Given a natural-language request, the agent retrieves relevant JUDI documentation and examples, generates candidate Julia code, and validates it in two stages. The first stage checks executable correctness through preprocessing, static analysis when feasible, and runtime validation in the target Julia environment. The second stage performs a domain-quality review that asks whether the generated script is scientifically complete for the inferred task family. The framework also attaches task-aware metric guidance, such as trace-energy consistency for forward modeling and image residual or illumination balance for migration, creating a bridge between interactive repair, benchmark design, and future learning-based supervision.

We demonstrate the approach with validated case studies in 2D forward modeling and compact RTM on a PACE compute environment. These results show that JUDIAgent can produce not only runnable Julia scripts, but reusable scientific artifacts and publication-ready figures for representative JUDI workflows. We argue that retrieval grounding, dual validation, and metric-aware repair provide a practical foundation for benchmark-driven evaluation and future SFT or RLHF for scientific coding agents in computational geophysics.
\end{abstract}
```

## Introduction Draft

```tex
\section{Introduction}
\label{sec:introduction}

Wave-equation-based seismic computing is an unusually demanding target for coding assistance. In this setting, syntactically correct code is often still unusable if it omits the model parameterization, acquisition geometry, source description, operator composition, or diagnostics required by the intended scientific task. Many important failure cases are therefore not parser failures or import errors. Instead, code may execute while still being scientifically incomplete, misleading, or insufficient for modeling, migration, or inversion.

JUDI.jl provides a powerful abstraction layer for seismic computing in Julia, but effective use of JUDI still requires familiarity with workflow structure. Users must know how to construct physical models, define source and receiver geometries, assemble forward and Jacobian operators, manage units, and generate interpretable artifacts. Large language models can help with this process, but naive prompting is not enough. Domain-specific APIs are easy to misuse, Julia syntax can be confused with Python syntax, and superficially plausible code can still omit essential workflow ingredients such as the migration model, the inversion objective, or quality-control outputs.

The goal of JUDIAgent is not simply to autocomplete Julia code. The goal is to translate natural-language requests into workflows that are both executable and scientifically adequate. This motivates a scientific coding agent rather than a generic coding assistant. JUDIAgent addresses the problem with three linked design choices: retrieval-grounded generation from JUDI documentation and examples, dual validation that separates executable correctness from domain adequacy, and task-aware metric guidance that exposes meaningful quality signals for different workflow families.

Our central claim is modest but important. We do not claim that JUDIAgent produces globally optimal seismic images or replaces numerical expertise. Instead, we claim that it improves the reliability of code generation for JUDI workflows in a domain where executable correctness alone is insufficient. This framing is supported by validated case studies in forward modeling and compact RTM, where the agent produced runnable workflows, saved scientific artifacts, and publication-style figures suitable for qualitative analysis.
```

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

As concrete examples, the current repo already contains two validated benchmark case studies that are suitable for qualitative analysis. The first is a 2D forward-modeling case that produces a saved synthetic dataset, a layered-velocity setup panel, and a central-shot gather with physically plausible direct and reflected arrivals. The second is a compact RTM case that produces a saved imaging artifact and a migrated image from a true model, a smoother migration model, and synthetic observed data. In both cases, the benchmark outputs were preserved, and separate paper-style figure copies were generated for the manuscript under \texttt{code\_summary/figures/}. These cases support the claim that the agent is capable of generating not only executable Julia scripts, but scientifically structured workflows with reusable artifacts for later inspection and reporting.
```

## Discussion / Limitations Draft

```tex
\section{Discussion and Limitations}
\label{sec:discussion}

The current results are promising, but they should be interpreted carefully. JUDIAgent is strongest today on validation-scale workflows, where the goal is to generate executable and scientifically structured scripts rather than state-of-the-art subsurface images. This distinction matters most for imaging tasks. For example, the compact RTM benchmark demonstrates that the full imaging chain can be assembled and validated, but the resulting image should be interpreted as a proof-of-capability artifact rather than a competitive migration result.

Another limitation is that figure quality is partly data-dependent. Prompt engineering and plotting defaults can improve consistency, but some display choices such as clipping strength or shallow-depth cropping remain dependent on the actual generated artifact. We therefore view paper-style redraw from saved artifacts as a practical and reproducible final presentation step rather than a failure of the generation process.

Finally, the current evaluation remains small-scale and qualitative. A natural next step is to run the full benchmark prompt catalog across multiple models, compare correctness-only and dual-validation settings, and measure not just execution success but structured workflow completeness.
```

## Conclusion Draft

```tex
\section{Conclusion}
\label{sec:conclusion}

JUDIAgent reframes LLM-based code generation for computational geophysics as a scientific workflow generation problem rather than a pure syntax or API-completion task. By combining retrieval-grounded generation, executable correctness checks, domain-quality review, and task-aware metric guidance, the system can produce JUDI workflows that are more structured, inspectable, and reusable than what correctness-only prompting would typically provide. The validated forward-modeling and compact RTM case studies in the current repo provide concrete evidence that this approach is practical today and can serve as a foundation for future benchmark-driven evaluation, supervised fine-tuning, and reward-model design for scientific coding agents.
```
