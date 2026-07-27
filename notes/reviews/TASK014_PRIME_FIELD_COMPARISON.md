# TASK-014 prime-field Semaev comparison

Date: 2026-07-26
Updated: 2026-07-27 under TASK-015

Status: source-bounded desk comparison. It authorizes no solver run, target
computation, route promotion, or security claim.

## TASK-015 post-closeout addendum

TASK-014 closed on 2026-07-26. The WCC 2017 source boundary, two comparison
rows, and the corresponding disposition clarification below were added on
2026-07-27 under TASK-015. They do not reopen or retroactively extend the
TASK-014 contract.

## Evidence boundary

- Petit, Kosters, and Messeng 2016 is bound to the inspected primary PDF and
  claim extract in `data/source_claim_extracts/petit_kosters_messeng2016.json`.
- Amadori, Pintore, and Sala is bound to the inspected accepted manuscript and
  claim extract in `data/source_claim_extracts/amadori_pintore_sala2018.json`.
- Yokoyama, Yasuda, Takahashi, and Kogure is bound to the final publisher PDF
  and claim extract in
  `data/source_claim_extracts/yokoyama_yasuda_takahashi_kogure2020.json`.
- Yokota, Kudo, and Yasuda, *Practical Limit of Index Calculus Algorithms for
  ECDLP over Prime Fields*, is bound to the inspected WCC 2017 author PDF and
  claim extract in
  `data/source_claim_extracts/yokota_kudo_yasuda2017_wcc.json`.
- Kudo, Yokota, Takahashi, and Yasuda remains metadata-only. The row below
  deliberately records unknowns instead of reconstructing CANS 2018 from its
  title, abstract, or the separate WCC precursor.
- P3 and P4 are historical repository experiments. Their exact scopes are
  recorded in their own `README.md`, `RESULTS.md`, run manifests, and
  validators.

## Comparison matrix

