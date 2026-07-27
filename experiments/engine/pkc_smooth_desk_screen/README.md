# PKC smooth-subgroup desk screen

This directory is a deterministic arithmetic screen for the published
prime-field smooth-subgroup mechanism, instantiated with the secp256k1 field
prime

```text
p = 2^256 - 2^32 - 977
```

and the small-factor product

```text
D = 2 * 3 * 7 * 13441 = 564522.
```

It is not a solver, an experiment authorization, or evidence of an ECDLP
shortcut.  The overall direct-mechanism result remains `inconclusive`.

## What is computed

For every `m` from 10 through 20, `artifact.json` records:

- the exact integer threshold `ceil(p^(1/m))`;
- the paper-balance threshold `ceil((m! p)^(1/m))`;
- the reduced exact rational `D^m/(m! p)`;
- `ceil(m! p / D^m)` only when the yield is below one;
- the standard direct `S_(m+1)` per-variable and total degree formulas;
- sequential and balanced recursive `S3` equation and internal-variable counts;
- a binary square-and-multiply upper bound for exponent 564522;
- conditional factor-base and linear-algebra counting minima; and
- explicit `null` values for solving degree, Macaulay dimensions and memory,
  recovery branches, usable factor-base cardinality, independence, and total
  work.

The exact factorization identity is also replayed:

```text
p - 1
  = 2 * 3 * 7 * 13441
    * 205115282021455665897114700593932402728804164701536103180137503955397371.
```

The 237-bit cofactor's primality is proved by the repository's Lean
certificate.  These standard-library scripts verify the product identity but
do not duplicate that primality certificate.  Given the certified prime
factorization, the artifact enumerates every divisor strictly below the large
cofactor.

There is one additional exact, narrowly scoped count.  If smoothness means
`B <= 13440`, then neither 13441 nor the large cofactor is eligible.  Every
`B`-smooth divisor of `p-1` therefore divides `2*3*7 = 42`.  Hence the
multiplicative subgroup or coset root set used as x-coordinate candidates has
`#F <= 42`.  This does not assert 42 usable curve points; counting both possible
y-sign lifts gives only the separate upper bound 84.

## Reproduce and validate

From this directory:

```bash
python3 generate.py --check
python3 validate.py
python3 -m py_compile generate.py validate.py
```

To intentionally regenerate after an audited producer change:

```bash
python3 generate.py --write
```

`validate.py` imports neither the producer nor its functions.  It uses a
different integer-root algorithm, independently recomputes the decisive
arithmetic, verifies canonical JSON, and checks `artifact.sha256`.  Its
`--artifact` and `--hash-file` options allow mutated copies to be supplied for
fault-injection tests without modifying the committed artifact.

## Source and claim boundary

- `SC-SECP-PMINUS1-FACTORIZATION`, bound to `artifact.json`, supplies the
  independently replayed integer factorization.
- `SC-SECP-PMINUS1-LARGE-COFACTOR-PRIME`, anchored to the exact theorem in
  `Ecdlp/Proved/Secp256k1PrimeP.lean`, supplies primality of the 237-bit
  cofactor.
- `SC-PKC-RELATION-YIELD`, anchored in
  `data/source_claim_extracts/petit_kosters_messeng2016.json`, supplies the
  paper's heuristic yield and balance expressions.
- The direct Semaev numbers replay the usual degree formula only.  They do not
  imply a solving degree or a Macaulay size.

The conditional `D`-column linear-algebra counts assume the full `D`-element
coordinate root set is used as `D` active logarithm unknowns.  Actual curve
lifts, independent relations, rank, recovery, exceptional components,
coefficient sparsity, storage, and total attack cost are unresolved.
