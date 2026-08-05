# The Riemann Hypothesis, in plain language

Status: **informal, non-normative**. This file explains the research target
for readers outside analytic number theory. Nothing here is a contract, a
claim, or evidence; the normative documents are `README.md`, `corpus.md`,
`MATHLIB_CAPABILITY_MAP.md`, `SOURCE_CONTRACTS.md`, `ROUTE_TRIAGE.md`, and
`TARGET_BRIDGE_CONTRACT.md`.

## What the conjecture says

The Riemann zeta function starts as the infinite sum
`ζ(s) = 1 + 1/2^s + 1/3^s + …`, which converges when `re(s) > 1`, and
extends uniquely to an analytic function on the whole complex plane except
`s = 1`. Euler's product formula `ζ(s) = Π_p (1 − p^(−s))^(−1)` ties it to
the prime numbers: the zeta function is an analytic encoding of how primes
are distributed.

The extended function is zero at `−2, −4, −6, …` (the "trivial zeros") and
at infinitely many other points, all of which are known to lie in the
vertical strip `0 < re(s) < 1`. The Riemann Hypothesis (1859) says: **every
one of those nontrivial zeros lies exactly on the middle line
`re(s) = 1/2`.** Through Riemann's explicit formula, each zero contributes
an oscillating term to the prime-counting error; RH is exactly the
statement that the primes are distributed as regularly as possible — the
error term in the Prime Number Theorem is essentially square-root sized.

It is one of the seven Clay Millennium Prize Problems (`RH-SRC-001`). It has
been verified for the first 3·10¹² zeros (`RH-SRC-007`), but no finite
computation can prove a statement about infinitely many zeros.

## Why it is hard

The zeta function's zeros are controlled by delicate cancellation in an
infinite oscillating sum. Every known reformulation (positivity of the Li
coefficients, the Nyman-Beurling approximation criterion, Weil's
explicit-formula positivity) is an exact equivalence: proving any of them
in full is exactly as hard as RH itself. A century and a half of partial
results (zero-free regions, zero-density estimates, "at least 41% of zeros
on the line") all stop structurally short of excluding even one hypothetical
off-line zero at large height. This repository's route triage
(`ROUTE_TRIAGE.md`) records, with sources, why each admitted attack route's
success criterion is currently unreachable short of RH itself.

## How long would a proof be?

Nobody knows, because nobody has one. Known proofs of comparable statements
give the range: the function-field analogue of RH (Weil 1948; Deligne 1974)
took decades of new algebraic geometry — the machinery filled books, though
the final papers were tens of pages. Some famous problems ended with short
conceptual keys once the right idea existed; others (classification-style
results) run to hundreds of pages. What this repository controls is not the
length but the **checkability**: any candidate argument here must be
formalized in Lean and accepted by the kernel, so a proof's prose length is
irrelevant — its formal dependency graph is the real object.

## What this repository is actually doing

Not claiming a proof. The honest, machine-checked path is:

1. freeze the exact formal statement (done — Mathlib's `RiemannHypothesis`);
2. map exactly which foundations exist and which are missing (done,
   independently replayed — `MATHLIB_CAPABILITY_MAP.md`);
3. adversarially triage the attack routes with preregistered success bars
   (done — all currently `PARK`ed, honestly);
4. build the missing kernel-checked foundations in dependency order,
   starting with the route-neutral bridge between the formal target and the
   classical formulations (contract frozen — `TARGET_BRIDGE_CONTRACT.md`);
5. re-open a route only when a genuinely new mechanism appears — with the
   preregistered bars deciding, not enthusiasm.

Every model-generated argument is a draft only; the Lean kernel is the sole
judge. A verified equivalence or foundation is progress in *formal
readiness*, and is never counted as progress on the truth of RH.