| Construction | New premise | Information source | Exact mechanism represented here | Relation and solver model | Recovery and total-cost claim | Main limitation | secp256k1 applicability |
|---|---|---|---|---|---|---|---|
| Naive Semaev | A random factor-base variety `V` of the form assumed by the source | Factor-base coordinates and Semaev relations | Point-decomposition ideal for a random `V` | Gröbner computation with S-polynomials; Proposition 9 gives a conditional almost-every-target operation lower bound | Recovery still requires enough usable relations and linear algebra; no end-to-end sub-generic algorithm follows | Assumption 7 and the non-rigorous transfer in Remark 8 are load-bearing; the result is an operation bound, not a solving-degree theorem | Structural baseline only. The bound cannot be transferred automatically to structured Petit, Amadori, or unread Kudo systems |
| Amadori et al. | Random points `R=uP+vQ` form the factor base and one system replaces repeated decompositions plus final sparse linear algebra | Stored `(u,v)` coefficients and a recovered point relation | One summation-polynomial system encoding the accumulated factor-base points | Single-system cost `T'` is compared with the Petit-style cost `T` using the unproved approximation `T approximately T'` | A recovered relation yields a linear congruence for the logarithm; the paper claims only a conditional fixed-`m` comparison with Petit and explicitly does not claim work below `p^(1/2)` | Solving cost is unestimated; experiments cover only 11-22-bit primes and `m` in `{3,4,5}` | Mechanism is defined over prime fields, but no cryptographic-scale cost bridge is established |
| WCC 2017 p-minus-one study | `m=2`, `N=2^r` divides `p-1`, and `N` is approximately `p^(1/2)` on selected favorable primes | Petit-style multiplicative roots and Semaev relations | Original, symmetric, hybrid, resultant or GCD, and exhaustive presentations | Single-machine Magma measurements on 12.1-22.0-bit primes; exhaustive `k=1` is lowest in every Table 1 row, but Table 2 has lower resultant or GCD times at 12.1, 14.1, and 16.0 bits; Gröbner variants show severe memory growth | The source measures practicality only and explicitly disclaims asymptotic analysis | The all-quadratic `m=2` chain and selected primes do not model secp256k1 `m=16`, its degree-13441 component, or S17 | Bounded prior art only. Timings and speedup factors cannot be transferred to secp256k1 |
| WCC 2017 p-plus-one trace extension | `p+1` has a smooth factor and, in the low-degree presentation, `p` is congruent to 3 modulo 4 with `m=2` | `N`-th roots of unity in the quadratic extension followed by the field trace | Trace-derived factor-base coordinates and the low-degree systems (9)-(10) | Experiments cover only 5.6-10.1-bit primes and stop because of memory | No asymptotic or cryptographic-scale claim | This is not the PKC auxiliary elliptic curve and self-isogeny mechanism | It does not decide `TP-SECP-PKC-AUXILIARY-CURVE` |
| Kudo et al. | Unknown from the unread full text | Springer metadata and abstract only | Not represented | Unknown | Unknown | Full text has not been lawfully obtained and inspected; no novelty or performance comparison may depend on this row | Unresolved |
| Petit direct smooth subgroup | `p-1` has a sufficiently large smooth divisor and the resulting composed map is constructible | Roots from a multiplicative subgroup or coset | Low-degree rational-map composition defining `L(x)=0` | Expected decompositions per target are modeled heuristically as `(deg L)^m/(m!p)`; total relation generation also depends on the unresolved system cost `T(E,m,L)` | Generalized-root solving, relation collection, recovery, independence, preprocessing, and sparse linear algebra all remain in the total cost | The source gives a partial unit-cost analysis, not an end-to-end advantage theorem | For the known secp256k1 divisor `D=564522`, both the raw size threshold and the source's heuristic balance first pass at `m=16`; this is applicability only |
| Petit auxiliary curve | An auxiliary curve over the same field has a large smooth-order factor and a usable self-isogeny | Roots induced by the auxiliary curve and its map | Auxiliary-curve composed rational map defining the target factor-base coordinates | Same Semaev relation layer, plus auxiliary-curve search and map construction | Search, map construction, generalized roots, recovery, relation independence, and linear algebra are unpriced | No concrete secp256k1 auxiliary curve and full-cost candidate is retained in this cycle | Parked, not ruled out |
| Historical P3 | A finite x-coordinate set is encoded by `f_F(X)=0` | Explicit toy factor-base coordinates | Raw finite-set system `{S_(m+1)=0, f_F(X_i)=0}` and a redundant coupled `u=x^3` presentation | Custom graded Macaulay proxy; relation sets independently replayed by brute-force EC arithmetic | Descriptive toy measurements only; no exact degree-of-regularity or asymptotic claim | Proxy stopping rule lacks external F4/GB validation; toy sizes, raw factor base, and no faithful Petit map | Historical scoped evidence only |
| Historical P4 | A toy composed polynomial map approximates a low-degree factor-base presentation | Explicit auxiliary variables and map parameters | Two six-variable polynomial-map presentations at `m=2`, neither faithful to PKC 2016 | Same custom P3 proxy; relation sets independently reconstructed and replayed | At one `|F|=4` point, a lower proxy degree came with much larger matrices and time; no growth or no-go claim | Not rational, no smooth subgroup or auxiliary curve, no PKC recovery semantics, and one toy scale | Historical approximation only |

## Desk disposition

The direct secp256k1 smooth-subgroup instance is retained only as a precise
arithmetic applicability result. Passing the two size predicates at `m=16`
does not supply the missing representation-level, solver, recovery,
relation-independence, sparse-linear-algebra, or amortization costs. The direct
instance therefore does not justify a native experiment.

The auxiliary-curve construction remains parked because no finite,
source-defined search family and no exact retained candidate close its curve
search, map, generalized-root, recovery, and full-cost obligations. WCC 2017's
p-plus-one trace construction is a different mechanism and cannot fill that
gap. CANS 2018 remains an explicit acquisition blocker. The historical P3/P4
measurements cannot substitute for either faithful construction.

No candidate passes the prerequisites for TASK-014 Phase D. The connected
GLV/Semaev workstream is also left without Lean work: the available review is
not source-independent, and the proposed statement is not decision-critical
after the coordinatewise-cube mechanism was closed.
