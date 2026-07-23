# P0 — GLV-symmetrized Semaev index calculus (`HYP_GLV_SEMAEV_001`)

Reproducible experiment package for the project's best *coherent* cryptanalytic bet. **Read the
honest prior first:** the expected outcome is a **negative / no-go** result. This is run as an
experiment through the truth substrate — to test the best available math lead *and* to build the
experiment-ledger machinery — **not** as an expected break of secp256k1. Breaking the curve is a
low-odds lottery ticket, not the goal; a rigorous negative result is a real, publishable output.

**Current status:** `RESULTS.md` contains a partial negative result for direct `m=2`
pair enumeration and GLV-orbit dictionary keys. It does not test the central
degree-of-regularity / Gröbner-solving claim below. The question remains open, but the
hypothesis remains parked after repository decision `RS-2026-07-22-001`
selected no route.

## The idea (one paragraph)

secp256k1 has `j = 0`, CM by the Eisenstein order `ℤ[ζ₃]`, and the order-3 automorphism
`φ(x,y) = (βx, y)` with `β³ = 1` (its eigenvalue `λ` on `⟨G⟩` is machine-checked here). Because
`φ` fixes `y` and `(βx)³ = x³`, both `y` and `u = x³` are `φ`-invariant. A Semaev factor base in
`x` already identifies `P` and `−P`; closing it under the GLV orbit (size 3) and rewriting the
`Sₘ = 0` relation systems in the invariants `u = x³` (or `y`) collapses each orbit of ~6 points to
one factor-base element. The **question** is whether the invariant coordinates do more than shrink
the base by a constant `3×–6×`: whether they lower the **degree of regularity**, shrink the Gröbner
matrices, raise the decomposition probability, or change the **asymptotics** of relation generation.

## Honest prior art (this is NOT claimed new in general)

- **Gaudry (2009), Diem (2011), Semaev (2004)** — index calculus for ECDLP via summation
  polynomials; **subexponential only over extension fields `𝔽_{pⁿ}`, n > 1** (Weil restriction).
- **Faugère, Gaudry, Huot, Renault**, *Using symmetries in the index calculus for elliptic curves
  discrete logarithm* — symmetry-adapted / quasi-homogeneous systems give real gains **over
  extension fields**. Directly relevant technique; **not** a prime-field result.
- **Petit et al.**, *Faster Algorithms for the ECDLP in the Large Characteristic Case* — composed
  low-degree rational maps for relation generation; the central open difficulty is exactly
  prime-field relation generation.
- GLV-invariant factor bases for `j = 0` curves have been considered in the extension-field
  attack literature.

**What could be genuinely new (and must be proven, not assumed):** the precise prime-field /
secp256k1 specialization — invariant-coordinate (`u = x³`, `y`) relation generation for `j = 0`
curves — *with a rigorous cost/scaling analysis*. Everything else is prior art and is cited as such.

## Why the prior is low (the obstruction)

The prime-field barrier is **relation generation**, not factor-base size. GLV orbit size 3 gives at
most a `~6×` base reduction — a **constant factor**. A breakthrough requires the invariants to
change the *asymptotic* relation-generation behaviour, which symmetrization alone has no known
reason to do over a prime field. That is the open, unlikely part.

## Experimental protocol (`HYP_GLV_SEMAEV_001` tests)

Family: `E_b : y² = x³ + b` over primes `p ≡ 1 (mod 3)` with a large prime subgroup (`toy_curves.py`).

Four variants, each measured across several sizes of `p`:
1. **plain** — standard Semaev `Sₘ` factor base in `x`.
2. **glv-base** — factor base reduced by GLV orbits (`x`, `βx`, `β²x`) and `±`.
3. **invariant** — `Sₘ` systems rewritten in `u = x³` (and/or `y`).
4. **petit** — planned: variant 3 plus a faithful Petit composed low-degree rational map.
   The existing `variant_petit.py` is only an integer-bit-filter control and is explicitly
   not evidence for or against Petit's algebraic construction.

Metrics per run: relation probability, factor-base size, `#relations` needed, **degree of
regularity**, max Gröbner matrix size, wall time, peak memory, and the empirical growth exponent
in `p`. Every run is recorded by `manifest.py` (code hash + seed + params + tool versions + output
hash) so results are reproducible and comparable.

## Decision criteria (from the hypothesis registry)

- **BREAKTHROUGH** (→ continue, then move identities to Lean): a *stable* `T(p) = p^{1/2 − ε}`,
  `ε > 0`, **with a theoretical explanation** of the scaling.
- **CLOSE as no-go** if: the speedup vanishes after precomputation; it is only a constant factor;
  the observed scaling exponent does not improve; or gains appear only on hand-picked singular
  curves. → a benchmark note + a `BARRIERS.md` / no-go entry.

Lean formalization happens **only** on a positive, explained result (never before).

## Tooling

Needs a real computational-algebra stack (finite-field linear algebra + Gröbner): `python-flint`
and `galois` (being provisioned), and/or a Gröbner engine (`msolve`) or SageMath on the server. The
first pipeline increment runs on genuinely small `p` with `sympy` to validate the harness end to
end; scaling runs need the faster stack. Untrusted-model code is **not** involved — this is our own
deterministic code, run manually (see `notes/EXECUTION_SECURITY.md`).

## Files

- `toy_curves.py` — the `j = 0` toy-curve family (prime `p ≡ 1 mod 3`, large prime subgroup, a
  generator, and the GLV endomorphism `β`).
- `manifest.py` — experiment-manifest helper (deterministic provenance record per run).
- `runs/` — output manifests + metrics (created by experiment runs).
