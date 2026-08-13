# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C6: exact first variation of the minimal trinomial norm

Date: 2026-08-13

Status: exact extraction law found; compact evaluation remains open.

Let `T=T_G` on a cyclic subgroup of odd prime order `n`, and let

```text
T_Q=T^k,
Q=[k]G,
1 <= k < n.
```

Define

```text
R_k(t)=det(I+T+tT^k)
      =Res(z^n-1,1+z+t z^k).
```

Jacobi's determinant formula gives

```text
R'_k(0)=det(I+T) Tr((I+T)^(-1)T^k).
```

For an odd cycle,

```text
det(I+T)=2,
(I+T)^(-1)=(1/2)sum_(j=0)^(n-1)(-1)^jT^j.
```

Also

```text
Tr(T^m)=n if m=0 mod n,
Tr(T^m)=0 otherwise.
```

Only `j=n-k` survives. Since `n` is odd,

```text
boxed:
R'_k(0)=-n(-1)^k.
```

Equivalently,

```text
boxed:
(-1)^k=-n^(-1)R'_k(0),
[t]Res(z^n-1,1+z+t z^k)=-n(-1)^k.
```

This is the first exact full-support observable in the current line with a constant-description extraction law. It passes the required sign changes under `Q -> -Q` and `G -> -G`.

The replay verifies the identity for all `1212` nonzero indices on the six frozen orders

```text
19,31,67,271,397,433
```

and independently reconstructs the resultant's linear coefficient for all `114` nonzero indices on orders `19,31,67` by exact interpolation.

This is not yet a fast evaluator. Generic implementations still fail the complete cost gate:

```text
explicit determinant or trace                    n-dimensional,
full resultant                                   degree n,
generic interpolation                            many determinant values,
dual-number determinant                          same large state,
automatic differentiation                        preserves underlying cost.
```

A symbolic arithmetic circuit for `R_k(t)` would immediately yield the target sign by constant-overhead differentiation, following Baur-Strassen. Therefore a compact symbolic trinomial-resultant circuit is essentially the target evaluator, not a free intermediate.

The remaining question is:

```text
Can the first variation of det(I+T_G+tT_Q) be evaluated directly from
public elliptic-curve coordinates below n^(1/2-epsilon), without knowing k
and without constructing an n-dimensional translation representation?
```

Promising representations are a constant-size elliptic resultant, determinant line, torsion, intersection formula, or nonlinear transfer state. A generic matrix or degree-`n` polynomial representation is rejected.

No accepted-cost evaluator or asymptotic improvement is claimed.

Reference: W. Baur and V. Strassen, The Complexity of Partial Derivatives, Theoretical Computer Science 22 (1983), 317-330.
