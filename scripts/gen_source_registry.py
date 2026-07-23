#!/usr/bin/env python3
"""Source registry — the second provenance brick: catalog the external works the substrate cites.

`gen_result_registry.py` ties every theorem name cited in `VERIFIED.md` to an actual Lean
declaration. This script does the complementary job for the *literature*: it catalogs each
external result the docs invoke (Shoup, Nechaev, Semaev, Gaudry, Diem, Faugère–Gaudry–Huot–Renault,
Petit, Pollard, Pohlig–Hellman, Schoof, Frey–Rück, Smart, Satoh–Araki, MOV) with a stable id,
title, authors, year, venue, and a permanent link where one is confidently known — and records
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
        "id": "petit_ecdlp_largechar",
        "title": "Faster Algorithms for the ECDLP in the Large Characteristic Case (title as "
                 "cited in the repo)",
        "authors": ["Christophe Petit", "et al."],
        "year": None,
        "venue": None,
        "url": None,
        "doi": None,
        "aliases": ["Petit"],
        "role": "Composed low-degree rational maps for prime-field relation generation — the "
                "construction the P0 'petit' variant is explicitly NOT a faithful implementation of.",
        "note": "Bibliographic details (exact year/venue/DOI) not independently verified; title "
                "recorded as it appears in the repo prose. Do not cite externally without checking.",
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
        entries.append(src | {"where_used": where[src["id"]]})
    return {
        "schemaVersion": 1,
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
                       "role", "note", "where_used"):
            if field not in entry:
                problems.append(f"{entry.get('id', '?')}: missing field '{field}'")
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
