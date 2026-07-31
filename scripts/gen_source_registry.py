#!/usr/bin/env python3
"""Source registry — the second provenance brick: catalog the external works the substrate cites.

`gen_result_registry.py` ties every theorem name cited in `VERIFIED.md` to an actual Lean
declaration. This script does the complementary job for the *literature*: it catalogs each
external result the docs invoke (Shoup, Nechaev, Semaev, Gaudry, Diem, GLV, invariant theory,
automorphism-assisted index calculus, Petit-style prime-field methods, Pollard, Pohlig–Hellman,
Schoof, Frey–Rück, Smart, Satoh–Araki, MOV) with a stable id, title, authors, year, venue, and a
permanent link where one is confidently known — and records
**where each work is cited** in the repository, computed by scanning the hand-authored docs.

Why it is a gate, not just a file: provenance rots silently. If a new doc starts citing "Semaev"
and the registry is not updated, the `where_used` map is quietly wrong. `--check` recomputes the
citation map from the current docs and fails if the committed `data/source_registry.json` is stale
or if any registered `where_used` path no longer contains the citation — a mechanical guard that
the bibliography stays honest against the actual prose.

Honesty note: fields we are not independently sure of (e.g. an exact venue) are recorded as null
with a `note`, never guessed. The registry documents provenance; it does not invent citations.

Usage:
  python3 scripts/gen_source_registry.py            # write data/source_registry.json
  python3 scripts/gen_source_registry.py --check    # fail if the committed JSON is stale/inaccurate
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "source_registry.json"

# Directories whose *.md are generated or vendored — excluded from the citation scan so the
# provenance map is computed only from hand-authored source-of-truth prose. (data/ holds generated
# views like knowledge_graph.md; platform/ is the Node app; node_modules/.lake are deps/build.)
EXCLUDE_DIR_PARTS = {".git", ".lake", "node_modules", "data", "platform", "archive"}
EXCLUDE_FILES = {"repo/ECDLP_DECISION_SUBSTRATE.md"}

# The canonical bibliography. `aliases` are the surname/acronym tokens the works are cited by in the
# prose; the scan matches them on word boundaries to compute `where_used`. Keep aliases specific
# enough not to collide (e.g. "Smart" is only ever the author here). `url`/`doi`/`venue`/`year` are
# filled only where we are confident; otherwise null + a `note`, never a guess.
SOURCES: list[dict] = [
    {
        "id": "sec2_v2",
        "title": "SEC 2: Recommended Elliptic Curve Domain Parameters, Version 2.0",
        "authors": ["Certicom Research"],
        "year": 2010,
        "venue": "Standards for Efficient Cryptography (SEC 2), Version 2.0",
        "url": "https://www.secg.org/sec2-v2.pdf",
        "doi": None,
        "aliases": ["SEC 2", "SECG"],
        "role": "Primary standards source for the secp256k1 field, curve, generator, "
                "prime subgroup order, and cofactor parameters.",
        "note": "Dated January 27, 2010; the official SECG site lists Version 2.0 as "
                "the finalized SEC 2 specification.",
    },
    {
        "id": "shoup1997",
        "title": "Lower Bounds for Discrete Logarithms and Related Problems",
        "authors": ["Victor Shoup"],
        "year": 1997,
        "venue": "EUROCRYPT 1997, LNCS 1233",
        "url": "https://www.shoup.net/papers/dlbounds1.pdf",
        "doi": "10.1007/3-540-69053-0_18",
        "aliases": ["Shoup"],
        "role": "Generic-group lower bound Ω(√n) for the discrete log — the collision-counting "
                "core formalized in GenericGroupBound.lean.",
        "note": None,
    },
    {
        "id": "corrigan_gibbs_henzinger_wu2026",
        "title": "The Structured Generic-Group Model",
        "authors": [
            "Henry Corrigan-Gibbs",
            "Alexandra Henzinger",
            "David J. Wu",
        ],
        "year": 2026,
        "venue": "EUROCRYPT 2026",
        "url": "https://eprint.iacr.org/2026/384",
        "doi": None,
        "aliases": [
            "Corrigan-Gibbs",
            "Structured Generic-Group Model",
            "SGGM",
        ],
        "role": "Primary source for the partial-operation structured generic-group "
                "model, its constrained-label lower bound, and the exact model "
                "assumptions audited by HYP-SGGM-MODEL-MAP-001.",
        "full_text_status": "full_text_inspected",
        "note": "The full 36-page author manuscript was inspected through the "
                "author-hosted PDF. The repository operation map is a scoped "
                "application audit, not a claim that the published lower bound "
                "already covers the M16 relation interface.",
    },
    {
        "id": "takhanov2024",
        "title": "Intractability of Learning the Discrete Logarithm with "
                 "Gradient-Based Methods",
        "authors": [
            "Rustem Takhanov",
            "Maxat Tezekbayev",
            "Artur Pak",
            "Arman Bolatov",
            "Zhibek Kadyrsizova",
            "Zhenisbek Assylbekov",
        ],
        "year": 2024,
        "venue": "Proceedings of the 15th Asian Conference on Machine Learning, "
                 "PMLR 222, pp. 1321-1336",
        "url": "https://proceedings.mlr.press/v222/takhanov24a.html",
        "doi": None,
        "aliases": ["Takhanov"],
        "role": "Primary theoretical and empirical prior for the limitations of "
                "gradient-based learning of discrete-log parity in prime-order "
                "cyclic groups. It motivates treating direct scalar-bit regression "
                "as a diagnostic baseline rather than the main discovery engine.",
        "full_text_status": "full_text_inspected",
        "note": "The result studies gradient concentration for a concept class "
                "indexed by the logarithm base. It is not represented here as an "
                "unconditional impossibility theorem for every fixed-base, "
                "representation-aware secp256k1 learner.",
    },
    {
        "id": "nechaev1994",
        "title": "Complexity of a determinate algorithm for the discrete logarithm",
        "authors": ["V. I. Nechaev"],
        "year": 1994,
        "venue": "Mathematical Notes 55(2)",
        "url": None,
        "doi": "10.1007/BF02113297",
        "aliases": ["Nechaev"],
        "role": "Independent generic-group discrete-log lower bound (with Shoup), cited as the "
                "Shoup/Nechaev bound.",
        "note": None,
    },
    {
        "id": "semaev2004",
        "title": "Summation polynomials and the discrete logarithm problem on elliptic curves",
        "authors": ["Igor Semaev"],
        "year": 2004,
        "venue": "IACR ePrint 2004/031",
        "url": "https://eprint.iacr.org/2004/031",
        "doi": None,
        "aliases": ["Semaev"],
        "role": "Introduces the summation polynomials Sₘ formalized (S₃/S₄) in SemaevThree.lean / "
                "SemaevFour.lean and studied in the P0 experiment.",
        "note": None,
    },
    {
        "id": "gaudry2009",
        "title": "Index calculus for abelian varieties of small dimension and the elliptic curve "
                 "discrete logarithm problem",
        "authors": ["Pierrick Gaudry"],
        "year": 2009,
        "venue": "Journal of Symbolic Computation 44(12)",
        "url": None,
        "doi": "10.1016/j.jsc.2008.08.005",
        "aliases": ["Gaudry"],
        "role": "Index calculus for ECDLP over extension fields via Weil restriction — the "
                "subexponential regime the prime-field barrier (BARRIERS.md B3) contrasts against.",
        "note": None,
    },
    {
        "id": "diem2011",
        "title": "On the discrete logarithm problem in elliptic curves",
        "authors": ["Claus Diem"],
        "year": 2011,
        "venue": "Compositio Mathematica 147(1)",
        "url": None,
        "doi": "10.1112/S0010437X10005075",
        "aliases": ["Diem"],
        "role": "Asymptotic index-calculus results for ECDLP over extension fields (Gaudry–Diem–"
                "Semaev), cited to bound the scope of the Semaev formalization.",
        "note": None,
    },
    {
        "id": "glv2001",
        "title": "Faster Point Multiplication on Elliptic Curves with Efficient Endomorphisms",
        "authors": ["Robert P. Gallant", "Robert J. Lambert", "Scott A. Vanstone"],
        "year": 2001,
        "venue": "CRYPTO 2001, LNCS 2139",
        "url": "https://www.iacr.org/archive/crypto2001/21390189.pdf",
        "doi": "10.1007/3-540-44647-8_11",
        "aliases": ["Gallant", "GLV"],
        "role": "Primary source for the GLV scalar decomposition and the efficient "
                "endomorphism used by secp256k1.",
        "note": None,
    },
    {
        "id": "fghr2014",
        "title": "Using symmetries in the index calculus for elliptic curves discrete logarithm",
        "authors": ["Jean-Charles Faugère", "Pierrick Gaudry", "Louise Huot",
                    "Guénaël Renault"],
        "year": 2014,
        "venue": "Journal of Cryptology 27(4); IACR ePrint 2012/199",
        "url": "https://eprint.iacr.org/2012/199",
        "doi": "10.1007/s00145-013-9158-5",
        "aliases": ["Faugère", "FGHR", "Huot", "Renault"],
        "role": "Symmetry-adapted / quasi-homogeneous index calculus — the extension-field "
                "precedent for GLV-symmetrized relation systems in HYP_GLV_SEMAEV_001.",
        "note": None,
    },
    {
        "id": "fhjrv2014",
        "title": "Symmetrized Summation Polynomials: Using Small Order Torsion Points to "
                 "Speed Up Elliptic Curve Index Calculus",
        "authors": ["Jean-Charles Faugère", "Louise Huot", "Antoine Joux",
                    "Guénaël Renault", "Vanessa Vitse"],
        "year": 2014,
        "venue": "EUROCRYPT 2014, LNCS 8441, pp. 40–57",
        "url": "https://www.iacr.org/archive/eurocrypt2014/84410158/84410158.pdf",
        "doi": "10.1007/978-3-642-55220-5_3",
        "aliases": ["Symmetrized Summation Polynomials", "Vitse"],
        "role": "Primary source for torsion-translation symmetries whose coordinatewise "
                "relation-preserving subgroup grows with the number of free relation variables.",
        "full_text_status": "full_text_inspected",
        "note": "The official IACR archival PDF was inspected. Its torsion-translation "
                "mechanism is distinct from the diagonal scalar GLV action.",
    },
    {
        "id": "gebregiyorgis2016_thesis",
        "title": "Algorithms for the Elliptic Curve Discrete Logarithm and the Approximate "
                 "Common Divisor Problem",
        "authors": ["Shishay Welay Gebregiyorgis"],
        "year": 2016,
        "venue": "PhD thesis, University of Auckland",
        "url": "https://www.math.auckland.ac.nz/~sgal018/Shishay.pdf",
        "doi": None,
        "aliases": ["Gebregiyorgis"],
        "role": "Closest prior treatment of a curve automorphism acting simultaneously on a "
                "Semaev relation system, including target transport, invariant coordinates, "
                "and negative polynomial-solving observations in characteristic 3.",
        "note": "The primary thesis PDF is hosted on an official University of Auckland faculty "
                "page. No DOI or canonical institutional-repository identifier was confirmed.",
    },
    {
        "id": "sturmfels2008",
        "title": "Algorithms in Invariant Theory",
        "authors": ["Bernd Sturmfels"],
        "year": 2008,
        "venue": "2nd ed., Texts & Monographs in Symbolic Computation, Springer Vienna",
        "url": "https://link.springer.com/book/10.1007/978-3-211-77417-5",
        "doi": "10.1007/978-3-211-77417-5",
        "aliases": ["Sturmfels"],
        "role": "Textbook source for invariant rings of diagonal cyclic scalar actions, "
                "Veronese subalgebras, and the generator count used in the GLV-Semaev analysis.",
        "note": "The iteration note cites the second edition. The underlying proposition first "
                "appeared in the 1993 edition; the metadata here is for the 2008 second edition.",
    },
    {
        "id": "duursma_gaudry_morain1999",
        "title": "Speeding up the Discrete Log Computation on Curves with Automorphisms",
        "authors": ["Iwan Duursma", "Pierrick Gaudry", "François Morain"],
        "year": 1999,
        "venue": "ASIACRYPT 1999, LNCS 1716, pp. 103–121",
        "url": "https://link.springer.com/chapter/10.1007/978-3-540-48000-6_10",
        "doi": "10.1007/978-3-540-48000-6_10",
        "aliases": ["Duursma"],
        "role": "Primary prior art for exploiting curve automorphisms in Pollard rho, including "
                "the order-6 automorphism group of j=0 curves and its constant-factor speedup.",
        "note": None,
    },
    {
        "id": "tsakou_ionica2021",
        "title": "Index calculus attacks on hyperelliptic Jacobians with efficient endomorphisms",
        "authors": ["Sulamithe Tsakou", "Sorina Ionica"],
        "year": 2021,
        "venue": "Mathematical Cryptology 1(2), pp. 102–114; IACR ePrint 2021/721",
        "url": "https://eprint.iacr.org/2021/721",
        "doi": None,
        "aliases": ["Tsakou", "Ionica"],
        "role": "Prior art for endomorphism-invariant factor bases and the literal j=0 map "
                "phi(x,y)=(beta*x,y) in extension-field index calculus.",
        "note": "The open IACR preprint is titled with 'Effective Endomorphisms'; the published "
                "2021 journal version uses 'efficient endomorphisms'. No DOI was confirmed.",
    },
    {
        "id": "petit_kosters_messeng2016",
        "title": "Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over "
                 "Prime Fields",
        "authors": ["Christophe Petit", "Michiel Kosters", "Ange Messeng"],
        "year": 2016,
        "venue": "PKC 2016, Part II, LNCS 9615, pp. 3–18",
        "url": "https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf",
        "doi": "10.1007/978-3-662-49387-8_1",
        "aliases": ["Petit–Kosters–Messeng", "Kosters", "Messeng"],
        "role": "Primary specification for composed low-degree rational-map factor bases and "
                "prime-field Semaev relation systems; required provenance for any faithful "
                "R-PETIT-COMPOSED-MAPS implementation.",
        "full_text_status": "full_text_inspected",
        "note": "An open official IACR archival PDF exists. The earlier repository statement that "
                "this source was unavailable or only paywalled was incorrect. A full-text "
                "construction and term review found no GLV, automorphism, endomorphism, "
                "invariant-coordinate, or fixed-target symmetry claim; its relevance is the "
                "faithful composed-map factor-base construction, not overlap with the bounded "
                "GLV-SEMAEV-ITER-001 stabilizer result.",
    },
    {
        "id": "amadori_pintore_sala2018",
        "title": "On the Discrete Logarithm Problem for Prime-Field Elliptic Curves",
        "authors": ["Alessandro Amadori", "Federico Pintore", "Massimiliano Sala"],
        "year": 2018,
        "venue": "Finite Fields and Their Applications 51, pp. 168–182",
        "url": "https://eprint.iacr.org/2017/609",
        "doi": "10.1016/j.ffa.2018.01.009",
        "aliases": ["Amadori"],
        "role": "Primary source for a one-Gröbner-basis prime-field index-calculus variant "
                "and an independent description of the faithful Petit factor base L(x)=0.",
        "full_text_status": "full_text_inspected",
        "note": "The open IACR manuscript and publication metadata were inspected. It is "
                "prior art for proposal design, not evidence that P4 implemented the method.",
    },
    {
        "id": "yokota_kudo_yasuda2017_wcc",
        "title": "Practical Limit of Index Calculus Algorithms for ECDLP over Prime Fields",
        "authors": ["Yuki Yokota", "Momonari Kudo", "Masaya Yasuda"],
        "year": 2017,
        "venue": "Proceedings of the Tenth International Workshop on Coding and "
                 "Cryptography (WCC 2017), 12 pp.",
        "url": "https://drive.google.com/file/d/1I8t-2nEMqzTr8ueppHIO3xWHe1khWiAb/"
               "view?usp=sharing",
        "doi": None,
        "aliases": ["Yokota-Kudo-Yasuda", "Practical Limit"],
        "role": "Primary extended-abstract evidence for the bounded m=2 experiments on "
                "p-minus-one smooth-factor accelerations and the separate p-plus-one "
                "trace construction.",
        "full_text_status": "full_text_inspected",
        "note": "The author-linked 12-page PDF was inspected and hashed as "
                "a60b09327429f0fd99561cd600455ee38da687078b55250ad4ebcb1170b7ded4. "
                "It is a separate WCC 2017 precursor, not the CANS 2018 paper, and "
                "does not change the latter's full_text_unread status.",
    },
    {
        "id": "kudo_yokota_takahashi_yasuda2018",
        "title": "Acceleration of Index Calculus for Solving ECDLP over Prime Fields and Its "
                 "Limitation",
        "authors": ["Momonari Kudo", "Yuki Yokota", "Yasushi Takahashi", "Masaya Yasuda"],
        "year": 2018,
        "venue": "CANS 2018, LNCS 11124, pp. 377–393",
        "url": "https://link.springer.com/chapter/10.1007/978-3-030-00434-7_19",
        "doi": "10.1007/978-3-030-00434-7_19",
        "aliases": ["Kudo"],
        "role": "Prior art for hybrid Gröbner acceleration and summation-polynomial symmetries "
                "in prime-field ECDLP index calculus, together with stated limitations.",
        "full_text_status": "full_text_unread",
        "note": "Springer metadata and abstract were verified. No open primary manuscript was "
                "confirmed, and the full paper was not inspected in this iteration.",
    },
    {
        "id": "yokoyama_yasuda_takahashi_kogure2020",
        "title": "Complexity Bounds on Semaev's Naive Index Calculus Method for ECDLP",
        "authors": [
            "Kazuhiro Yokoyama",
            "Masaya Yasuda",
            "Yasushi Takahashi",
            "Jun Kogure",
        ],
        "year": 2020,
        "venue": "Journal of Mathematical Cryptology 14(1), pp. 460–485",
        "url": "https://doi.org/10.1515/jmc-2019-0029",
        "doi": "10.1515/jmc-2019-0029",
        "aliases": ["Yokoyama–Yasuda–Takahashi–Kogure", "Yokoyama"],
        "role": "Conditional lower-bound evidence for Gröbner-basis computation in "
                "Semaev's naive random-factor-base index calculus method.",
        "full_text_status": "full_text_inspected",
        "note": "The final 26-page publisher PDF was inspected from a preserved publisher "
                "snapshot. Proposition 9 depends on Assumption 7 and the explicitly "
                "non-rigorous transfer in Remark 8, and is scoped to the naive random-V "
                "ideal and algorithms using S-polynomials. It is not a no-go theorem for "
                "structured Petit, Amadori, or Kudo systems.",
    },
    {
        "id": "petit_ecdlp_largechar",
        "title": "Faster Algorithms for the ECDLP in the Large Characteristic Case (title as "
                 "cited in the repo)",
        "authors": ["Christophe Petit", "et al."],
        "year": None,
        "venue": None,
        "url": None,
        "doi": None,
        "aliases": ["Faster Algorithms for the ECDLP in the Large Characteristic Case"],
        "role": "Composed low-degree rational maps for prime-field relation generation — the "
                "construction the P0 'petit' variant is explicitly NOT a faithful implementation of.",
        "note": "Unverified legacy identity, retained separately from Petit–Kosters–Messeng 2016 "
                "because the title does not match and equivalence was not established. The broad "
                "alias 'Petit' was removed to prevent provenance conflation. Do not cite this "
                "record externally without identifying the underlying work.",
    },
    {
        "id": "pollard1978",
        "title": "Monte Carlo methods for index computation (mod p)",
        "authors": ["John M. Pollard"],
        "year": 1978,
        "venue": "Mathematics of Computation 32(143)",
        "url": None,
        "doi": "10.1090/S0025-5718-1978-0491431-9",
        "aliases": ["Pollard"],
        "role": "Pollard rho — the O(√n) generic upper bound matching Shoup's lower bound "
                "(PollardRho.lean), giving generic DLP Θ(√n).",
        "note": None,
    },
    {
        "id": "pohlig_hellman1978",
        "title": "An Improved Algorithm for Computing Logarithms over GF(p) and Its Cryptographic "
                 "Significance",
        "authors": ["Stephen C. Pohlig", "Martin E. Hellman"],
        "year": 1978,
        "venue": "IEEE Transactions on Information Theory 24(1)",
        "url": None,
        "doi": "10.1109/TIT.1978.1055817",
        "aliases": ["Pohlig", "Pohlig–Hellman", "Pohlig-Hellman"],
        "role": "Reduces DLP to prime-order subgroups — why cofactor-1 prime order n matters "
                "(PohligHellman.lean).",
        "note": None,
    },
    {
        "id": "schoof1985",
        "title": "Elliptic Curves over Finite Fields and the Computation of Square Roots mod p",
        "authors": ["René Schoof"],
        "year": 1985,
        "venue": "Mathematics of Computation 44(170)",
        "url": None,
        "doi": "10.1090/S0025-5718-1985-0777280-6",
        "aliases": ["Schoof"],
        "role": "Polynomial-time point counting — the algorithm Mathlib lacks, so #E(𝔽ₚ)=n is "
                "pinned by native_decide rather than proved (the point-counting barrier).",
        "note": None,
    },
    {
        "id": "frey_ruck1994",
        "title": "A remark concerning m-divisibility and the discrete logarithm in the divisor "
                 "class group of curves",
        "authors": ["Gerhard Frey", "Hans-Georg Rück"],
        "year": 1994,
        "venue": "Mathematics of Computation 62(206)",
        "url": None,
        "doi": "10.1090/S0025-5718-1994-1218343-6",
        "aliases": ["Frey", "Rück", "Frey–Rück", "Frey-Rück"],
        "role": "Frey–Rück (FR) transfer via pairings — with MOV, the attack the embedding-degree "
                "bound (EmbeddingDegree.lean) proves secp256k1 resists.",
        "note": None,
    },
    {
        "id": "mov1993",
        "title": "Reducing Elliptic Curve Logarithms to Logarithms in a Finite Field",
        "authors": ["Alfred J. Menezes", "Tatsuaki Okamoto", "Scott A. Vanstone"],
        "year": 1993,
        "venue": "IEEE Transactions on Information Theory 39(5)",
        "url": None,
        "doi": "10.1109/18.259647",
        "aliases": ["MOV", "Menezes"],
        "role": "MOV transfer to 𝔽_{p^k}^× via the Weil pairing — resisted by secp256k1's large "
                "embedding degree (secp256k1_embedding_degree_gt_100).",
        "note": None,
    },
    {
        "id": "smart1999",
        "title": "The Discrete Logarithm Problem on Elliptic Curves of Trace One",
        "authors": ["Nigel P. Smart"],
        "year": 1999,
        "venue": "Journal of Cryptology 12(3)",
        "url": None,
        "doi": "10.1007/s001459900052",
        "aliases": ["Smart", "SSSA"],
        "role": "Anomalous-curve (trace-one) attack — resisted because secp256k1 has trace t≠1 "
                "(secp256k1_trace_ordinary_nonanomalous / anomalous_iff_trace_one).",
        "note": "Discovered independently by Smart, Satoh–Araki, and Semaev; cited here as "
                "Smart/SSSA.",
    },
    {
        "id": "shor1994",
        "title": "Algorithms for Quantum Computation: Discrete Logarithms and Factoring",
        "authors": ["Peter W. Shor"],
        "year": 1994,
        "venue": "35th Annual Symposium on Foundations of Computer Science",
        "url": "https://doi.org/10.1109/SFCS.1994.365700",
        "doi": "10.1109/SFCS.1994.365700",
        "aliases": ["Shor"],
        "role": "Foundational polynomial-time quantum route for discrete logarithms; "
                "kept separate from the classical threat model.",
        "note": None,
    },
    {
        "id": "luo2026",
        "title": "Quantum Algorithm for Elliptic Curve Discrete Logarithms with "
                 "Space-Efficient Point Addition",
        "authors": ["Han Luo", "Ziyi Yang", "Jingquan Luo", "Ziruo Wang",
                    "Yuexin Su", "Xiaoming Sun", "Lvzhou Li", "Tongyang Li"],
        "year": 2026,
        "venue": "arXiv:2607.13816",
        "url": "https://arxiv.org/abs/2607.13816",
        "doi": None,
        "aliases": ["Luo"],
        "role": "Current tracked logical-resource estimate for a quantum ECDLP "
                "implementation over a 256-bit prime-field curve.",
        "note": "Reports 835 logical qubits and 2^30.63 Toffoli gates. This is an "
                "algorithmic logical-resource estimate, not evidence of available "
                "fault-tolerant hardware.",
    },
]


def scan_docs() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*.md")):
        relative = p.relative_to(ROOT)
        if any(part in EXCLUDE_DIR_PARTS for part in relative.parts):
            continue
        if relative.as_posix() in EXCLUDE_FILES:
            continue
        out.append(p)
    return out


def alias_pattern(alias: str) -> re.Pattern:
    # Word-boundary match that respects unicode letters (é, ü) and hyphenated compounds. \b does not
    # behave well around non-ASCII, so guard with explicit non-letter lookarounds.
    esc = re.escape(alias)
    return re.compile(rf"(?<![^\W\d_]){esc}(?![^\W\d_])")


def compute_where_used(sources: list[dict]) -> dict[str, list[str]]:
    docs = scan_docs()
    texts = {p: p.read_text(encoding="utf-8") for p in docs}
    where: dict[str, list[str]] = {}
    for src in sources:
        pats = [alias_pattern(a) for a in src["aliases"]]
        hits = []
        for p, text in texts.items():
            if any(pat.search(text) for pat in pats):
                # Registry paths are repository identifiers, not host paths.
                hits.append(p.relative_to(ROOT).as_posix())
        where[src["id"]] = sorted(hits)
    return where


def build_registry() -> dict:
    where = compute_where_used(SOURCES)
    entries = []
    for src in sorted(SOURCES, key=lambda s: s["id"]):
        entries.append(
            src
            | {
                "full_text_status": src.get("full_text_status", "not_asserted"),
                "where_used": where[src["id"]],
            }
        )
    return {
        "schemaVersion": 2,
        "purpose": "External works cited across the substrate, with provenance (where_used) "
                   "computed from the hand-authored docs. Companion to result_registry.json "
                   "(theorem-name provenance).",
        "scan_scope": "**/*.md excluding " + ", ".join(sorted(EXCLUDE_DIR_PARTS)),
        "source_count": len(SOURCES),
        "sources": entries,
    }


def main() -> int:
    check = "--check" in sys.argv
    registry = build_registry()

    # Structural self-checks (run in both modes): unique ids, required fields, and every registered
    # where_used path actually still contains an alias (guards against a doc dropping a citation).
    ids = [s["id"] for s in SOURCES]
    problems: list[str] = []
    if len(ids) != len(set(ids)):
        problems.append("duplicate source ids in the bibliography")
    for entry in registry["sources"]:
        for field in ("id", "title", "authors", "year", "venue", "url", "doi", "aliases",
                       "role", "note", "full_text_status", "where_used"):
            if field not in entry:
                problems.append(f"{entry.get('id', '?')}: missing field '{field}'")
        if entry.get("full_text_status") not in {
            "full_text_inspected",
            "full_text_unread",
            "not_asserted",
        }:
            problems.append(
                f"{entry.get('id', '?')}: invalid full_text_status "
                f"{entry.get('full_text_status')!r}"
            )
        if not entry["where_used"]:
            problems.append(f"{entry['id']}: cited by no scanned doc — orphan bibliography entry")

    if check:
        if problems:
            print("source-registry check FAILED — bibliography integrity problems:")
            for p in problems:
                print(f"  - {p}")
            return 1
        if not OUT.exists():
            print(f"source-registry check FAILED — {OUT.relative_to(ROOT)} is missing; run "
                  "`python3 scripts/gen_source_registry.py`.")
            return 1
        on_disk = json.loads(OUT.read_text(encoding="utf-8"))
        if on_disk != registry:
            print("source-registry check FAILED — committed data/source_registry.json is stale "
                  "(docs changed which works they cite, or the bibliography changed). Regenerate "
                  "with `python3 scripts/gen_source_registry.py` and commit.")
            return 1
        n_cites = sum(len(s["where_used"]) for s in registry["sources"])
        print(f"source-registry check OK: {len(SOURCES)} works, provenance in sync "
              f"({n_cites} doc citations across {len(scan_docs())} scanned docs).")
        return 0

    if problems:
        print("WARNING — bibliography integrity problems (writing anyway):")
        for p in problems:
            print(f"  - {p}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n_cites = sum(len(s["where_used"]) for s in registry["sources"])
    print(f"wrote {OUT.relative_to(ROOT)} — {len(SOURCES)} works, {n_cites} doc citations "
          f"across {len(scan_docs())} scanned docs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
