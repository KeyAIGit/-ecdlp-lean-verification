# UORC-056 Effectivity Dichotomy for Compression Claims

## Status

Resolved logical boundary. A general nonconstructive compression claim is either trivial or already algorithmic; a meaningful intermediate theorem must restrict the representation class.

## Case 1: pure existential factorization is trivial

Suppose the claim asks only for a small set `X` and maps

`S : subgroup points -> X`,

`D : X -> {+1,-1}`

such that `D(S(Q))` equals exact parity, but does not require `S` or `D` to be publicly constructible.

Choose

`X={+1,-1}`,

`S(Q)=Parity(Q)`,

and `D` equal to the identity.

The state has only two values. Thus an arbitrarily small existential state always exists for every Boolean function. This statement contains no algorithmic information.

The same problem appears if an exponentially large parity table is allowed to be hidden inside the definitions of `S`, `D`, advice, coefficients, branch choices, or preprocessing.

## Case 2: effective factorization is already an algorithm

Suppose instead that:

- `S(E,G,Q)` is publicly computable in `poly(log n)` time and memory;
- `D(E,G,S)` is publicly computable in `poly(log n)` time;
- all advice, preprocessing, representation, and precision costs are polynomial;
- decoding is exact for every subgroup point.

Then the composition

`Q -> S(E,G,Q) -> D(E,G,S)`

is itself a polynomial-time exact parity algorithm.

Conversely, any polynomial-time parity algorithm gives such a factorization by choosing `S(Q)=Q` and using the algorithm as `D`.

Therefore a fully effective general compression theorem is equivalent to the target algorithm, not a weaker precursor.

## No representation-free middle theorem

Without restrictions on the mathematical form of `S` and `D`, there is no substantive middle statement between the two cases:

- remove effectivity, and compression is vacuous;
- require full effectivity, and compression is the algorithm.

A nonconstructive proof may still prove that a particular algorithm exists without displaying an optimized implementation. Logically, however, it has already proved polynomial-time solvability.

## Where genuine intermediate theorems live

A useful weaker theorem must declare a restricted representation class and establish a structural fact inside it. Examples include:

- parity lies in a specified module of dimension `poly(log n)`;
- a specified matrix family has low rank;
- a declared recurrence grammar has bounded width;
- an oriented root has a short straight-line program in a specified gate set;
- a particular CM, Miller, theta, or p-adic state is closed under declared transitions;
- a declared class is impossible by a lower bound.

Such results can be easier than the complete algorithm because they prove only one structural component. But they must not be called a proof of general H-PCX until public construction and exact decoding are supplied.

## Consequence for H-PCX and H-RPCX

General H-PCX, as currently defined, is equivalent to a polynomial-time parity algorithm and therefore to polynomial-time ECDLP via bit peeling.

H-RPCX is a stronger extraction hypothesis only after its feature language is fixed. If the feature language is not fixed or may contain the unknown parity function itself, recoverability is again circular.

The engine must therefore attach every compression hypothesis to:

1. a finite or effectively bounded grammar;
2. an explicit cost model;
3. a noncircular public construction;
4. an exact verification route;
5. a statement of what remains outside the class.

## Decision rule

Reject any claimed intermediate theorem that does not answer:

- What exactly is the allowed state language?
- How is the state constructed without already knowing parity?
- How is the decoder represented and evaluated?
- Where are all coefficients, branch choices, and preprocessing charged?
- Why is the theorem not satisfied by the tautological state `S(Q)=Parity(Q)`?
