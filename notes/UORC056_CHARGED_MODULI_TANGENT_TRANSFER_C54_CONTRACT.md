# UORC-056 C54 contract: charged moduli-tangent transfer

Date: 2026-08-19

Status: successor research contract. No parity evaluator is claimed.

## 1. Input from C53

C53 proves:

```text
connection defect = zero, direct point state, or full-scalar channel;
(T,R,S) is identical on Q and -Q and cannot decode parity;
OA*OB=(R(Q)/R(G))*((T(G)+7)/(T(Q)+7));
endpoint charge in the tangent pair is carried by the public x/y ratio.
```

The remaining compact state is the charged pair

```text
OA=omega_a(Q)/omega_a(G),
OB=omega_b(Q)/omega_b(G).
```

## 2. Exact C54 question

Determine whether the charged pair has a public short transfer or orbit-factor law that yields

```text
(-1)^k
```

without a scalar-labelled path, an exact nonzero-anchor connection defect, or an order-n table.

## 3. Mandatory targets

C54 must derive and test:

1. exact addition and doubling laws for the charged state;
2. covariance under `Q -> -Q`, `G -> -G` and GLV;
3. the factor remaining after dividing out the public coordinate charge;
4. bounded-width transfer matrices and recursive resultants;
5. even/odd orbit factors in the charged coordinate;
6. complete cost accounting.

## 4. Immediate rejection rules

Reject any candidate that:

```text
uses k in a tangent or connection input,
uses only the neutral quotient state,
returns the ordinary x/y orientation without the generator-relative parity,
materializes Theta(n) coefficients or values,
fits only one toy curve,
or has total cost Omega(sqrt(n)).
```

## 5. Success outcomes

C54 must end with one of:

1. a public sub-square-root parity evaluator;
2. a scoped no-go theorem for the declared charged-transfer grammar;
3. a new compact transfer state with an explicitly unresolved decoder.
