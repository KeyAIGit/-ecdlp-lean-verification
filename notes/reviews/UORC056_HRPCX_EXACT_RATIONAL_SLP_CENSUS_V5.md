# UORC-056 H-RPCX exact rational SLP census V5

## Purpose

V1-V3 prove structural barriers. V5 performs the first exact nonlinear circuit census under the H-RPCX track.

## Grammar

The same expression is evaluated without coefficient retraining on five deterministically selected small prime-subgroup instances of

`y^2 = x^3 + 7`.

Public leaves are:

- `0`, `1`, `-1`, and the curve constant `7`;
- generator coordinates `x(G)` and `y(G)`;
- query coordinates `x(Q)` and `y(Q)`.

Allowed gates are:

- addition;
- subtraction;
- multiplication;
- inversion, only when the operand is nonzero at every tested nonzero subgroup point on every curve.

The target is exact canonical parity on every nonzero subgroup point.

## Search method

The search is exhaustive up to eight arithmetic gates.

Every expression is evaluated semantically on the full joint corpus. Expressions with identical joint value vectors are merged, keeping only the smallest circuit. Commutative gates are canonicalized. No beam, random sampling, correlation threshold, or learned coefficient is used.

Therefore a negative result is exact for the declared grammar and gate budget.

## Result

No single expression with at most eight allowed gates equals exact parity on the full five-curve corpus.

This closes only the declared coordinate-rational grammar at that size. It does not prove a general arithmetic-circuit lower bound.

## What remains open

- circuits with more than eight gates;
- group-operation leaves such as coordinates of `[s]Q`;
- GLV, CM, Miller, theta, division-polynomial, p-adic, or pairing states;
- inversion with explicit exceptional-branch handling;
- high-degree recurrences and modular-composition circuits;
- circuits specialized to secp256k1 through additional public constants, provided their total description cost is counted.

## Engine consequence

The H-RPCX engine must not spend additional runs enumerating syntactic variants of this exact grammar below the certified gate bound. Expansion must add a genuinely new primitive or raise the proven size frontier.