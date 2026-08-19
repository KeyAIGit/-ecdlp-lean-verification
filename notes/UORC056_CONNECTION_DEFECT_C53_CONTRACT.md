# UORC-056 C53 contract: connection defect and moduli-tangent decoder

Date: 2026-08-19

Status: successor research contract. No parity evaluator is claimed.

## 1. Input from C52

C52 establishes three facts:

1. prime-to-characteristic torsion lifts uniquely and preserves `Q_t=[k]G_t`;
2. a nonzero fixed-fibre vertical tangent pair reveals the full scalar `k`;
3. the genuine `a`-moduli direction produces a public logarithmic-cost state with CM quotient relation

```text
R=x dot x_a
S=x^2 dot y_a/y
2(T+7)S=T(3R+1), T=x^3.
```

No declared character decoder returns parity.

## 2. Connection-defect target

For a publicly specified connection `nabla`, define

```text
Delta_k^nabla(G)=nabla([k]G)-d[k]_G(nabla(G)).
```

C53 must determine whether `Delta` is:

```text
zero for a functorial connection,
a public coboundary,
a chosen gauge term,
a pairing or full dual phase,
or a genuinely new endpoint-charged observable.
```

A candidate is rejected if its connection or tangent input is defined using the unknown scalar or an equivalent path label.

## 3. Nonlinear moduli-state target

Search for a uniform decoder built from a constant number of public values among

```text
R(Q), S(Q),
R(phi Q), S(phi Q),
R(phi^2 Q), S(phi^2 Q),
anchor-normalized ratios,
Frobenius conjugates,
resultants or determinants with bounded state dimension.
```

The search must run gauge and covariance type checks before numerical fitting.

## 4. Mandatory gates

A successful package must provide:

1. a literal public evaluator from `E,G,Q`;
2. exact behavior under `Q -> -Q`, `G -> -G` and GLV;
3. held-out validation beyond the C52 corpus;
4. exceptional zero and pole handling;
5. no hidden order-n table or scalar-dependent tangent advice;
6. complete preprocessing, advice, memory, precision, representation and online cost;
7. total cost `O(n^(1/2-epsilon))` for one fixed positive epsilon;
8. independent replay and Lean checks for the algebraic core.

## 5. Immediate rejection rules

Reject any candidate that:

```text
uses a fixed-fibre tangent pair with nonzero anchor differential,
depends only on the scaling direction,
is invariant under the required endpoint gauge,
materializes Theta(n) quotient coefficients,
fits only one toy curve,
or obtains k by inserting it into the deformation.
```

## 6. Success outcomes

C53 must end with exactly one of:

1. a public sub-square-root parity evaluator;
2. a precisely scoped no-go theorem for the declared connection grammar;
3. a new compact charged state with a separately stated unresolved decoder.
