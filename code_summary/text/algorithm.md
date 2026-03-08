# Algorithm

## 3.1 High-Level Workflow

The JUDIAgent workflow can be expressed as the following algorithm:

---

**Algorithm 1: JUDIAgent Workflow**

---

**Input:** User task description $\tau$, maximum iterations $K$, configuration $\mathcal{C}$

**Output:** Validated Julia code $\texttt{code}^*$ or error report

---

1. Initialize state $\mathcal{S}_0 \leftarrow \{\texttt{messages}: [\tau], \texttt{error}: \texttt{False}, \texttt{iter}: 0\}$
2. **while** $\mathcal{S}.\texttt{iter} < K$ **and not** converged **do**
3. $\quad$ // **Reasoning Phase**
4. $\quad$ $\texttt{response} \leftarrow \text{LLM}(\mathcal{S}.\texttt{messages}, \text{prompt}, \text{tools})$
5. $\quad$ **if** $\texttt{response}$ contains tool calls **then**
6. $\quad\quad$ **for each** tool call $(\texttt{name}, \texttt{args})$ **in** $\texttt{response}$ **do**
7. $\quad\quad\quad$ $\texttt{result} \leftarrow \text{execute\_tool}(\texttt{name}, \texttt{args})$
8. $\quad\quad\quad$ Append $\texttt{result}$ to $\mathcal{S}.\texttt{messages}$
9. $\quad\quad$ **end for**
10. $\quad$ **else**
11. $\quad\quad$ Extract $\texttt{code}$ from $\texttt{response}$
12. $\quad\quad$ // **Validation Phase**
13. $\quad\quad$ $\texttt{lint\_result} \leftarrow \text{run\_linter}(\texttt{code})$
14. $\quad\quad$ $\texttt{exec\_result} \leftarrow \text{run\_julia}(\texttt{code})$
15. $\quad\quad$ **if** $\texttt{lint\_result}.\texttt{ok}$ **and** $\texttt{exec\_result}.\texttt{ok}$ **then**
16. $\quad\quad\quad$ **return** $\texttt{code}$ // Success
17. $\quad\quad$ **else**
18. $\quad\quad\quad$ Append error feedback to $\mathcal{S}.\texttt{messages}$
19. $\quad\quad\quad$ $\mathcal{S}.\texttt{error} \leftarrow \texttt{True}$
20. $\quad\quad$ **end if**
21. $\quad$ **end if**
22. $\quad$ $\mathcal{S}.\texttt{iter} \leftarrow \mathcal{S}.\texttt{iter} + 1$
23. **end while**
24. **return** error report

---

## 3.2 Retrieval-Augmented Generation (RAG)

The RAG subsystem enables the agent to ground its code generation in concrete examples from the JUDI documentation.

---

**Algorithm 2: RAG-Based Example Retrieval**

---

**Input:** Query string $q$, vector store $\mathcal{V}$, search parameters $(k, \lambda)$

**Output:** Retrieved documents $\mathcal{D}$

---

1. Embed query: $\mathbf{e}_q \leftarrow \text{embed}(q)$
2. Retrieve candidates: $\mathcal{C} \leftarrow \text{top-}k\text{-similarity}(\mathbf{e}_q, \mathcal{V})$
3. **if** using MMR (Maximal Marginal Relevance) **then**
4. $\quad$ $\mathcal{D} \leftarrow \emptyset$
5. $\quad$ **while** $|\mathcal{D}| < k$ **do**
6. $\quad\quad$ $d^* \leftarrow \arg\max_{d \in \mathcal{C} \setminus \mathcal{D}} \left[ \lambda \cdot \text{sim}(\mathbf{e}_q, \mathbf{e}_d) - (1-\lambda) \cdot \max_{d' \in \mathcal{D}} \text{sim}(\mathbf{e}_d, \mathbf{e}_{d'}) \right]$
7. $\quad\quad$ $\mathcal{D} \leftarrow \mathcal{D} \cup \{d^*\}$
8. $\quad$ **end while**
9. **else**
10. $\quad$ $\mathcal{D} \leftarrow \mathcal{C}$
11. **end if**
12. **return** $\mathcal{D}$

---

