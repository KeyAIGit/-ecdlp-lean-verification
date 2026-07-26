# PKC sextic-twist CM arithmetic screen

This package is a deterministic, non-executable arithmetic screen for GitHub
issue #252. It tests whether the sextic twist

```text
E6: y^2 = x^3 + 6 over the secp256k1 base field
```

has the order, factorization, CM Frobenius representation, and rational-kernel
endomorphism candidates stated in the issue. It also recomputes the narrow
PKC-2016 relation-yield heuristic for selected subgroup divisors.

## What it establishes

The producer and independent validator check:

- the six `j=0` CM trace and group-order candidates;
- five deterministic points that distinguish the `E6` order candidate;
- the exact displayed order factorization;
- recursive Pocklington primality certificates for every prime factor;
- Eisenstein norms and exact divisibility `alpha | (Pi - 1)` for four candidate
  rational-kernel endomorphisms;
- exact rational inputs to the heuristic `D^m/(m!p)` for `m=3..6`;
- the canonical artifact SHA-256.

`generate.py` uses affine elliptic-curve arithmetic. `validate.py` does not import
it and replays the order discrimination with a separate Jacobian implementation.
Both scripts use only the Python standard library.

## What it does not establish

This package does not prove that the endomorphism circuit is a useful factor-base
membership representation. In particular, it does not establish:

- the full subgroup and coset construction;
- saturation, exceptional-locus, or recovery semantics;
- lower Groebner degree, mixed volume, treewidth, memory, or runtime;
- an end-to-end advantage over plain Semaev relation generation or Pollard rho;
- any secp256k1 discrete-log result.

It runs no solver and no ECDLP instance. Any toy experiment remains blocked by
the Research Engine gates and a separate dated owner decision.

## Replay

```text
python3 experiments/pkc_sextic_twist_cm_screen/generate.py --check
python3 experiments/pkc_sextic_twist_cm_screen/validate.py
```

Expected terminal lines:

```text
CERT_OK
VALIDATION_OK
5686ff12d977575229801df9ccae092bb150faa33e15d88bf9669fa04bd44c86
```

## Sources

- Petit, Kosters, and Messeng, *Algebraic Approaches for the Elliptic Curve
  Discrete Logarithm Problem over Prime Fields*, PKC 2016, especially Sections
  3.1, 3.2, and 3.4.
- Bos et al., *Elliptic Curve Cryptography in Practice*, Financial Cryptography
  2014, for the six secp256k1 twist classes and their large-factor sizes.

The exact arithmetic in the committed artifact is recomputed locally and is not
accepted from an informal twist-factor list.
