# UORC-056 C44: Ward open-transport boundary

Date: 2026-08-17

Status: exact closure of one unlimited multiplicative character class, plus an exact secp256k1 transport-connectivity diagnosis. No ordered-sector evaluator, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. What C44 attacks

C43B reduced the target to

\[
(-1)^k=g_G(Q)J_G(x(Q)),\qquad Q=[k]G.
\]

Here `g_G` and `J_G` are **classification signs**: each is only `+1` or `-1`, but neither is a binary digit of `k`. The remaining hard object is the ordered-sector sign

\[
J_G(x(Q)).
\]

C44 attacks the first concrete open-transport proposal: use Ward quasi-periodicity of the elliptic divisibility sequence, or a dependent rank-two elliptic-net period shift, to carry the known orientation at the public generator `G` to the public query `Q`.

An **open transport** means a value with two distinct endpoints, the known anchor and the query. This matters because squares, norms and closed loops erase the sign we are trying to preserve.

## 2. The near-period state

Let

\[
\rho(k)=\chi\bigl(\psi_k(G)\bigr),
\]

where `psi_k` is a division polynomial and `chi` is the quadratic character (the operation that returns `+1` for a nonzero square and `-1` for a nonsquare).

For secp256k1 the exact Ward constants satisfy

\[
\chi(A)=+1,\qquad \chi(B)=-1.
\]

The order-shifted division value therefore has character

\[
\boxed{
N(k):=\chi\bigl(\psi_{n+1}([k]G)\bigr)=(-1)^k\rho(k).
}
\]

This is close to the desired answer, but it contains one unwanted factor `rho(k)`.

## 3. Unlimited four-class theorem

The exact rank-two period-lattice formula shows that every declared character atom is, up to a public constant sign, one of

\[
1,\qquad N(k),\qquad N(k+1),\qquad N(k)N(k+1).
\]

This is not a bounded search statement. Multiplying any finite number of such atoms merely toggles the two exponents modulo two, so the result remains in the same four classes.

For the fixed public secp256k1 generator, exact small-index division-polynomial values provide mismatch witnesses for both possible global phases of every class. Consequently

\[
\boxed{
\text{no finite multiplicative monomial of the declared Ward period-lattice characters equals }(-1)^k.
}
\]

The reason is simple: whenever the construction retains parity, it retains the unwanted `rho` sign with it. Whenever it cancels the `rho` signs multiplicatively, it cancels parity as well.

This closes the entire declared multiplicative character class, not only products up to some chosen weight.

## 4. Doubling and GLV do not connect the whole sector space

On the pair quotient `k ~ -k`, multiplication by two has exact order

\[
\operatorname{ord}_n(2)=\frac{n-1}{64}.
\]

The pair quotient contains `(n-1)/2` positions, so doubling splits it into

\[
\frac{(n-1)/2}{(n-1)/64}=32
\]

separate cycles.

The GLV multiplier `lambda` is already a power of two:

\[
\lambda=2^{2\operatorname{ord}_n(2)/3}\pmod n.
\]

Therefore adding GLV edges does not join those 32 cycles. The known orientation at `G` anchors one cycle, leaving 31 independent cycle signs, or

\[
2^{31}=2,147,483,648
\]

compatible assignments in this transport model.

This corrects the superseded claim that doubling was transitive on the secp256k1 pair quotient.

## 5. A transitive multiplier exists, but localization remains

The public multiplier `7` has full order `n-1` modulo the prime group order. Hence it is transitive on the pair quotient: every pair `{Q,-Q}` lies on one orbit of repeated multiplication by seven.

This removes the 32-cycle disconnection, but does not yet give an algorithm. To transport the anchor sequentially, one must locate the exponent `t` satisfying

\[
Q=\pm[7^t]G.
\]

Finding that orbit position is another discrete-log localization problem. C44 does not claim a lower bound for every way of avoiding it. It proves that merely replacing doubling by a transitive public multiplier does not itself produce the missing endpoint value.

## 6. Decision

C44 establishes:

```text
Ward near-period state                          public and O(log n)
Near-period character                           parity times rho(k)
Finite multiplicative Ward/net character class  exactly four variable classes
Exact parity decoder in that class              impossible on secp256k1
Doubling + GLV pair cycles                       32
Residual signs after one anchor                  31
Transitive public multiplier                     7
Cheap orbit localization                         not found
Ordered-sector evaluator                         not found
Parity oracle                                    not found
```

## 7. Successor

The next package is

```text
FULL-FIELD-OPEN-ROOT-TRANSPORT-C45
```

It must retain an **unsquared full field value** from the anchor to the query before applying any quadratic character, norm, square, symmetric determinant or closed-loop product.

A valid candidate must not:

1. reduce to a finite monomial in the Ward near-period characters;
2. require the hidden orbit exponent `t`;
3. contain a dense order-`n` table or a square-root-width dictionary;
4. accept the desired branch as hidden advice.

The constructive targets are an endpoint-evaluable Miller/theta/elliptic-unit transport, a nonmultiplicative rank-two net relation, or a public recurrence that propagates the unsquared branch along an addition chain without knowing the hidden scalar path.

## Claim boundary

The all-weight closure is exact for the declared multiplicative quadratic-character Ward period-lattice grammar. It does not close unrestricted full-field transports, additive combinations, theta functions, elliptic units, p-adic constructions, modular composition, or arbitrary arithmetic circuits.
