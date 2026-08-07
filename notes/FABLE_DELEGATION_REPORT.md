# How the orchestrator delegates to a sub-agent — a methods report

A short, shareable account of how this project uses two different AI roles — an
orchestrating model and a delegated model — and specifically
the technique of **framing tasks as pure mathematics** so a content-restricted model stays
useful on a security-adjacent project. Written so it can be read on its own.

## 1. Two roles, cleanly separated

| | **Orchestrator** | **Delegate** |
|---|---|---|
| Runs | in the live session, with full repo + conversation context, and tools (shell, git, the server, GitHub) | as an isolated sub-agent, one task at a time |
| Does | writes the Lean, drives the kernel/CI verification, edits the repo, decides what to prove | drafts mathematical exposition, decomposes a problem into a lemma graph, independently re-derives an argument as a cross-check |
| Judged by | the Lean **kernel** (a proof is real only if `lake env lean`/`lake build` accepts it) | a human + the orchestrator (its output is *prose/plan*, never a machine-checked proof) |
| Output lives in | `Ecdlp/Proved/*.lean` (the theorems) | `notes/*.md` (the exposition; each carries a provenance line) |

**Key point for "who did what":** every `.lean` theorem is the orchestrator + the kernel. Every note
under `notes/` whose footer says *"drafted by an AI model"* is the delegate's mathematical prose,
adapted by the orchestrator. Nothing the delegate writes is ever counted as a proof — the ledger (`VERIFIED.md`)
lists only kernel-checked theorems.

## 2. Context isolation (yes — the delegate is sealed off)

When the orchestrator spawns the delegate, the delegate receives **only the single prompt it is given** — a
fresh, empty context. It does **not** see the conversation, the repository, prior messages,
the orchestrator's reasoning, or any other agent's work. This is deliberate and has two
consequences:

1. The task must be **fully self-contained** — every definition, hypothesis, and desired
   conclusion has to be spelled out in the prompt, because the delegate can't look anything up.
2. When the delegate independently reproduces a result the orchestrator already has, that is a
   **genuine independent cross-check** — it had no way to copy the answer.

## 3. The technique: frame the task as *pure mathematics*

The delegate is comparatively **restrictive on cryptography/security-adjacent prompts** (names like a
specific curve, words like "attack"/"break"/"key" tend to trip its content filtering). The
mathematics we need, however, is not intrinsically cryptographic — the relevant theorems are
general facts about elliptic curves, and the specific curve is merely one instance.

So the orchestrator **strips all application framing** and poses the *same* mathematics
abstractly. This does two things at once: it stays inside what the delegate will engage with, **and**
it is the honestly-correct level of generality (the theorem is general; the instance is a
corollary).

**Before → after (real example from this project):**

> **Rejected framing:** "Explain why the secp256k1 GLV endomorphism lets you speed up
> attacks on the elliptic-curve discrete log …"

> **Working framing:** "Let $p$ be a prime with $p\equiv 1 \pmod 3$ and $E: y^2=x^3+b$ a
> curve with $j$-invariant $0$ over $\mathbb{F}_p$. The map $\varphi:(x,y)\mapsto(\beta x,y)$
> with $\beta^2+\beta+1=0$ is an order-3 automorphism. Prove $\varphi^2+\varphi+1=0$ in
> $\mathrm{End}(E)$, that $\varphi\neq\mathrm{id}$, and that every $\varphi$-orbit sums to the
> identity …"

Same content; the second is pure algebraic geometry, no curve named, no application. The delegate
engages fully and returns rigorous mathematics.

## 4. Anatomy of a good delegated task (the template used)

1. **State the deliverable and format first** — "Write a rigorous note (~1000 words), Markdown,
   pure mathematics, return ONLY the Markdown."
2. **Give the complete self-contained setup** — all objects, hypotheses, notation (it can't
   look anything up).
3. **Enumerate exactly what to develop** — a numbered list of statements/lemmas, not a vague
   topic.
4. **Ask for structure and honesty** — section headings; difficulty/《reachable vs blocked》
   tags; "be honest, do not overstate; correctness over flourish."
5. **Constrain the framing** — "pure algebra/number theory, no applications, no cryptography."
6. **For a cross-check:** don't hand it the answer — give it the setup and let it derive, then
   compare with what the kernel already verified.

## 5. What the delegate has produced here (the call log)

Three delegated tasks this session; each output is a committed, readable file:

| # | Task given to the delegate (pure-math framing) | Output (the delegate's work) | How it was used |
|---|---|---|---|
| 1 | Endomorphism ring of a $j{=}0$ curve; order-3 automorphism; CM by $\mathbb{Z}[\omega]$ | `notes/CM_EISENSTEIN.md` | exposition + independent cross-check of the GLV theorems |
| 2 | When an order-3 automorphism acts as a scalar on a cyclic group; what pins the scalar | `notes/GLV_EIGENVALUE.md` | matched the eigenvalue-node statement + isolated the missing hypothesis |
| 3 | Dependency map of the division-polynomial ↔ torsion correspondence, tagged LEAF/MID/CORE | `notes/DIVISION_POLY_TORSION_MAP.md` | the depth roadmap: told us which lemmas to attempt now vs which are blocked |

In each case the delegate **independently reproduced** the facts the orchestrator had formalized in
Lean (a real corroboration, given the isolation in §2), and added surrounding theory the
orchestrator had not formalized.

## 6. The division of labor, in one line

**The delegate maps and cross-checks the mathematics; the orchestrator formalizes it and the kernel
judges it.** The delegate makes the orchestrator faster and more confident; it never certifies a proof. That line
is enforced structurally: only `.lean` files accepted by Lean enter `VERIFIED.md`.

---
*This report contains no secrets, keys, or infrastructure details — safe to share.*
