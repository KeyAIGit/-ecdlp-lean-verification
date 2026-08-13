# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C7: dual-exponent and pairing boundary

Date: 2026-08-13

Status: the C6 first-variation identity is exact, but its apparent sparse dual representation is not publicly uniform. No evaluator is claimed.

C6 proves for every nonzero `Q=[k]G`:

```text
[t] Res(z^n-1,1+z+t z^k)=-n(-1)^k.
```

The variable `z` represents the translation `T_G`. Therefore the term for
translation by `Q` is `z^k` because `T_Q=T_G^k`.

An algorithm that receives public `(G,Q)` and explicitly emits an exponent
`e_Q` satisfying

```text
T_Q=T_G^(e_Q)
```

has already computed the full scalar. The regular translation action is
faithful, so `Q=[e_Q]G` and uniqueness gives `e_Q=k`. The three-term notation is
mathematically compact but algorithmically nonuniform if the exponent list is
treated as public input.

The available representations are therefore:

```text
explicit z^k exponent                  circular: it is k,
black-box translation P -> P+Q         public, but n-dimensional generically,
full dual diagonalization              n character components.
```

A nondegenerate pairing with a complementary torsion point gives

```text
e_n(Q,R)=e_n(G,R)^k.
```

This transfers the discrete logarithm to `mu_n`. It does not directly give
canonical integer parity. Since `n` is odd, every homomorphism
`H -> {+1,-1}` is trivial, while canonical parity has one wrap defect and is
not a group character.

For secp256k1, the exact public modular replay verifies, from the factorization
recorded in `notes/PRIMALITY.md`,

```text
ord_n(p)=(n-1)/6
=19298681539552699237261830834781317975472927379845817397100860523586360249056.
```

This embedding degree has bit length `254`. It is `Theta(n)`, so a conventional
field containing `mu_n` has linear base-field dimension and cannot meet a
sub-square-root representation budget.

The repository replay is

```text
experiments/parity_lift_000/uorc056_secp256k1_embedding_degree.py
```

and checks the factor product, annihilation exponent, minimality against every
prime divisor of the candidate order, and the public half-order value `-1`.
The repository's recursive Lean primality certificates are still a separate
planned item. An external exact replay produced for this package verifies the
same factorization through a 46-node recursive Lucas certificate without a
probabilistic primality test.

Closed in this declared representation class:

```text
explicit generation of the hidden dual exponent,
one pairing character as canonical parity,
full character diagonalization,
conventional small-extension pairing for secp256k1.
```

Still open:

```text
a primal elliptic-coordinate formula for the first variation,
a constant-size determinant line or torsion invariant,
a smaller coordinate trace formula for (I+tau_G)^(-1)tau_Q,
an oriented fast elliptic product evaluated before dual expansion.
```

Strongest successor:

```text
PRIMAL-FIRST-VARIATION-EVALUATOR-057
```

Evaluate `[t]det(I+T_G+tT_Q)` directly from public elliptic coordinates without
compiling `Q` into `z^k`, without an extension of degree `Theta(n)`, and without
constructing the regular or dual `n`-dimensional representation.

```text
exact first-variation observable          yes
public explicit exponent z^k              no; it is k
one pairing character gives parity        no
full dual state size                      n
secp256k1 embedding degree                (n-1)/6
embedding-degree bit length               254
primal coordinate evaluator               open
accepted-cost evaluator                   absent
sub-square-root ECDLP                     absent
```
