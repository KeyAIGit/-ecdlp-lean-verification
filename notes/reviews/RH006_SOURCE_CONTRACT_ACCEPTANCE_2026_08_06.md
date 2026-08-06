# RH-006 source-contract acceptance record

Date: 2026-08-06

Baseline: repository `main` at `7bf13abd618abf187e3b9446ab0fb61002eae6a6`.

Decision: **ACCEPT WITH APPLIED AMENDMENTS**.

This record accepts the source-semantics surface of
`domains/riemann-hypothesis/SOURCE_CONTRACTS.md` after the complete replay in
`RH006_SOURCE_REPLAY_2026_08_06.md`. It does not accept a Lean implementation,
discharge a formal or research obligation, select an RH route, or claim
progress on RH.

## Coverage disposition

| source | replayed | confirmed | amended | open |
|---|---:|---:|---:|---:|
| `LAG07` | 27 | 26 | 1 | 0 |
| `BOM-CLAY` | 12 | 12 | 0 | 0 |
| `BD02-v2` | 20 | 19 | 1 | 0 |
| **total** | **59** | **57** | **2** | **0** |

The accurate completion statement is **59/59 rows dispositioned: 57
confirmed, 2 amended**. The two historical replay discrepancies remain in the
replay table as review evidence; they are not relabelled as confirmations.

## Applied amendment A: `SC-WEIL-01`

The pinned `LAG07` source names the linear involution

```text
tilde(G)(s) = G(1-s).
```

The Hermitian pairing in (3.1) instead contains the conjugate-adjoint
reflection

```text
J(G)(s) = conj(G(1-conj(s))).
```

The contract now quotes the source-named tilde exactly and introduces `J`
separately as `DERIVED` contract notation. Appendix (A.7) supports the
Mellin-side realization of the operation used in the pairing; it does not
rename `J` as the source's tilde. The pairing, analytic multiplicity,
absolute-convergence, and sesquilinearity claims are unchanged.

Independent mathematical replay also checked that `J` preserves the class
`A`: it preserves the open strip and imaginary part, conjugation of the
reflected local series preserves holomorphicity, its growth argument is
uniformly comparable, and direct expansion gives `J(J(G)) = G`.

## Applied amendment B: `SC-NB-04`

The pinned `BD02-v2` PDF literally prints

```text
K := L2((infinity,infinity), (2*pi)^(-1/2) dt).
```

Equation (2.6) then uses `tau`. The contract now quotes `dt` literally and
identifies `tau` only as a bound-variable renaming. With
`g(u) = exp(u/2) * f(exp(u))`, the transform is the unnormalized Fourier
transform of `g`, so Plancherel gives

```text
||f||_H^2 = (1/(2*pi)) * integral_R |M0(f)(tau)|^2 d tau.
```

Therefore the formal target `L2_C(R, d tau/(2*pi))` is unchanged and remains
a derived normalization, not a literal transcription of the faulty display.

## Gate result

No source discrepancy remains open among the 59 replayed rows. `RH-006` is
complete, and the source-contract prerequisite for the xi package is
satisfied.

The next gate is independent acceptance of
`XI_PACKAGE_CONTRACT.md`. Until that acceptance has its own dated record,
promotion of `drafts/RiemannXi.lean` to a built module is not authorized.
Kernel build, no-incomplete-proof checks, ledger coverage, registry generation,
and both axiom audits remain mandatory in the later promotion change.
