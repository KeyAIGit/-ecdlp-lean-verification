# RH source-PDF checksum replay

Date: 2026-08-05

Scope: mechanical re-verification of the three audited-PDF SHA-256 pins in
`domains/riemann-hypothesis/SOURCE_CONTRACTS.md` (§Local pinned source
table). This record closes exactly one input condition of the pending
`SOURCE_CONTRACTS.md` acceptance review — that the pinned artifacts are
byte-reproducible from their canonical URLs — and nothing more. It is
**not** the adversarial source-to-formalization review itself (theorem
extracts, signs, cutoffs, measures, errata), which remains open and
independent.

## Method

Each PDF was fetched fresh from the exact URL in the contract table and
hashed:

```bash
curl -sSL -o lag07.pdf   "https://www.numdam.org/item/10.5802/aif.2311.pdf"
curl -sSL -o bomclay.pdf "https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf"
curl -sSL -o bd02v2.pdf  "https://arxiv.org/pdf/math/0202141v2"
sha256sum *.pdf
```

Page counts were taken from the PDF page-tree objects (`/Type /Page`),
since `file(1)` reads only the first `/Count` it encounters and undercounts
two of the three files.

## Result: 3/3 exact matches

| local ID | fetched 2026-08-05 from | observed SHA-256 | pinned SHA-256 | match | pages | size (bytes) |
|---|---|---|---|---|---|---|
| `LAG07` | numdam.org/item/10.5802/aif.2311.pdf | `d1c3175591daff6a7f7503c8452eee0ce2536280cb9ce468a6c0a159be4d9f9b` | same | **yes** | 53 | 668121 |
| `BOM-CLAY` | claymath.org/wp-content/uploads/2022/05/riemann.pdf | `1454b2909f99271726ffb68b056aef45b7d3e6893a66282cad596339d69bafa9` | same | **yes** | 11 | 159267 |
| `BD02-v2` | arxiv.org/pdf/math/0202141v2 | `3ce4aff466443c71094affc1f8b6f5f0dd36cb4377dc5d2ceddbd2537c1d1819` | same | **yes** | 7 | 117974 |

Notes:

- The `BOM-CLAY` page count (11) matches the contract's "11-page PDF"
  description exactly.
- All three artifacts are therefore byte-identical to what the 2026-08-04
  audit hashed; any future locator (`§`, equation number, printed page)
  citing these pins refers to reproducible bytes.

## What this does and does not close

- Closes: the "PDF checksums re-verified" input of the
  `SOURCE_CONTRACTS.md` acceptance review (flagged in
  `notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md` §Scope boundary).
- Does not close: extraction and convention review of the contract's
  theorem statements against these PDFs (signs, cutoffs, multiplicity,
  measures, the recorded v2 errata). `SOURCE_CONTRACTS.md` remains
  "proposed under independent review".
