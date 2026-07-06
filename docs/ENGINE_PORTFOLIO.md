# Engine portfolio — "hard-but-short" reasoning challenges

The core product thesis: a **strong model proposes, a machine verifier judges, only truth
survives**. This file tracks challenges given to the strong model (Fable) that have a *short,
explicit answer but require genuine mathematical reasoning to find* — and, for each, an
**independent machine verification** of the answer (never the model's own say-so).

Metric that matters for the product: of the hard problems posed, how many the engine solves
under independent verification.

**Batch 1 result: 8 / 8 hard problems solved and independently verified.** Every answer was
re-checked on our side (a fresh sympy run, or the Lean kernel) — never trusted on the model's
own "I ran it" claim.

| # | Challenge | Model | Verified how | Status |
|---|---|---|---|---|
| 1 | Weil rung W3: Miller function unique up to a unit | Fable | Lean kernel (full CI) | ✅ verified |
| 2 | Multiplication-by-3 `x`-coordinate formula, secp256k1 | Fable | sympy, re-run independently | ✅ verified |
| 3 | Multiplication-by-4 `x`-coordinate formula (double∘double) | Fable | sympy, re-run independently | ✅ verified |
| 4 | Multiplication-by-5 `x`-coordinate formula (via `ψ₄ψ₆/ψ₅²`) | Fable | sympy, re-run independently | ✅ verified |
| 5 | Multiplication-by-6, **two composition orders `[2][3]=[3][2]`** agree | Fable | sympy, re-run independently | ✅ verified |
| 6 | 5- and 7-division polynomials `ψ₅, ψ₇` from the recurrence | Fable | sympy, re-run independently | ✅ verified |
| 7 | Multiplication-by-7 `x`-coordinate (deg 49; completes `n=2..7`) | Fable | sympy, re-run independently | ✅ verified |
| 8 | **No-go certificate**: `E[2]` and `E[3]` `x`-loci disjoint — explicit Bézout `u·(x³+7)+v·ψ₃=1`, `Res=−3⁶·7⁴` | Fable | sympy, re-run independently | ✅ verified |

These build a coherent, kernel-promotable series (the `x([n]P) = Φₙ/ΨSqₙ` multiplication maps
for `n = 2..6` and the odd division polynomials) — engine validation **and** corpus growth in one
batch. Each is a candidate to promote to a Lean theorem.

---

## Challenge 2 — the `[3]P` `x`-coordinate formula for secp256k1

**Problem (hard, short answer).** For `E : y² = x³ + 7`, derive `x([3]P)` as a reduced rational
function of `x` alone (the `y`-dependence must cancel via `y² = x³ + 7`), with an explicit
verification certificate. This requires deriving the division polynomials `ψ₂, ψ₃, ψ₄`, applying
the multiplication formula, and proving the `y`-cancellation and coprimality — real reasoning, but
the answer is two short polynomials.

**Fable's answer.**

```
x([3]P) = N(x) / D(x),   in lowest terms,
  N(x) = x⁹ − 672 x⁶ + 2352 x³ + 21952
  D(x) = 9 x⁸ + 504 x⁵ + 7056 x² = 9 x² (x³ + 28)²
```

with `ψ₂² = 4(x³+7)`, `ψ₃ = 3x⁴ + 84x = 3x(x³+28)`, `ψ₄ = 4y(x⁶ + 140x³ − 392)`, and
`N = x·ψ₃² − 8(x³+7)(x⁶+140x³−392)`, `D = ψ₃²`.

**Independent verification (re-run on our side, NOT trusting the model's claim).** The sympy
certificate below returns `0 / 1 / 0 / 0` on all four checks — the mult-by-3 group-law composite
(tangent-double then chord-add) minus `N/D`, reduced modulo `y² − x³ − 7`, is identically zero;
`gcd(N,D)=1`; `D = ψ₃²`; `N` matches the `ψ₂·ψ₄` form:

```python
import sympy as sp
x, y = sp.symbols('x y')
lam = 3*x**2/(2*y); x2 = lam**2 - 2*x; y2 = lam*(x - x2) - y
mu  = (y2 - y)/(x2 - x); x3 = mu**2 - x - x2
N = x**9 - 672*x**6 + 2352*x**3 + 21952
D = 9*x**8 + 504*x**5 + 7056*x**2
num, _ = sp.fraction(sp.cancel(sp.together(x3 - N/D)))
assert sp.reduced(sp.expand(num), [y**2 - (x**3 + 7)], y, x)[1] == 0     # on-curve identity
assert sp.gcd(sp.Poly(N, x), sp.Poly(D, x)).as_expr() == 1              # lowest terms
assert sp.expand(D - (3*x**4 + 84*x)**2) == 0                           # D = psi3^2
assert sp.expand(N - (x*(3*x**4+84*x)**2 - 8*(x**3+7)*(x**6+140*x**3-392))) == 0
```

**Result: ✅ verified independently.** This is a genuine next result beyond the ledger's
multiplication-by-2 formula (`secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq`), and a candidate to promote to a
kernel-checked Lean theorem (the `n=3` case of `x([n]P) = Φₙ/ΨSqₙ`).

*Honest note:* the identity holds as rational functions, i.e. off the finitely many `x` where
`2P = ±P` or `y = 0` (where `[3]P` hits `O` / the affine formulas degenerate) — exactly what the
polynomial-remainder-zero certificate states.

---

## Batch 1 — new verified results worth recording

The division polynomials `ψ₅, ψ₇` for `y² = x³ + 7` (both re-derived from the standard
recurrence and independently re-checked; roots match order-5 / order-7 points over several
prime fields):

```
ψ₅(x) = 5x¹² + 2660x⁹ − 11760x⁶ − 548800x³ − 614656
ψ₇(x) = 7x²⁴ + 27608x²¹ − 2101904x¹⁸ − 284585728x¹⁵ − 2228742656x¹²
        − 26142548992x⁹ − 330576748544x⁶ − 661153497088x³ + 377801998336
```

The multiplication maps `x([n]P) = N/D` for `n = 3,4,5,6` (all `gcd(N,D)=1`, degrees `n²`) are
recorded in the session and each independently sympy-verified against the group-law composite;
`n=6` additionally confirms `[2]∘[3] = [3]∘[2]`. Candidates for promotion to kernel-checked Lean
theorems (the `n=2` case, `secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq`, is already in the ledger).
