# GPT Pro focused continuation

## ODD-RATIONAL-FUNCTIONAL-CALCULUS-069

Work only on the UORC056 endpoint-gauge branch. Reproduce C15-C18 first. Use only frozen toy curves, the public seven-curve extension corpus, known toy scalars, and public secp256k1 constants. Do not accept an external unknown-scalar point, wallet, or production key.

## Central target

For

```text
Z_i(P)=Z_G(phi^i(P)), i=0,1,2,
```

C18 closes the full polynomial family

```text
Theta_P=Tr_<phi>(P(Z_G))
```

for nonzero odd polynomials and proves quotient support at least `(n-1)/6-4`.

Study

```text
Theta_R=Tr_<phi>(R(Z_G)),
R(-T)=-R(T),
R in F_p(T).
```

Find an exact compact selector with complete cost `O(n^(1/2-epsilon))`, or prove a support or state lower bound for one declared odd rational grammar.

## Mandatory order

### A. Local orders

Write a reduced odd rational function in one of the forms

```text
R(T)=T*A(T^2)/B(T^2),
R(T)=A(T^2)/(T*B(T^2)).
```

Compute the odd integers

```text
a=ord_(T=0) R,
b=ord_(T=infinity) R.
```

Classify competing valuations on GLV orbit types 0,1,2,3. Separate `a<b`, `a>b`, and the balanced case `a=b`.

### B. Balanced cancellation families

Prioritize

```text
T/(1+cT^2),
T+c/T,
T/(1+cT^2)+d*T^3/(1+eT^2),
T*A(T^2)/B(T^2).
```

When leading valuations tie, compute the leading coefficient ratio as a rational orbit function. A constant receives credit only if cancellation is uniform symbolically over the complete admissible domain, not after per-orbit fitting.

### C. Invariant-field reduction

Express every candidate through `E1,E2,E3`, cancel public factors, and verify

```text
(E1,E2,E3)->(-E1,E2,-E3).
```

Reject any candidate whose odd sign is inserted through a denominator trivialization or branch seed.

### D. Bounded synthesis

Freeze a rational grammar before screening. Separate discovery, validation, and held-out curves. The same symbolic formula must transfer across the extension corpus.

### E. Scoped theorem

If no compact formula survives, prove a theorem for at least one broad class:

```text
fixed local-order pair (a,b),
bounded rational degree,
two-term Laurent symmetric circuits,
finite sums of odd rational traces,
or bounded-width rational ABPs in E1,E2,E3.
```

Degree-only reasoning is forbidden. Charge preprocessing, advice, memory, representation, and online work.

## Completion gates

A positive result must handle every subgroup point and divisor collision, preserve generator covariance, provide regularized local extraction, and pass the complete sub-square-root cost gate.

A negative result must name the exact grammar and prove the bound within it. A finite negative screen is supporting evidence only.