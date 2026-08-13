# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C5: minimal sparse two-translation resultant

Date: 2026-08-13

Status: exact structural narrowing; no evaluator is claimed.

Let `T=T_G` and `T_Q=T^k` on the cyclic subgroup function space. C4 shows that one-translation spectral data is independent of nonzero `k`.

For distinct shifts `r,s mod n`, where `n` is odd prime,

```text
det(aT^r+bT^s)=a^n+b^n.
```

Thus every two-term translation norm is independent of the relative shift. The first potentially informative circulant is

```text
D_(a,b,c)(k)=det(aI+bT+cT^k)
            =Res(z^n-1,a+bz+cz^k).
```

For `k` different from `0,1`, affine changes of the exponent triple `{0,1,k}` give the exact identities

```text
D_(a,b,c)(k)
=D_(a,c,b)(1/k)
=D_(b,a,c)(1-k)
=D_(b,c,a)(1/(1-k))
=D_(c,a,b)((k-1)/k)
=D_(c,b,a)(k/(k-1)).
```

Consequences for the public secp256k1 subgroup order `n=1 mod 4`:

```text
b=c  -> D(k)=D(1/k).
```

At `k=2`, the inverse `(n+1)/2` has the opposite canonical parity. Hence this coefficient family cannot equal the target sign.

Likewise,

```text
a=c  -> D(k)=D(k/(k-1)).
```

At `k=3`, the transformed value `(n+3)/2` has the opposite parity, so this family is also rejected.

The family `a=b` has only the forced symmetry `k -> 1-k`, which preserves canonical parity on the nondegenerate domain. It remains open, together with fully asymmetric coefficients.

The deterministic replay checks:

```text
all two-term determinant identities on six frozen orders,
all six affine identities for every admissible k,
explicit symmetry mismatch witnesses,
145 primitive integer triples in [-3,3]^3
on the complete nonzero domains for n=19,31,67.
```

For the bounded templates it tests:

```text
determinant is exactly two-valued by parity,
quadratic character of the determinant equals parity up to global sign.
```

Both exact match counts are zero. This is bounded evidence only.

The unresolved minimal object is

```text
D_(a,a,c)(G,Q)=det(aI+aT_G+cT_Q)
```

or a fully asymmetric three-term variant, together with a complete sub-square-root coordinate evaluation method. A degree-`n` resultant, an `n`-dimensional state, or all roots of unity are not admissible as hidden cost.

No public oriented-root evaluator or asymptotic improvement is obtained.
