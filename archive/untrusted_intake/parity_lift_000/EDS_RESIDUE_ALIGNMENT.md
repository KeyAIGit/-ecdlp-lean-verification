# EDS-RESIDUE-ALIGNMENT-001

Date: 2026-08-11

Status: **untrusted source alignment, correction candidate, and public-parameter
verification**. This file is quarantined from canonical evidence and Research
Engine state. It authorizes no unknown-target computation and claims no ECDLP
improvement.

## 1. The central parity question already has a precise EDS form

Lauter and Stange, *The elliptic curve discrete logarithm problem and equivalent
hard problems for elliptic divisibility sequences*, arXiv:0803.0728 and SAC
2008, define the EDS Residue problem.

Let

```text
Q = [k]G,
W_G(t) = psi_t(G),
```

where `psi_t` is the elliptic division polynomial. The EDS Residue problem asks
for the quadratic character

```text
rho_G(Q) = chi(W_G(k))
```

without knowing `k`.

The same paper proves that an exact parity oracle recovers the full ECDLP by
repeated halving, and that EDS Residue is subexponentially equivalent to ECDLP
under the stated hypotheses. It also observes that ratios of consecutive EDS
residues can be computed from the public point, while the absolute initial
residue remains hidden.

This is the concrete version of the previously vague phrase "hidden theta
orientation bit".

## 2. Canonical periodic lift

For a point `P` of order `n` with `gcd(n,q-1)=1`, define

```text
Phi(P) = (
  W_P(q-1) / W_P(q-1+n)
)^(1/n^2).
```

The root is unique because `n^2` is invertible modulo `q-1`. The value `Phi(Q)`
is computable from the public point `Q` without knowing its scalar.

The associated perfectly periodic EDS is the point function

```text
Q -> Phi(Q).
```

Thus a weak canonical nonprojective lift already exists. It is not enough to
solve ECDLP, because the relation between this periodic lift and the original
EDS contains one unresolved quadratic-character bit.

## 3. Normalization correction candidate

Equation (4) in the displayed 2008 version is printed as

```text
Phi([k]P) = Phi(P)^(k^2-1) W_P(k).
```

The following evidence instead gives

```text
boxed: Phi([k]P) = Phi(P)^(k^2) W_P(k).
```

Evidence:

1. At `k=1`, the corrected equation is an identity; the printed equation would
   force `Phi(P)=1`.
2. The rank-one elliptic-net transformation law gives

   ```text
   W_[k]P(l) W_P(k)^(l^2) = W_P(k*l).
   ```

   Comparing `l=q-1` and `l=q-1+n`, then applying the unique `n^2` root,
   yields the exponent `k^2`.
3. The later ratio formula in the same paper uses the exponent difference
   `(k+1)^2-k^2=2k+1`, which is consistent with `k^2`.
4. Exhaustive toy checks and the fixed secp256k1 replay pass with `k^2` and fail
   with `k^2-1` on every declared nontrivial sample.

This is recorded as a correction candidate, not as an accepted erratum, until
an independent source-level review is completed.

## 4. Exact secp256k1 specialization

For the public secp256k1 parameters,

```text
gcd(n,p-1) = 1.
```

The fixed public-parameter verifier computes

```text
Phi(G) =
0xee45a5d3582bcc343de09e2560a984ff1cbda1b74b117071860c29563f329c94
```

and finds

```text
chi(Phi(G)) = -1.
```

Therefore, for `Q=[k]G`, the corrected identity gives

```text
chi(Phi(Q)) = (-1)^(k^2) chi(W_G(k))
            = (-1)^k rho_G(Q).
```

Equivalently,

```text
boxed: (-1)^k = chi(Phi(Q)) rho_G(Q).
```

The first factor is publicly computable from `Q`. The second factor is exactly
the EDS Residue bit.

This is the sharpest current answer to the parity-lift question:

```text
canonical lift  = Phi(Q),
hidden orientation bit = rho_G(Q)=chi(psi_k(G)),
parity decoder = chi(Phi(Q))*rho_G(Q).
```

The fixed verifier is

```text
experiments/parity_lift_000/verify_secp_eds_residue_bridge.py
```

and accepts no external point or scalar.

## 5. Why evaluating a fixed division polynomial at Q does not expose rho_G(Q)

The elliptic-net transformation law gives, for every fixed public integer `m`,

```text
psi_m([k]G) = W_G(m*k) / W_G(k)^(m^2).
```

Taking quadratic characters yields

```text
chi(psi_m(Q))
 = chi(W_G(m*k)) rho_G(Q)^(m^2).
```

This supplies relations among EDS residue bits, but a multiplicative expression
made only from fixed-index values `psi_m(Q)` is automatically balanced.

For exponents `e_i` and fixed indices `m_i`, the corresponding EDS exponent
polynomial is

```text
sum_i e_i (m_i*k)^2
- (sum_i e_i m_i^2) k^2
= 0.
```

In the terminology of Proposition 3 of Lauter and Stange, the parity-sensitive
quadratic exponent `t(k)` is constant. The factor `Phi(G)^(k^2)` cancels
exactly.

Consequences:

- a fixed product or ratio of division-polynomial evaluations at `Q` cannot use
  the published EDS-residue mechanism to reveal parity;
- high algebraic degree alone is not useful when the expression remains
  balanced;
- the toy negative for products or ratios of up to four `chi(psi_m(Q))` values
  is explained structurally rather than only empirically.

The balance identity is the next small Lean theorem package.

## 6. GLV consequence

The secp256k1 GLV eigenvalue `lambda` has order three modulo `n` and its
canonical integer representative is even. Hence

```text
chi(psi_lambda(Q)) = chi(Phi([lambda]Q)).
```

The denominator contribution has even exponent and disappears. Both sides are
publicly computable. This gives no absolute EDS residue bit.

More generally, walking around the three-point GLV orbit supplies balanced
relative equations. Without an unbalanced EDS residue observable, the cycle
does not determine `rho_G(Q)`.

This explains why the existing GLV phase-elimination work and the parity line
can share algebraic infrastructure while remaining scientifically distinct.

## 7. What remains genuinely open

The central target is now:

```text
Given public (G,Q), compute rho_G(Q)=chi(psi_k(G)) for Q=[k]G
without recovering k first and below the square-root generic baseline.
```

Promising surviving mechanism classes are narrower than before:

1. an unbalanced theta, sigma, or elliptic-net section whose evaluation from
   `Q` does not cancel the `k^2` scaling factor;
2. a statistic or correlation that identifies the absolute sign of the EDS
   residue sequence from the publicly computable relative sequence;
3. a p-adic or analytic normalization that fixes this sign with a proved
   precision and cost bound;
4. a nonlocal relation involving several independently chosen points or curve
   models that breaks the balance identity without supplying equivalent hidden
   input.

A fixed coordinate change, fixed-index division polynomial, Kummer quotient,
or GLV orbit norm is not sufficient.

## 8. Current completion metric

These percentages measure completion of declared obligations, not probability
of solving ECDLP.

| obligation | completion |
|---|---:|
| identify exact EDS formulation of hidden bit | 100% |
| derive parity bridge | 100% mathematically |
| verify public secp256k1 nonresidue condition | 100% in fixed Python replay |
| independently replay the public condition in Sage or a second CAS | 0% |
| source-level review of the exponent correction | 60% |
| Lean proof of the four generic parity foundations | committed, CI pending |
| Lean proof of fixed-index balance identity | next small package |
| mechanism computing EDS Residue below square-root cost | no positive evidence |

The result is a major narrowing of the question, not a practical attack.
