# RH-006 source-contract replay record

Date: 2026-08-06

Scope: the `RH-006` output — a statement-by-statement second-agent replay of
`domains/riemann-hypothesis/SOURCE_CONTRACTS.md` against the three
SHA-256-pinned PDFs (checksums re-verified 2026-08-05,
`notes/reviews/RH_SOURCE_PDF_CHECKSUM_REPLAY_2026_08_05.md`). Three
independent agents replayed one source each, reading the PDFs page-by-page
(text extraction cross-checked against rendered page images for every sign-
and overline-sensitive display); a fourth agent produced the coverage
checklist from the contract side. **No contract text is edited by this
task** — discrepancies are recorded for the external reviewer to amend.

## Verdict summary

| source | rows replayed | confirmed | discrepancies |
|---|---|---|---|
| `LAG07` (Ann. Inst. Fourier 57 (2007), 53 pp.) | 27 | 26 | **1 (load-bearing)** |
| `BOM-CLAY` (Clay official description, 11 pp.) | 12 | 12 | 0 |
| `BD02-v2` (arXiv math/0202141v2, 7 pp.) | 20 | 19 | 1 (cosmetic) |

Total: **59 rows replayed; 57 confirmed; 2 discrepancies**.

Every normative locator in the contract's pinned-source table exists at the
stated place; the final-publication `LAG07` theorem numbering matches the
contract's (the arXiv-numbering warning stands).

## Discrepancy 1 (load-bearing): `SC-WEIL-01` involution attribution

Contract: attributes to `LAG07` the involution
`tilde(G)(s) = conj(G(1 - conj(s)))`.

Source (printed p. 1704, image-verified; cf. (A.1)-(A.2) p. 1735, (A.7)
p. 1737): "The class `A` is closed under the action of the involution
`G~(s) := G(1 - s)`" — **no conjugation**; the appendix Mellin-side
involution (A.2) is likewise `f^~(s) = f^(1-s)`. The conjugated reflection
`conj(G(1 - conj(s)))` occurs in the Hermitian pairing (3.1), and Appendix
(A.7) realizes the same operation as the Mellin transform of "tilde of
g-bar". It is never LAG07's named tilde involution.

Assessment: mathematically, `A` is closed under both maps, and the
conjugated reflection is the operationally relevant one for the Hermitian
pairing (3.1) — but as a transcription of the source's named involution the
contract line is wrong. Required amendment: quote the source involution as
`G(1-s)`; introduce `J(G)(s) = conj(G(1 - conj(s)))`, including closure of
`A` under `J`, as a contract-defined `DERIVED` object; and cite (3.1)/(A.7)
for its use in the pairing. Until amended, no Lean statement may cite the
current `SC-WEIL-01` involution line as `SOURCE`.

**Amendment disposition (2026-08-06): resolved.** `SOURCE_CONTRACTS.md` now
quotes the source-named tilde as `G(1-s)`, introduces `J` separately as a
`DERIVED` conjugate-linear involution preserving `A`, and cites (3.1)/(A.7)
only for its operational use. The pairing and its multiplicity, convergence,
and sesquilinearity claims are unchanged.

## Discrepancy 2 (cosmetic): `SC-NB-04` erratum-2 quotation

