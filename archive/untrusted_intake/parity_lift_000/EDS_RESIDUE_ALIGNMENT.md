# EDS-RESIDUE-ALIGNMENT-001

Date: 2026-08-11

Status: **untrusted source alignment and public-parameter verification**. This
file is quarantined from canonical evidence and Research Engine state. It
authorizes no unknown-target computation and claims no ECDLP improvement.

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

## 2. Public point function and normalized periodic EDS

For a point `P` of order `n` with `gcd(n,q-1)=1`, define the public point-scaling
function

```text
Phi(P) = (
  W_P(q-1) / W_P(q-1+n)
)^(1/n^2).
```

The root is unique because `n^2` is invertible modulo `q-1`. The value `Phi(Q)`
is computable from the public point `Q` without knowing its scalar.

The elliptic-net transformation law gives the point-function identity

```text
Phi([k]P) = Phi(P)^(k^2) W_P(k).
```

A normalized perfectly periodic EDS is obtained by dividing by the public
global value `Phi(P)`:

```text
W_tilde_P(k)
  = Phi([k]P) / Phi(P)
  = Phi(P)^(k^2-1) W_P(k).
```

Thus the `k^2` and `k^2-1` exponents describe two conventions for the same
construction:

- `k^2` belongs to the public point function `Q -> Phi(Q)`;
- `k^2-1` belongs to the EDS normalized so that its first term is one.

They differ only by the public scalar `Phi(P)`. Ratios of periodic terms are
unchanged. The distinction matters when one tracks an absolute quadratic
character rather than only ratios.

The fixed toy and secp256k1 replays verify both forms simultaneously. This is a
normalization alignment, not a claimed erratum.

## 3. Exact secp256k1 specialization

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

Therefore, for `Q=[k]G`, the public point-function identity gives

```text
chi(Phi(Q)) = chi(Phi(G))^(k^2) chi(W_G(k))
            = (-1)^k rho_G(Q),
```

because `k^2` and `k` have the same parity. Equivalently,

```text
boxed: (-1)^k = chi(Phi(Q)) rho_G(Q).
```

The first factor is publicly computable from `Q`. The second factor is exactly
the EDS Residue bit.

This is the sharpest current answer to the parity-lift question:

```text
canonical public lift = Phi(Q),
hidden orientation bit = rho_G(Q)=chi(psi_k(G)),
parity decoder = chi(Phi(Q))*rho_G(Q).
```

The fixed verifier is

```text
experiments/parity_lift_000/verify_secp_eds_residue_bridge.py
```

and accepts no external point or scalar.

## 4. Why evaluating a fixed division polynomial at Q does not expose rho_G(Q)

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
  this EDS-residue mechanism to reveal parity;
- high algebraic degree alone is not useful when the expression remains
  balanced;
- the toy negative for products or ratios of up to four `chi(psi_m(Q))` values
  is explained structurally rather than only empirically.

The balance identity is the next small Lean theorem package.

## 5. GLV consequence

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

## 6. What remains genuinely open

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

## 7. Current completion metric

These percentages measure completion of declared obligations, not probability
of solving ECDLP.

| obligation | completion |
|---|---:|
| identify exact EDS formulation of hidden bit | 100% |
| derive parity bridge | 100% mathematically |
| verify public secp256k1 nonresidue condition | 100% in fixed Python replay |
| independently replay the public condition in Sage or a second CAS | 0% |
| source-level normalization alignment | about 85% |
| Lean proof of the four generic parity foundations | committed, CI pending |
| Lean proof of fixed-index balance identity | next small package |
| mechanism computing EDS Residue below square-root cost | no positive evidence |

The result is a major narrowing of the question, not a practical attack.
