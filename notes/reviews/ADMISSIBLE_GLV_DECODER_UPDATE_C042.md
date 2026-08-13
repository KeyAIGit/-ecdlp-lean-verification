# Admissible GLV decoder update after C042

Date: 2026-08-12

## Result

The first natural translated-characteristic mixed-weight determinant

```text
M_ij(Q,R)=x(phi^i Q + phi^j R)
```

is C3-circulant after public row scaling.  Its determinant decomposes into three C3 Fourier components; one component is an exact square.  The anti-Kummer plus/minus determinant reduces, modulo a square denominator and public constants, to

```text
y(Q)*x(Q)^3*R4(X^3,x(Q)^3;7),
```

with a degree-four polynomial `R4` in the quotient coordinate.  It is therefore a low-degree direct-coordinate square class rather than a new theta-level orientation object.

A public scalar pullback only permutes additive Fourier frequencies, so one pulled-back copy cannot amplify this base resolvent into the carry spectrum.

The stronger exact pencil

```text
F([m]Q)+c*G([ell]Q)
```

was exhaustively tested for every nonzero `m,ell`, every `c in F_p`, both global square classes, and nine declared base-component pairs across the medium groups of orders 271 and 433.

```text
nominal exact formula instances: 1,637,634,348
exact carry decoders:            0
```

This is a bounded toy result, not a secp256k1 impossibility theorem.

## Decoder-class consequence

Move the following class from open to bounded/closed:

```text
bounded-pole translated-coordinate C3 determinants and their declared complete two-pullback additive pencils.
```

Do not continue by adding a third arbitrary coordinate term without a new exact mechanism.  The next admissible object must leave the translated bounded-pole coordinate category, most naturally through a genuinely different theta characteristic or Heisenberg/metaplectic intertwiner.

## Claim boundary

No carry, hard-R3, parity, scalar-recovery, or sub-square-root ECDLP algorithm is obtained.