The substantive erratum is real — the PDF typesets the K-display measure
with exponent `-1/2` (`(2pi)^(-1/2) dt`) where Plancherel requires
`(2pi)^(-1)`. But the contract quotes the erratum letterform as
`(2*pi)^(-1/2) d tau` while the PDF letter is `dt` (the source itself uses
`tau` in (2.6) and `t` in the K display — a further internal inconsistency
the contract's quote silently normalizes). Suggested amendment: quote the
source measure as `(2pi)^(-1/2) dt`.

**Amendment disposition (2026-08-06): resolved.** `SOURCE_CONTRACTS.md` now
quotes `(2*pi)^(-1/2) dt` literally, treats `tau` only as the formal
bound-variable renaming used in (2.6), and retains the independently derived
Plancherel measure `d tau/(2*pi)`. No formal obligation or route conclusion
changes.

## Notable confirmations (selection)

- `LAG07` (2.7) factor-2 normalization and the prose "This convention is
  forced if we wish to have entire functions in all cases" — confirmed
  verbatim (p. 1697).
- The genus-one Hadamard product and `A(pi) = -sigma_1` live in the PROOF of
  Lemma 4.1 (p. 1707), not its statement — consistent with the contract's
  citation practice.
- `SC-LI-02`'s boundary caveat is genuinely needed: the definition (1.1)
  uses `|rho| <= T` while the Lemma 2.3 proof uses `|rho| < T`, and (2.11)
  counts with `0 <= Im rho < T` above / `-T <= Im rho <= 0` below — the
  source is mixed on boundary conventions, exactly as the contract warns.
  The (2.11) cutoff is on `Im(rho)`, not `|rho|`; the contract correctly
  carries the conversion as a `FORMAL-OBLIGATION`.
- `BOM-CLAY` trace formula: every term, sign, and the strict `|Im rho| < T`
  cutoff confirmed against rendered displays; the autocorrelation uses
  ordinary `dy`; the contract's claim that the source does NOT prove
  `W`-closure under autocorrelation is confirmed (no such proof in §V).
- `BD02-v2`: erratum 1 (target interval typeset `(infinity, infinity)`)
  confirmed exactly as recorded; the raw Mobius family's divergence in `H`
  is the source's own statement; the repeated-gamma-factor typesetting error
  in the v2 Lemma 2.2 proof is confirmed present.


## Row-level replay: LAG07

| contract item | source locator | verdict | evidence |
|---|---|---|---|
| Local pinned source table row for LAG07 (bibliographic identity, SHA-256, normative locators list) | PDF cover page (PDF p.1) and whole document; printed pp. 1689-1740 | **CONFIRMED** | The cover, publication identity, 53-page extent, and SHA-256 `d1c3175591daff6a7f7503c8452eee0ce2536280cb9ce468a6c0a159be4d9f9b` match the pin. Every listed locator from §1 through Appendix A exists with the final-publication numbering used by the contract. |
| (2.7) normalization xi(s, pi_triv) = 2*xi_classical(s) | Eq. (2.7) and following paragraph, printed p. 1697 (PDF p.10); xi_classical display printed p. 1690 (PDF p.3) | **CONFIRMED** | Directly below (2.7), LAG07 states `e(0,pi_triv) = e(1,pi_triv) = -1` and `xi(s,pi_triv) = 2 xi(s)`, with the convention forced by entirety. Printed p. 1690 defines the classical `xi(s) = (1/2) s(s-1) pi^(-s/2) Gamma(s/2) zeta(s)`. |
| SC-XI-01: Theorem 2.1(3) critical-strip localization | Theorem 2.1(3), printed p. 1698 (PDF p.11) | **CONFIRMED** | 'The zeros of Lambda(s,pi) all lie in the open critical strip 0 < Re(s) < 1. In particular Lambda(s,pi) is non-vanishing on the lines Re(s) = 0 and Re(s) = 1.' |
| SC-XI-01: Theorem 2.1(4), the (2.11) zero-counting asymptotic | Theorem 2.1(4), eq. (2.11)-(2.12), printed p. 1698 (PDF p.11) | **CONFIRMED** | 'The counting function N+_pi(T) (resp. N-_pi(T)) for zeros of Lambda(s,pi) with 0 <= Im(rho_pi) < T (resp. -T <= Im(rho_pi) <= 0) each satisfy (2.11) N±_pi(T) = (N/2pi) T log T + (1/2) C0(pi) T + O(log T) as T -> infinity', with C0(pi) = (1/pi) log Q(pi) - (N/pi)(1+log(2pi)); O-constant depends on pi. Two-sided as the contract says. |
| SC-XI-01: Theorem 2.1(6) entire order one | Theorem 2.1(6), printed p. 1698 (PDF p.11) | **CONFIRMED** | 'The function xi(s,pi) is an entire function of order one and maximal type. It is bounded in vertical strips -B < Re(s) < B for any finite B, and has rapid decrease there as \|Im(s)\| -> infinity.' |
| SC-XI-01: Lemma 2.2 power-sum convergence | Lemma 2.2, eq. (2.16), printed p. 1701 (PDF p.14) | **CONFIRMED** | 'the power sums sigma_n(pi) := sum'_{rho in Z(pi)} 1/rho^n, n >= 1, are absolutely convergent for n >= 2, and are *-convergent for n = 1. The real parts of these sums are absolutely convergent for all n >= 1.' Z(pi) is defined just above as 'the multi-set of zeros of xi(s,pi) (counted with multiplicity)'. |
| SC-XI-01: Lemma 4.1 and genus-one Hadamard factorization with A_xi = -starSum m(rho)/rho | Lemma 4.1 and its proof, printed p. 1707 (PDF p.20) | **CONFIRMED** | Lemma 4.1 states the expansion (4.1) xi'/xi(s+1,pi) = sum (-1)^n sigma_{n+1}(pi^vee) s^n. Its proof contains: 'Since xi(s,pi) is entire of order one we have the Hadamard product expansion xi(s,pi) = e^{A(pi)s + B(pi)} prod_{rho in Z(pi)} (1 - s/rho) e^{s/rho}', and 'One can also deduce by a *-convergent rearrangement that A(pi) = -sum'_{rho in Z(pi)} 1/rho = -sigma_1(pi)'. |
| SC-LI-01: (1.6) summability hypothesis | Eq. (1.6), printed p. 1691 (PDF p.4) | **CONFIRMED** | LAG07 introduces an arbitrary multiset `Z` satisfying `sum Re(rho)/(1+\|rho\|)^2 < infinity`. Thus (1.6) is a hypothesis of the abstract Bombieri-Lagarias criterion, not a theorem there about the Riemann-xi zero multiset; multiplicity is carried by multiset membership. |
| SC-LI-01: star convergence of sum' m(rho)/rho | Text before eq. (1.8), printed p. 1691 (PDF p.4) | **CONFIRMED** | 'Finally, if Z omits the values 0 and 1 and the sum sum_{rho in Z} 1/rho is *-convergent, then the coefficients lambda_n(Z) are well-defined for all integers n by the following *-convergent sum: (1.8) lambda_n(Z) := sum'_{rho in Z} (1 - (1 - 1/rho)^n).' |
| SC-LI-02: (1.1)/(1.8) cutoff \|rho\| <= T, multiplicity mandatory, star limit, lambda_0 = 0, both integer signs | Eq. (1.1) and surrounding text, printed p. 1690 (PDF p.3); eq. (1.8) p. 1691 | **CONFIRMED** | The prime means `lim_{T->infinity} sum_{\|rho\| <= T}`, zeros are counted with multiplicity, and LAG07 calls this star convergence. The text admits positive and negative integer indices, records `lambda_0 = 0`, and (1.8) gives the corresponding abstract-multiset definition. |
| SC-LI-02: contract note that proofs occasionally use < T | Proof of Lemma 2.3, printed p. 1702 (PDF p.15) | **CONFIRMED** | The Lemma 2.3 proof opens with 'sum_{\|rho\| < T} [1 - (1 - 1/rho)^n] = sum_{\|rho\| < T} n/rho + ...' using the STRICT cutoff \|rho\| < T, whereas the definition (1.1) uses \|rho\| <= T. The contract's boundary-insensitivity caveat is therefore accurate and needed. |
| SC-LI-03: (1.3) local derivative formula | Eq. (1.3), printed p. 1690 (PDF p.3) | **CONFIRMED** | '(1.3) lambda-tilde_n := (1/(n-1)!) (d^n/ds^n)[s^{n-1} log xi(s)]\|_{s=1}, n >= 1.' Matches the contract's localLambda_n definition exactly (factorial, power s^{n-1}, evaluation at s = 1, n >= 1). |
| SC-LI-03: relation localLambda_n = lambda_(-n) | Text after (1.3), printed p. 1690 (PDF p.3) | **CONFIRMED** | The source states `localLambda_n = lambda_(-n)` for `n > 0`; equality with `lambda_n` then uses the zeta-specific symmetry (1.2). The contract therefore correctly forbids replacing the negative-index coefficient before the required symmetry and reality facts are proved. |
| SC-LI-04: Theorem 2.4 one-sided criterion with rho -> 1-conj(rho) invariance | Theorem 2.4 and (2.20), printed p. 1702 (PDF p.15); Theorem 2.1(5), printed p. 1698 (PDF p.11) | **CONFIRMED** | Theorem 2.4 makes `Re(lambda_n(pi)) >= 0` for every positive `n` equivalent to RH for `xi(s,pi)`. Its proof explicitly uses that `Z(pi)` omits `0,1` and is invariant under `rho -> 1-conj(rho)`, exactly the symmetry prerequisite retained by the contract. |
| SC-WEIL-01: class A and the O(1/\|s\|) bound for \|im s\| >= 1 | Class-A definition paragraph, printed p. 1704 (PDF p.17); L-subset-A passage, printed p. 1705 (PDF p.18) | **CONFIRMED** | Definition: 'the vector space A of all functions F(s) holomorphic in the strip 0 < Re(s) < 1 which satisfy a uniform growth bound F(s) = O(1/\|s\|) in the strip outside(2) the region \|Im(s)\| <= 1, with O-constant depending on the function.' Later, p. 1705: 'the vanishing condition at infinity implies a bound F(s) = O(1/\|s\|) uniformly in the region \|Im(s)\| >= 1.' |
| SC-WEIL-01: pre-amendment involution attribution `tilde(G)(s) = conj(G(1 - conj(s)))` | Class-A paragraph and (3.1), printed p. 1704 (PDF p.17); (A.1)-(A.2), p. 1735; (A.7), p. 1737 | **DISCREPANCY — RESOLVED 2026-08-06** | LAG07's named involution is `tilde(G)(s) = G(1-s)`, with no conjugation; the amended contract now quotes it exactly. The separately named derived adjoint reflection `J(G)(s) = conj(G(1-conj(s)))` occurs in (3.1) and is realized in (A.7) as the Mellin transform of "tilde of g-bar". |
| SC-WEIL-01: (3.1) definition, multiplicity, absolute convergence, sesquilinearity | Eq. (3.1) and following paragraph, printed p. 1704 (PDF p.17) | **CONFIRMED** | '(3.1) <F,G>_{W(pi)} := sum_{rho in Z(pi)} F(rho) conj(G(1 - conj(rho))).' (rendered image shows the overline spanning G(1-rho-bar)). 'The sum on the right counts zeros with multiplicity, and it converges absolutely due to the growth bound on F and G for large \|s\|. This scalar product is linear in the first factor and conjugate-linear in the second factor.' |
| SC-WEIL-02: Li class L and (3.2) G_n definition | Li-class paragraph and eq. (3.2), printed p. 1705 (PDF p.18) | **CONFIRMED** | 'We define the Li class L of test functions to be the set of rational functions in the function field C(s) that vanish at infinity (on the Riemann sphere) and whose polar divisor is contained in the set {0, 1}.' '(3.2) G_n(s) := 1 - (1 - 1/s)^n for n in Z.' Also: 'every nonzero member of it has a pole at either s = 0 or s = 1, or both.' |
| SC-WEIL-02: Theorem 3.1 Gram identities | Theorem 3.1, eqs. (3.3)-(3.4), printed p. 1705 (PDF p.18), rendered image verified | **CONFIRMED** | '(3.3) <G_n, G_m>_{W(pi)} = lambda_n(pi) + lambda_{-m}(pi) - lambda_{n-m}(pi).' 'In particular (3.4) \|\|G_n\|\|^2_{W(pi)} = lambda_n(pi) + lambda_{-n}(pi) = 2 Re(lambda_n(pi)).' No conjugation bars on any lambda term (image-verified). The proof runs all three sums under one common star-sum before splitting, supporting the contract's common-cutoff requirement. |
| SC-BRIDGE-01: (A.3) W[f] definition with \|rho\| <= T star limit | Eq. (A.3) and following line, printed pp. 1735-1736 (PDF pp.48-49) | **CONFIRMED** | '(A.3) W[f] := sum'_{rho: xi(rho)=0} f-hat(rho), in which prime means that the (possibly conditionally convergent) sum is interpreted as lim_{T->infinity} sum_{\|rho\| <= T}.' |
| SC-BRIDGE-01: (A.4) trace functional | Eq. (A.4), printed p. 1736 (PDF p.49) | **CONFIRMED** | '(A.4) T[f] := f-hat(0) - W[f] + f-hat(1).' Endpoint terms on the spectral side and minus sign on the zero contribution exactly as the contract states. |
| SC-BRIDGE-01: (A.5) trace form | Eq. (A.5), printed p. 1736 (PDF p.49) | **CONFIRMED** | '(A.5) T[f] = sum_nu W_nu(f), in which W_nu(f) is a contribution associated to each (non-archimedean or archimedean) place nu.' |
| SC-BRIDGE-01: (A.6) covariance rearrangement | Eq. (A.6), printed p. 1736 (PDF p.49); W_0/W_1 definitions p. 1737 (PDF p.50) | **CONFIRMED** | '(A.6) W[f] = -sum_nu W_nu(f) + W_0(f) + W_1(f)', 'a rearrangement of the terms in the trace form equality', with W_0(f) := f-hat(0) and W_1(f) := f-hat(1). |
| SC-BRIDGE-01: endpoint/sign bookkeeping and the Bombieri/Lagarias sign | (A.6) and discussion, printed pp. 1736-1737 (PDF pp.49-50) | **CONFIRMED** | Setting `W_0(f) = W_1(f) = 0` in (A.6) gives `sum_nu W_nu(f) = -W[f]`. This is exactly the contract's derived one-sign conversion between the Bombieri arithmetic form and Lagarias zero-side positivity. |
| SC-BRIDGE-02: LAG07 side of the cutoff conversion (\|rho\| <= T) | Eq. (1.1) text, printed p. 1690 (PDF p.3); (A.3) prime-convention, printed p. 1736 (PDF p.49) | **CONFIRMED** | Both LAG07 star-limits are radial and non-strict: (1.1) 'lim_{T->infinity} sum_{rho: \|rho\| <= T}' and (A.3) 'lim_{T->infinity} sum_{\|rho\| <= T}'. The contract's claim that Lagarias uses \|rho\| <= T is exact; the Bombieri \|im(rho)\| < T half belongs to BOM-CLAY and was not audited here. |
| SC-BRIDGE-03/04: Li functions require the common-cutoff covariance regularization | Appendix A closing discussion, printed pp. 1737-1738 (PDF pp.50-51); Li-class description p. 1705 (PDF p.18) | **CONFIRMED** | LAG07 says the Li class is valid for the extended covariance form, not the trace form, and `T[f]` is undefined for every Li test function. It redefines the right side of (A.6) as `T -> infinity` with local cutoffs `1/T` and `T`, and states that the divergent endpoint contribution is offset by a corresponding finite-prime divergence. |
| Final-publication theorem/equation numbering matches the contract (arXiv-divergence warning) | Whole document, printed pp. 1689-1740 | **CONFIRMED** | In this final Numdam publication every citation resolves at the contract's number: Theorem 2.1 (items (1)-(6), containing (2.8)-(2.15)), Lemma 2.2 with (2.16), Lemma 2.3 with (2.17)-(2.19), Theorem 2.4 with (2.20)-(2.22), Theorem 3.1 with (3.3)-(3.4), Lemma 4.1 with (4.1), Appendix A with (A.1)-(A.7), and §1 with (1.1)-(1.8). No cited label is missing or attached to different content. |

## Row-level replay: BOM-CLAY

| contract item | source locator | verdict | evidence |
|---|---|---|---|
| SC-BOMB-01 test class W: regularity and first-kind discontinuities with midpoint values | BOM-CLAY printed p. 8, §V, second paragraph | **CONFIRMED** | "Consider the class W of complex-valued functions f(x) on the positive half-line R+, continuous and continuously differentiable except for finitely many points at which both f(x) and f'(x) have at most a discontinuity of the first kind, and at which the value of f(x) and f'(x) is defined as the average of the right and left limits there." Verified both in extracted text and rendered image. |
| SC-BOMB-01 decay bounds with delta > 0 | BOM-CLAY printed p. 8, §V, same paragraph | **CONFIRMED** | "Suppose also that there is delta > 0 such that f(x) = O(x^delta) as x -> 0+ and f(x) = O(x^(-1-delta)) as x -> +infinity." Exponents match the contract exactly (x^delta at 0+, x^(-1-delta) at infinity). |
| SC-BOMB-01 Mellin convention and analyticity strip | BOM-CLAY printed p. 8, displayed formula after 'Let f~(s) be the Mellin transform' | **CONFIRMED** | f~(s) = integral_0^infinity f(x) x^s dx/x, "which is an analytic function of s for -delta < Re(s) < 1 + delta." Exponent convention x^s dx/x (not x^(s-1) dx notationally, though equal) and strip both match the contract verbatim. |
| SC-BOMB-02 von Mangoldt definition Lambda(n) = log p iff n = p^a, else 0 | BOM-CLAY printed p. 8, line before 'Explicit Formula' | **CONFIRMED** | "Let Lambda(n) = log p if n = p^a is a power of a prime p, and 0 otherwise." Matches the contract's 'prime p and a : N with 1 <= a and n = p^a' (a power of a prime has exponent >= 1); sum in the formula starts at n = 1, matching the contract's sum_{n >= 1}. |
| SC-BOMB-02 trace explicit formula: term placement and signs | BOM-CLAY printed p. 8, boxed display "Explicit Formula. For f in W we have" | **CONFIRMED** | The display places `Mellin(f)(0) - sum_rho Mellin(f)(rho) + Mellin(f)(1)` on the spectral side. The prime-power, `(log(4*pi)+gamma) f(1)`, and archimedean integral terms are on the right with the signs and denominator `x - x^(-1)` recorded by the contract. |
| SC-BOMB-02 zero-sum meaning: strict cutoff \|im(rho)\| < T, T -> +infinity | BOM-CLAY printed p. 8, display immediately after the Explicit Formula | **CONFIRMED** | "Here the first sum ranges over all nontrivial zeros of zeta(s) and is understood as lim_{T -> +infinity} sum_{\|Im(rho)\| < T} f~(rho)." The cutoff is printed with a STRICT < on \|Im(rho)\|, exactly as the contract states, and T -> +infinity through positive values. |
| SC-BOMB-02 multiplicity is implicit in §V | BOM-CLAY printed p. 8, §V zero-sum display | **CONFIRMED** | The printed sum is sum_{\|Im(rho)\| < T} f~(rho) with no multiplicity factor m(rho) anywhere in §V; the phrase is only 'ranges over all nontrivial zeros of zeta(s)'. The contract's claim that §V 'leaves it implicit' is accurate — the contract's m(rho) is its own annotation, correctly flagged as not printed in the source. |
| SC-BOMB-03 autocorrelation with ordinary dy and conjugate on g(y) | BOM-CLAY printed p. 9, first display of the page | **CONFIRMED** | Rendered image shows f(x) = integral_0^infinity g(xy) overline{g(y)} dy with an overline (complex conjugate) on g(y) and ordinary measure dy — NOT dy/y. (The conjugation bar is invisible in plain text extraction; confirmed by rasterizing the display at 6x zoom.) |
| SC-BOMB-03 two vanishing moment conditions | BOM-CLAY printed p. 9, second display | **CONFIRMED** | "whenever g in W satisfies the additional conditions integral_0^infinity g(x) dx/x = integral_0^infinity g(x) dx = 0." Both conditions printed; under the p. 8 Mellin convention these are exactly Mellin(g)(0) = 0 and Mellin(g)(1) = 0, matching the contract's equivalent restatement (which the contract does not attribute as printed). |
| SC-BOMB-03 Mellin factorization Mellin(f_g)(s) = Mellin(g)(s) * conj(Mellin(g)(1 - conj s)) | Not present anywhere in BOM-CLAY (checked all 11 pages; 'Mellin' appears only on printed p. 8) | **CONFIRMED** | The source never states this factorization; §V passes directly from the moment conditions to the geometric (finite-field) analogy. The contract labels this identity DERIVED 'after the required integral and interchange justifications', not SOURCE — that labeling is correct. |
| SC-BOMB-03 negativity direction: RH iff Q_B(f_g) <= 0, non-strict | BOM-CLAY printed p. 9, lines 1-3 and the Algebraic Index Theorem statement | **CONFIRMED** | "Weil also proved that the Riemann hypothesis is equivalent to the negativity of the right-hand side for all functions f(x) of type [autocorrelation], whenever g in W satisfies the additional conditions [moments]." Direction matches: RH <-> sign condition on the arithmetic right-hand side over the autocorrelation class. |
| Contract claim: source does NOT prove closure of W under autocorrelation | BOM-CLAY printed pp. 8-9 (entire §V); full-document replay of all 11 pages | **CONFIRMED** | §V neither proves that `f_g` belongs to `W` nor supplies the integrability and Fubini argument needed for its Mellin factorization. The contract correctly keeps that regularity bridge as a `FORMAL-OBLIGATION` instead of importing it from the source. |

## Row-level replay: BD02-v2

| contract item | source locator | verdict | evidence |
|---|---|---|---|
| SC-NB-01 Hilbert space H = L2((0,infinity), dx) | p.1, Introduction, display 'H := L2(0, infinity)' | **CONFIRMED** | PDF p.1: 'We shall be working in the Hilbert space H := L2(0, infinity)'. Lebesgue measure dx is implicit in the source; contract makes it explicit. |
| SC-NB-01 rho(x) = x - floor(x) and rho_a(x) = rho(1/(a*x)), a real, 1 <= a | p.1, abstract and Introduction display 'rho_a(x) := rho(1/(ax))' | **CONFIRMED** | PDF p.1: 'We denote the fractional part of x by rho(x) = x - [x]'; 'linear hull of the family {rho_a \| 1 <= a in R} with rho_a(x) := rho(1/(ax))'. Abstract states the same with 'a >= 1'. |
| SC-NB-01 chi = 1_(0,1] with abstract-vs-body (0,1) vs (0,1] note | p.1, abstract line 1 vs Introduction line 2 | **CONFIRMED** | Abstract typesets 'chi = chi_(0,1)' (open interval subscript, verified in rendered image); body says 'let chi stand for the characteristic function of the interval (0, 1]'. Exactly the abstract-vs-body split the contract records; the two indicators agree a.e. as the contract notes. |
| SC-NB-01 B = span{rho_a \| a real, 1 <= a}, B_nat = span{rho_a \| a positive natural} | p.1, Introduction | **CONFIRMED** | PDF p.1: B 'defined as the linear hull of the family {rho_a \| 1 <= a in R}'; 'The much smaller subspace B^nat of natural Beurling functions is generated by {rho_a \| a in N}'. Source writes the natural subspace as B^nat (superscript), contract as B_nat (cosmetic). Source says 'a in N'; the positive-natural reading is forced since rho_a requires a >= 1 (abstract) and rho_0 is undefined. |
| SC-NB-02 Theorem 1.1: RH <-> chi in closure(B_nat), both directions | p.1, Theorem 1.1 | **CONFIRMED** | PDF p.1: 'Theorem 1.1. The Riemann hypothesis is equivalent to the statement that chi in overline(B^nat)'. The overline (closure bar) on B^nat is visually confirmed in the rendered page image (text extraction drops it). Equivalence = both implications. |
| SC-NB-02 classical Nyman-Beurling criterion quoted in the introduction (closure(B)->RH edge) | p.1, Introduction, display `chi in closure(B)` | **CONFIRMED** | The introduction states RH equivalent to `chi in closure(B)`; the closure bar is image-verified. Together with `B_nat <= B`, this supplies exactly the reverse implication used by the contract. |
| SC-NB-03 Mellin identity -zeta(s)/s = integral_0^infinity x^(s-1) rho_1(x) dx for exactly 0 < re(s) < 1 | p.4, unnumbered display between (2.6) and (2.7), attributed to Titchmarsh [15] (2.1.5) | **CONFIRMED** | PDF p.4: '-zeta(s)/s = integral_0^infinity x^(s-1) rho_1(x) dx, (0 < Re(s) < 1)'. Strip condition matches the contract exactly. |
| SC-NB-03 a-scaled version: integral x^(s-1) rho_a(x) dx = -a^(-s) zeta(s)/s | p.4, implicit in the step from the Titchmarsh identity to (2.7) | **CONFIRMED** | Substitution `y = a*x` gives the factor `a^(-s)`, and specialization to (2.7) reproduces its exponent `a^(1/2+epsilon+i*tau)`. The contract correctly presents this as a consequence of the displayed source identity, not as a verbatim source display. |
| SC-NB-04 M0(f)(tau) = integral_0^infinity x^(-1/2 + i*tau) f(x) dx | p.4, equation (2.6) | **CONFIRMED** | PDF (2.6): 'M(f)(tau) := integral_0^infinity x^(-1/2 + i*tau) f(x) dx', called the Fourier-Mellin map, asserted to be 'an invertible isometry from H to K'. |
| SC-NB-04 erratum 1: target interval typeset as (infinity, infinity) | p.4, display 'K := L2((infinity,infinity),(2pi)^(-1/2) dt)' after (2.5) | **CONFIRMED** | PDF p.4 literally typesets 'K := L2((infinity, infinity), (2pi)^(-1/2) dt)' with NO minus sign before the first infinity. Verified in two independent text extractors (pypdf, PyMuPDF) and visually in the rendered page image; minus signs elsewhere on the same page extract correctly, so this is not an extraction artifact. Intended is R = (-infinity, infinity). |
| SC-NB-04 erratum 2 (pre-amendment wording): measure typeset as (2*pi)^(-1/2) d tau | p.4, same K display | **DISCREPANCY — RESOLVED 2026-08-06** | The display literally has `(2*pi)^(-1/2) dt`; the contract now quotes that text exactly. Its formal `d tau` is only a bound-variable renaming, and the independently derived Plancherel measure `d tau/(2*pi)` is unchanged. |
| SC-NB-04 correct derivation gives L2(R, d tau/(2*pi)) | derived; source asserts isometry below (2.6), p.4 | **CONFIRMED** | Independent replay: with x = e^u, M(f)(tau) is the unnormalized Fourier transform of g(u) = e^(u/2) f(e^u), and \|\|f\|\|_H^2 = integral \|g\|^2 du = (2pi)^(-1) integral \|M(f)(tau)\|^2 d tau. So M is unitary H_C <-> L2_C(R, d tau/(2pi)), as the contract states; neither of the source's typeset K parameters ((infinity,infinity), (2pi)^(-1/2)) is literally correct. |
| SC-NB-05 Littlewood convergence sum mu(a) a^(-s) = 1/zeta(s) for re(s) > 1/2 under RH | p.3, sect. 2.1 first paragraph (citing [15] Theorem 14.25 (A)); reused p.4 after (2.7) | **CONFIRMED** | PDF p.3: 'the well-known theorem of Littlewood ... to the effect that under the Riemann hypothesis sum_{a=1}^infinity mu(a) a^(-s) converges to 1/zeta(s) for Re(s) > 1/2'. RH-dependent exactly as the contract's ledger tags it. |
| SC-NB-05 Lemma 2.1 zero-free specialization | p.3, Lemma 2.1 / (2.1); specialization p.5 top | **CONFIRMED** | Lemma 2.1 assumes zero-freeness on `Re(s) > alpha`. The proof then chooses `alpha = 1/2` and `delta = epsilon`, so this use is under the standing RH hypothesis, exactly as the contract's dependency ledger requires. |
| SC-NB-05 Lindelof estimates derived from RH | p.5, first paragraph after the specialized (2.1) | **CONFIRMED** | The proof explicitly invokes the Lindelöf hypothesis on `re(s) = 1/2-epsilon`, says it follows from RH, and obtains the displayed `K_epsilon (1+\|tau\|)^(-1+2*epsilon)` majorant. The contract's RH-dependent label is exact. |
| SC-NB-05 conditional closure membership versus unconditional final H-limit | p.5, proof after (2.9) through the final limit; Corollary 3.1, p.6 | **CONFIRMED** | Under the standing RH hypothesis, the source proves `f_(epsilon,n) -> f_epsilon` in `H` and `f_epsilon in closure(B_nat)` for small epsilon. It then explicitly says "without the assumption of the Riemann hypothesis" before deriving `f_epsilon -> -chi` in `H`. Corollary 3.1 separately restates the RH-equivalent fixed-epsilon convergence criterion. The contract correctly forbids combining the unconditional final limit with the conditional closure-membership step as though both were unconditional. |
| SC-NB-05 Lemma 2.2 unconditional zeta-ratio estimate (contract: cross-multiplied form) | p.3, Lemma 2.2 / (2.2) | **CONFIRMED** | Lemma 2.2 is explicitly independent of RH and Lindelöf, with `0 <= epsilon <= epsilon0 < 1/4`, a constant depending only on `epsilon0`, and all real `tau`. The source writes a quotient; the contract's cross-multiplied form is the zero-safe formal obligation and does not attribute division at denominator zeros to the source. |
| SC-NB-05 repeated-gamma-factor typesetting error in the v2 proof of Lemma 2.2 | p.3, proof of Lemma 2.2, second displayed line | **CONFIRMED** | The rendered PDF repeats the same `Gamma(1/4 + epsilon/2 + i*tau/2)` factor in numerator and denominator. The functional-equation derivation requires opposite signs of `epsilon` in the two gamma arguments, so the contract correctly records and rejects the printed repetition. |
| SC-NB-06 (1.1) raw Mobius family F_n = sum_{a=1}^n mu(a) rho_a and its divergence in H | p.2, equation (1.1) and following sentence | **CONFIRMED** | PDF p.2: '(1.1) F_n := sum_{a=1}^n mu(a) rho_a, which tends to -chi both a.e. and in L1 norm when restricted to (0,1) (see [1]), but which has been shown ([2],[3]) to diverge in H'. The contract's rejection of the raw family cites exactly this source statement. |
| SC-NB-06 (1.2) universal lower bound C/sqrt(log N(F)) with N(F) = max_k a_k as the scale | p.2, equation (1.2) and preceding sentence | **CONFIRMED** | The source defines `N = max_k a_k` for a finite Beurling combination and states `\|F-chi\|_H >= C/sqrt(log N)` with absolute `C`. Thus `N` is the real-valued maximum index/scale, not the number of summands, exactly as the contract records. |

## Coverage

The contract-side checklist (independent fourth agent) enumerates every
`SOURCE`/`DERIVED` claim citing one of the three PDFs; all checklist items
are covered by the row tables above, including both recorded `BD02-v2`
errata, the `LAG07` numbering note, and the source-quoting rows of the
anti-circularity matrix.

## RH-006 exit assessment

The record is sufficient for the external reviewer to accept or amend
`SOURCE_CONTRACTS.md` in one pass: 57/59 rows confirmed, with the two
amendments proposed above (one load-bearing for the Weil lane, one cosmetic).
Acceptance of the amended package clears the `RH-006` source-contract gate;
`RH-007` remains separately subject to independent acceptance of its xi
contract and to the normal promotion/CI gates.

## External acceptance disposition (2026-08-06)

**ACCEPT WITH APPLIED AMENDMENTS.** Both discrepancies above are resolved in
`SOURCE_CONTRACTS.md`; the separate acceptance record is
`RH006_SOURCE_CONTRACT_ACCEPTANCE_2026_08_06.md`. The historical replay result
remains 57 confirmed rows plus 2 discrepancies. The completion result is
**59/59 rows dispositioned: 57 confirmed, 2 amended, 0 open**. This closes
`RH-006` only; it does not accept the xi contract or authorize built promotion.
