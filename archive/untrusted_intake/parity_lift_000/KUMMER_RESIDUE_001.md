# KUMMER-RESIDUE-001: the residual parity bit after public sign removal

Date: 2026-08-11

Status: **untrusted structural derivation**. This note is quarantined from
canonical evidence and Research Engine state. It constructs no unknown-target
oracle and claims no ECDLP improvement.

## 1. Why this question differs from direct parity

For an odd-order cyclic group `C=<G>`, canonical scalar parity satisfies

```text
par_G(-Q) = 1 - par_G(Q),    Q != O.
```

Therefore parity itself cannot factor through the Kummer quotient
`E/{P ~ -P}` or through an x-only/even-theta representation.

The EDS alignment separates parity into

```text
(-1)^k = chi(phi_raw(Q)) * rho_G(Q),
Q=[k]G,
rho_G(Q)=chi(W_G(k)).
```

The first factor is public and sign-sensitive. The second factor is the hidden
EDS Residue bit. The correct Kummer question is therefore not whether Kummer
coordinates directly contain parity, but whether they contain `rho_G(Q)` after
the public sign-sensitive factor has been removed.

## 2. Negation law of the raw point function

For a short Weierstrass curve in odd characteristic, division polynomials have
point-negation parity

```text
psi_m(-P) = (-1)^(m+1) psi_m(P).
```

Thus odd-index terms are invariant and even-index terms change sign.

The raw point function is

```text
phi_raw(P) =
  (W_P(q-1) / W_P(q-1+n))^(1/n^2),
```

where `n` is odd and `gcd(n,q-1)=1`. Since `q-1` is even and `q-1+n` is odd,
negating `P` changes the ratio by `-1`. The inverse of the odd integer `n^2`
modulo the even integer `q-1` is itself odd. Consequently

```text
phi_raw(-P) = -phi_raw(P).                    (1)
```

This is a deterministic public sign change, not the hidden scalar parity.

## 3. General EDS-residue negation law

Assume the raw point-function bridge

```text
chi(phi_raw([k]G))
  = chi(phi_raw(G))^(k^2) rho_G([k]G).
```

When `chi(phi_raw(G))=-1`, compare this identity for `k` and `n-k`. Because `n`
is odd, `k` and `n-k` have opposite parity, while equation (1) contributes the
factor `chi(-1)`. Cancellation gives

```text
rho_G(-Q) = -chi(-1) * rho_G(Q).              (2)
```

Hence the residual bit has two field-dependent behaviours:

```text
q == 3 mod 4  ->  chi(-1)=-1  ->  rho_G(-Q)= rho_G(Q),
q == 1 mod 4  ->  chi(-1)=+1  ->  rho_G(-Q)=-rho_G(Q).
```

## 4. secp256k1 specialization

The secp256k1 prime satisfies

```text
p == 3 mod 4.
```

The fixed-public branch replay also records

```text
chi(phi_raw(G)) = -1.
```

Therefore equation (2) specializes to

```text
boxed: rho_G(-Q) = rho_G(Q).                  (3)
```

So the hidden EDS Residue bit is Kummer-invariant on the nonidentity
secp256k1 group, even though canonical scalar parity is not.

The existing fixed samples include the pairs `G,-G` and `2G,-2G`; their EDS
residue characters agree. A complete formal proof still requires the raw
point-function identity and division-polynomial negation law to be bound to the
repository's exact definitions.

## 5. Revised central theta question

The most precise surviving question is now

```text
Given the Kummer class x(Q) of a nonzero public point Q=[k]G,
can one compute rho_G(Q)=chi(psi_k(G)) below square-root cost?
```

Equivalently, seek a Kummer/theta observable `R` satisfying

```text
R(x([k]G)) = rho_G([k]G),
```

with an explicit map, exceptional-locus treatment, precision model, recovery
theorem, and total cost.

This is a better target than a sign-sensitive theta lift for parity itself:

- Kummer coordinates are allowed because the remaining bit is invariant;
- the public factor `chi(phi_raw(Q))` restores the final scalar parity;
- exact parity then recovers the full discrete logarithm by the proved bit-peel
  reduction.

## 6. Direct algebraic Kummer-output barrier

There are `(n-1)/2` nonidentity Kummer classes in an odd prime-order group. If a
nonconstant rational function `r` on the Kummer line has no pole on those
classes and directly takes the values

```text
r(x(Q)) = rho_G(Q) in {+1,-1},
```

then `r^2-1` vanishes at all `(n-1)/2` classes. If `d` is the degree of `r`, a
nonzero `r^2-1` has at most `2d` zeros, so

```text
d >= (n-1)/4.                                (4)
```

If `r^2-1` is identically zero, `r` is constant and cannot encode a nonconstant
residue sequence.

Equation (4) closes only direct bounded-degree `+1/-1` outputs. It does not
close a high-degree expression with a short recurrence, nor an arithmetic
character decoder of the form

```text
chi(f(x(Q))) = rho_G(Q).
```

That character-valued Kummer class is now the principal live algebraic target.

## 7. Research consequences

The parity line should be split into two layers:

1. **Public sign layer**

   ```text
   Q -> chi(phi_raw(Q)),
   ```

   which distinguishes `Q` and `-Q` and is already publicly evaluable under the
   stated hypotheses.

2. **Hidden Kummer layer**

   ```text
   x(Q) -> rho_G(Q),
   ```

   which is the actual unresolved bit on secp256k1.

This changes the role of prior theta/Kummer work. Sign-erasing coordinates are
not useful as direct parity decoders, but they may be exactly the natural space
for the residual EDS bit.

## 8. Highest-value next obligations

1. Formalize the division-polynomial negation law for the repository's exact
   `prePsi/psi` conventions.
2. Formalize equation (2) as an abstract sign theorem and specialize it to
   secp256k1 using `p mod 4 = 3`.
3. Recast `CHAR-PARITY-001` as a Kummer-residue search:

   ```text
   chi(f(x(Q))) = rho_G(Q).
   ```

4. Apply the mixed-character/conductor analysis to this even sequence rather
   than to direct scalar parity.
5. Test structured x-only theta, division-polynomial, and elliptic-net
   observables on independently held-out toy curves, measuring formula growth
   rather than isolated interpolation success.

## 9. Completion estimate

These numbers measure completion of the stated subproblem, not probability of
solving ECDLP.

| obligation | completion |
|---|---:|
| derive residual negation law | about 90% |
| secp256k1 Kummer-invariance specialization | about 85% |
| bind the proof to exact repository division-polynomial definitions | about 20% |
| independent CAS/source replay | 0% |
| identify the correct Kummer-residue decoder class | about 70% |
| construct a sub-square-root decoder | no positive evidence |

## Claim boundary

Equation (3) narrows where the unknown bit lives. It does not make that bit
easier to compute, and it does not imply that a bounded-level theta function,
Kummer coordinate, or existing GLV invariant already evaluates it.