The vector store is pre-populated with:
- **JUDI.jl examples:** ~50 annotated Julia scripts covering modeling, RTM, FWI, extended sources, etc.
- **Documentation:** Markdown files explaining data structures, linear operators, and inversion methods.

Embeddings are computed using OpenAI's `text-embedding-3-small` (or local models via Ollama).

## 3.3 Code Validation Pipeline

The validation pipeline ensures generated code is syntactically correct and executes without runtime errors.

---

**Algorithm 3: Code Validation**

---

**Input:** Julia code string $\texttt{code}$

**Output:** $(\texttt{success}, \texttt{error\_message})$

---

1. // **Preprocessing**
2. $\texttt{code} \leftarrow \text{fix\_imports}(\texttt{code})$ // Add missing `using JUDI`
3. $\texttt{code} \leftarrow \text{shorten\_simulations}(\texttt{code})$ // Reduce runtime for testing

4. // **Static Analysis**
5. $(\texttt{stdout}, \texttt{stderr}) \leftarrow \text{julia\_lint}(\texttt{code})$
6. **if** $\texttt{stderr}$ contains errors **then**
7. $\quad$ **return** $(\texttt{False}, \texttt{stderr})$
8. **end if**

9. // **Execution**
10. $\texttt{result} \leftarrow \text{julia\_run}(\texttt{code}, \texttt{timeout}=180\text{s})$
11. **if** $\texttt{result}.\texttt{error}$ **then**
12. $\quad$ $\texttt{msg} \leftarrow \text{format\_error}(\texttt{result}.\texttt{stderr})$
13. $\quad$ **return** $(\texttt{False}, \texttt{msg})$
14. **end if**
15. **return** $(\texttt{True}, \texttt{result}.\texttt{stdout})$

---

## 3.4 State Transition Diagram

The agent's execution follows a state machine with the following transitions:

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
                    v                                         │
┌────────────┐    ┌─────────┐    ┌───────┐    ┌──────────┐   │
│ User Input │───>│  Agent  │───>│ Tools │───>│  Agent   │───┘
└────────────┘    │ (call   │    │(RAG,  │    │(continue)│
                  │  model) │    │ lint, │    └──────────┘
                  └─────────┘    │ run)  │          │
                       │         └───────┘          │
                       │                            │
                       v                            v
                  ┌──────────┐              ┌───────────┐
                  │Check Code│─── error ───>│  Agent    │
                  │(validate)│              │ (fix err) │
                  └──────────┘              └───────────┘
                       │
                       │ success
                       v
                  ┌──────────┐
                  │ Finalize │───> Output validated code
                  └──────────┘
```

## 3.5 Prompt Engineering

The agent prompt encodes domain-specific knowledge critical for JUDI.jl code generation:

### 3.5.1 API Conventions

```
Model(n, d, o, m) - Create model with:
  - n: Tuple of Int64 (grid size)
  - d: Tuple of Float64 (spacing)
  - o: Tuple of Float64 (origin)
  - m: Array (squared slowness)

Geometry(x, y, z; dt, t, nsrc) - Acquisition geometry
judiVector(geometry, wavelet) - Source/data vector
judiModeling(model) - Forward modeling operator
```

### 3.5.2 Common Pitfalls

The prompt explicitly warns against:
- Using Python syntax (`range(10)` → `1:10`)
- Importing types as modules (`using Geometry` → `using JUDI`)
- Creating arrays of Model objects (incorrect JUDI pattern)

### 3.5.3 Workflow Strategy

```
1. ANALYZE: Break down requirements
2. RETRIEVE: Query examples BEFORE coding
3. GENERATE: Write Julia code
4. VALIDATE: Run linter + execution
5. ITERATE: Fix errors with retrieved context
```

## 3.6 Complexity Analysis

| Component | Complexity |
|-----------|------------|
| LLM inference | $O(\text{context\_length}^2)$ per token |
| RAG retrieval | $O(N \log N)$ for approximate nearest neighbor |
| Julia linting | $O(|\texttt{code}|)$ |
| Forward modeling | $O(N_x N_z N_t)$ for 2D |
| Adjoint computation | $O(N_x N_z N_t)$ |

The overall runtime is dominated by Julia execution (forward modeling), which scales linearly with model size and recording time.

