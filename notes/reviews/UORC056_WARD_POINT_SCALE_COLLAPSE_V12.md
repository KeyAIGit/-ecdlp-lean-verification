# UORC-056 Ward point-scale collapse V12

Date: 2026-08-14

Status: **the Ward quasi-period constants of the EDS attached to a public query point contain no additional orientation beyond the already-public ratio-root point function. Under `gcd(n,p-1)=1`, the two Ward constants are exact fixed powers of `phi_raw(Q)` and `phi_raw(Q)` is recovered from either nondegenerate constant by one public exponentiation.**

Central target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

V12 is a mechanism closure, not the target evaluator.

## 1. Ward constants at a rational n-torsion point

Let `P in E(F_p)` have odd order `n>=3`, with `gcd(n,p-1)=1`. Write

```text
W_j(P)=psi_j(P).
```

Silverman's torsion quasi-periodicity gives units `a_P,b_P in F_p^*` with

```text
W_(s*n+j)(P)=a_P^(j*s) b_P^(s^2) W_j(P).
```

In the classical division-polynomial normalization used by the executable replay,

```text
a_P = W_(n+2)/(W_2 W_(n+1)),
b_P = W_2 W_(n+1)^2/W_(n+2).
```

## 2. The public ratio-root point function

The existing PARITY-LIFT bridge defines `phi_raw(P)` by

```text
phi_raw(P)^(n^2)=W_(p-1)(P)/W_(p-1+n)(P).       (V12.1)
```

The `n^2`-th root is unique because `gcd(n,p-1)=1`.

Apply Ward quasi-periodicity with `j=p-1` and one period shift:

```text
W_(p-1+n)=a_P^(p-1) b_P W_(p-1).
```

Fermat gives `a_P^(p-1)=1`, so

```text
W_(p-1)/W_(p-1+n)=b_P^(-1).                    (V12.2)
```

Combining `(V12.1)` and `(V12.2)` yields

```text
boxed:
b_P=phi_raw(P)^(-n^2).                         (V12.3)
```

Thus the second Ward constant is exactly a fixed power of the already-public point scale.

## 3. The first Ward constant also collapses

The torsion constants satisfy

```text
a_P^n=b_P^2.                                    (V12.4)
```

Using `(V12.3)`,

```text
a_P^n=phi_raw(P)^(-2n^2).
```

Since the `n`-th power map on `F_p^*` is injective when `gcd(n,p-1)=1`,

```text
boxed:
a_P=phi_raw(P)^(-2n).                           (V12.5)
```

Therefore the full pair is

```text
(a_P,b_P)
=(phi_raw(P)^(-2n), phi_raw(P)^(-n^2)).         (V12.6)
```

No hidden scalar or generator orientation appears in `(V12.6)`.

## 4. Explicit reconstruction

Let

```text
e=(n^2)^(-1) mod (p-1).
```

Then `(V12.3)` gives

```text
boxed:
phi_raw(P)=b_P^(-e).                             (V12.7)
```

So computing the Ward constants and computing the public ratio-root point scale are equivalent up to fixed public exponentiations. The Ward state is not a new information channel.

## 5. Quadratic-character consequence

Because `n` is odd,

```text
chi(a_P)=+1,
chi(b_P)=chi(phi_raw(P)).                        (V12.8)
```

On secp256k1 the already-verified EDS bridge is

```text
(-1)^k=chi(phi_raw([k]G))*chi(psi_k(G)).         (V12.9)
```

Hence the Ward character pair becomes

```text
chi(a_Q)=+1,
chi(b_Q)=chi(phi_raw(Q)),
```

which exposes exactly the public factor of `(V12.9)` and leaves the same hidden EDS-residue/orientation factor as before.

## 6. Generator-change law and why its apparent carry disappears

A direct change-of-generator calculation with `P=[k]G` initially produces a carry `c=floor(2k/n)` in the exponents of `a_P` and `b_P`. After substituting the torsion relation `a_G^n=b_G^2` and the normalized periodic EDS, all carry terms cancel exactly. This is another way to reach `(V12.6)`.

Thus the apparent `2k>=n` information in the raw Ward exponents is gauge, not a new parity observable.

## 7. Exact replay

The committed replay verifies `(V12.3)`--`(V12.8)` for every nonzero marked point of the frozen 18-curve corpus and for fixed known secp256k1 sample scalars. It also checks direct reconstruction of `phi_raw(P)` from `b_P` and the secp parity bridge.

## 8. Decision

```text
Ward a_Q,b_Q cheaply computable from Q?                 yes
Do they contain a new orientation bit?                  no
Exact relation to public point scale                    (V12.6)
Recover phi_raw(Q) from Ward b_Q                        one fixed exponentiation
Character of a_Q                                        +1
Character of b_Q                                        chi(phi_raw(Q))
Central parity evaluator                                still absent
```

## 9. Remaining central route

Do not continue searching functions of the Ward quasi-period constants alone. V12 proves that this state is only a repackaging of the public coordinate factor already separated from the hidden orientation.

The high-leverage remaining target is still **distinguished global integration / branch propagation**: evaluate the oriented Pell/Miller factor or `Y_G(x(Q))/y(Q)` directly without an orbit walk, an explicit oriented root, a dual character, or square-root-width state.

## 10. Claim boundary

V12 closes only the information content of the classical Ward quasi-period constants under the stated coprimality hypothesis. It does not rule out richer high-index division-polynomial combinations, nonlinear field-valued circuits, theta/elliptic-unit constructions, or the central evaluator itself.
