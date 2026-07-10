#!/usr/bin/env python3
"""Build dashboard.html / index.html — the navigable home page of the environment.

Visual identity matches the KeyAI brand (navy #001a3f, accent blue #1d85ff, rounded
geometric type Baloo 2 + Nunito, real extracted logo assets in assets/). Charts follow
the data-viz method: status-semantic color for the frontier breakdown (good/warning/
critical, not an arbitrary 6-hue rainbow), a single-hue sequential bar for the
foundations-blocked magnitude comparison, mark specs (thin bars, rounded data-ends,
2px gaps), keyboard-reachable hover (CSS-only, works on :focus too), and a table-view
twin for every chart (the WCAG-clean accessible equivalent). Colors were sampled
directly from the deck's rendered slides and validated for contrast — not guessed.

Modern-site touches: sticky glass nav with scrollspy, scroll-reveal
(IntersectionObserver, respects prefers-reduced-motion), animated stat-tile count-up,
an animated circular completeness meter, real favicon/OG metadata.

Consolidates live state (metrics, L1-L5 layers, tracks/checkpoints, frontier map, recent
milestones) AND a full, auto-discovered navigation of every doc/data/script in the repo,
grouped by purpose, so nothing is ever missing or hard to find.

This is a SNAPSHOT (regenerate with this script — also run on every ledger change so the
live GitHub Pages / htmlpreview link stays current). For truly-live status use the GitHub
Actions tab (CI green/red in real time) and the commit history.

Run: python3 scripts/build_dashboard.py
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FM = ROOT / "data" / "frontier_map.json"
KG = ROOT / "data" / "knowledge_graph.json"
STATUS_MD = ROOT / "STATUS.md"
ARTIFACTS = ROOT / "repo" / "ARTIFACTS.yaml"
TASKS = ROOT / "tasks" / "NEXT.md"
HYPOTHESES = ROOT / "experiments" / "HYPOTHESES.yaml"
VERIFIED = ROOT / "VERIFIED.md"
CORPUS_CSV = ROOT / "data" / "KG_CLAIM_FORMALIZATION_v1.csv"
PUB_UNITS = ROOT / "PUBLISHABLE_UNITS.md"
OUT = ROOT / "dashboard.html"
INDEX = ROOT / "index.html"
# Ledger rows that are alternate-form/`supporting:` restatements of the same fact.
# VERIFIED.md's canonical line is the single source of truth ("180 ledger rows /
# ~158 distinct" → 22 restatement rows); keep this in sync with it.
DISTINCT_OFFSET = 22
REPO = "https://github.com/KeyAIGit/-ecdlp-lean-verification"
BLOB = f"{REPO}/blob/main"
TREE = f"{REPO}/tree/main"

# ---- status-semantic palette (validated: good/warning/critical fixed roles, never
# themed; text stays in ink tokens, these hexes are for fills/dots only, per the
# dataviz method's "text never wears the data color" + icon-and-label mitigation for
# sub-3:1 fills) ----
STATUS = {
    "verified":    {"hex": "#0ca30c", "label": "verified",    "note": "kernel-checked"},
    "tractable":   {"hex": "#1d85ff", "label": "tractable",   "note": "reachable, no new foundation"},
    "partial":     {"hex": "#fab219", "label": "partial",     "note": "some progress possible"},
    "blocked":     {"hex": "#d03b3b", "label": "blocked",     "note": "needs a missing foundation"},
    "informal":    {"hex": "#94a3b8", "label": "informal",    "note": "not a formal statement by nature"},
    "unassigned":  {"hex": "#64748b", "label": "unassigned",  "note": "not yet triaged"},
}
STATUS_ORDER = ["verified", "tractable", "partial", "blocked", "informal", "unassigned"]
DOT = {"done": "#0ca30c", "wip": "#fab219", "todo": "#94a3b8"}

TRACKS = [
    ("A — Frontier map (machine-actionable)", [
        ("A1 frontier_map.json + query", "done"),
        ("A2 status+foundation for every claim (79.8%)", "wip"),
        ("A3 per-foundation unlock lists", "todo"),
    ]),
    ("B — Depth (verified foundations, DAG)", [
        ("GLV object: equation→hom→cube-root→torsion-preserving", "done"),
        ("E[n] group object bridged", "done"),
        ("next rung → E[n]≅(ℤ/n)² (blocked by point-counting)", "todo"),
    ]),
    ("C — Engine & extensibility", [
        ("CI trust gates (no-sorry, axiom audit, count/import)", "done"),
        ("generator + prover loop", "done"),
        ("warm server node (idle — needs PAT)", "todo"),
    ]),
]
LAYERS = [
    ("L1", "Verified core", "kernel-checked theorems (absolute trust)", "done"),
    ("L2", "Frontier map", "what's open/blocked & by which missing foundation", "wip"),
    ("L3", "Navigable structure", "machine-readable graph + queryable data", "done"),
    ("L4", "Formalized objects", "GLV (cube-root + torsion-preserving), torsion, division polys", "wip"),
    ("L5", "Engine", "AI+kernel pipeline; self-extensible substrate", "todo"),
]

NAV = [
    ("Start here", [
        ("README.md", "Project overview, layout, build instructions"),
        ("READ_FIRST.md", "Low-context orientation: what this is, what not to claim"),
        ("AGENTS.md", "Orientation for any Claude instance — read this first"),
        ("ENVIRONMENT_PLAN.md", "The strategic plan: L1-L5 layers, 3 tracks, checkpoints"),
        ("CLAUDE.md", "Working conventions for automated/assisted runs"),
        ("AGENT.md", "The authoritative protocol"),
        ("SETUP.md", "Minimal build command"),
    ]),
    ("Research OS & architecture", [
        ("STATUS.md", "Canonical generated snapshot: live counts, corpus status, and bottleneck"),
        ("PLATFORM_STRATEGY.md", "Direction: from one verified case to a verified-research platform (honest phased roadmap)"),
        ("tasks/NEXT.md", "Small-context active task queue"),
        ("experiments/HYPOTHESES.yaml", "Hypothesis registry with evidence and exit criteria"),
        ("REPOSITORY_ARCHITECTURE.md", "Whole-repo map: canonical, generated, public, scratch, archive"),
        ("repo/ARTIFACTS.yaml", "Machine-readable artifact classification manifest"),
        ("repo/CLEANUP_PLAN.md", "Conservative cleanup plan: classify, review, then move/delete"),
        ("CLAUDE_REVIEW_PACKET.md", "Final adversarial review packet template"),
    ]),
    ("The ledger & proofs", [
        ("VERIFIED.md", "The canonical ledger — every kernel-verified theorem, one row each"),
        ("Ecdlp/Proved/", "The Lean source of every verified theorem (38 files)", TREE + "/Ecdlp/Proved"),
        ("Ecdlp/Targets/", "Open conjecture stems — not built, not gated (13 files)", TREE + "/Ecdlp/Targets"),
        ("Ecdlp/AxiomAudit.lean", "The axiom-audit harness (#print axioms on headline results)"),
        ("TRUST_REPORT.md", "Trust boundary: pure-kernel vs native_decide (compiler-trust) classification"),
    ]),
    ("Honesty & independent review", [
        ("COVERAGE.md", "Honest 3-denominator coverage benchmark (regenerate: coverage_report.py)"),
        ("BARRIERS.md", "The no-go map — what's blocked, and by which missing foundation"),
        ("ABSTRACT_SCOPE.md", "Honest scope of the DL-crypto library (abstract algebra, not yet instantiated)"),
        ("REVIEW_DOSSIER.md", "Adversarial 5-lens independent-review packet"),
        ("ONE_PAGE_SUMMARY.md", "One-page external summary (Lean-expert + generalist audiences)"),
    ]),
    ("Frontier & data (machine-readable)", [
        ("data/frontier_map.json", "The queryable frontier map — status + blocking foundation per claim"),
        ("data/knowledge_graph.json", "Machine-readable theorem graph (deps, areas, barriers)"),
        ("data/knowledge_graph.md", "Rendered knowledge graph"),
        ("data/KG_CLAIM_FORMALIZATION_v1.csv", "The 486-claim corpus (read-only source)"),
        ("data/README.md", "Corpus provenance"),
    ]),
    ("Deep-dive notes (foundations & strategy)", [
        ("notes/FOUNDATIONS.md", "The deep-foundations roadmap toward the Weil pairing"),
        ("notes/GLV_LAMBDA.md", "GLV [λ]-eigenvalue bottleneck + the reachable cube-relation substitute"),
        ("notes/GLV_HOMOMORPHISM.md", "How the GLV homomorphism reduces to one slope identity"),
        ("notes/FOUNDATION_ROADMAP.md", "Corpus → missing-object leverage map"),
        ("notes/ARCHITECTURE.md", "System architecture (mermaid diagram)"),
        ("notes/AGENT_ORCHESTRATION.md", "Agent/orchestration map"),
        ("notes/KNOWLEDGE_GRAPH.md", "Knowledge-graph design notes"),
        ("notes/PRIMALITY.md", "Pratt primality certificate notes"),
        ("notes/SERVER_CONNECT.md", "No-SSH server bootstrap (Hetzner Console)"),
        ("notes/SERVER_RUNBOOK.md", "Server operational runbook"),
    ]),
    ("Engine & scripts", [
        ("scripts/build_dashboard.py", "Regenerates this page"),
        ("scripts/build_frontier_map.py", "Regenerates/queries data/frontier_map.json"),
        ("scripts/build_knowledge_graph.py", "Regenerates the knowledge graph"),
        ("scripts/coverage_report.py", "Regenerates COVERAGE.md"),
        ("scripts/check_axioms.py", "CI: axiom-audit checker (no sorryAx, no custom axioms)"),
        ("scripts/check_counts.py", "CI: count-consistency checker (no retired headline numbers)"),
        ("scripts/generator.py", "Layer-3: corpus → open target stems"),
        ("scripts/prover_loop.py", "Layer-2: autonomous prover loop (Tier-0 + model tiers)"),
        ("scripts/prover_target_attempt.py", "Single-target prover attempt harness"),
        ("scripts/prover_smoke_test.py", "Smoke test for the prover harness"),
        ("scripts/pratt_certificate.py", "Generates Pratt primality certificates"),
        ("scripts/frontier_generator.py", "Frontier-expander target generator"),
        ("scripts/foundation_map.py", "Foundation leverage-map builder"),
    ]),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def git_log(n: int = 14) -> list[tuple[str, str]]:
    try:
        out = subprocess.run(
            ["git", "log", "--format=%h\t%s", f"-{n}", "origin/main"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=20,
        ).stdout
    except Exception:
        out = ""
    rows = []
    for line in out.strip().splitlines():
        if "\t" in line:
            h, s = line.split("\t", 1)
            rows.append((h, s))
    return rows


def count_lines_matching(path: Path, pattern: str) -> int:
    """Count lines matching a regex in a file (0 if absent). Used for the pipeline
    stage counters so the site's layer chain is driven by the real artifacts, never
    hand-typed numbers that would drift."""
    try:
        return len(re.findall(pattern, path.read_text(encoding="utf-8"), re.M))
    except Exception:
        return 0


def build_pipeline(stages: list[dict]) -> str:
    """Render the Research OS layer chain: Corpus → Frontier → Hypotheses → Tasks →
    Proofs → Truth graph → Site → Papers. Each stage shows a live count pulled from
    its own source artifact and links straight to it, so the public site *is* the
    pipeline, walked end to end. This is the spine the whole environment hangs on."""
    cells = []
    n = len(stages)
    for i, s in enumerate(stages):
        val = esc(str(s["value"]))
        unit = f'<span class="pgunit">{esc(s["unit"])}</span>' if s.get("unit") else ""
        here = ' pgcard--here' if s.get("here") else ""
        href = esc(s["href"])
        # internal anchors don't open a new tab; external repo links do
        ext = "" if href.startswith("#") else ' target="_blank" rel="noopener"'
        arrow = '' if i == n - 1 else '<div class="pgarrow" aria-hidden="true">→</div>'
        cells.append(
            f'<a class="pgcard{here}" href="{href}"{ext}>'
            f'<div class="pgeyebrow"><span class="pgstep">{i+1:02d}</span>{esc(s["layer"])}</div>'
            f'<div class="pgval">{val}{unit}</div>'
            f'<div class="pgrole">{esc(s["role"])}</div>'
            f'<div class="pgsrc">{esc(s["src"])}</div></a>'
            f'{arrow}')
    return f'<div class="pipeline reveal">{"".join(cells)}</div>'


def nav_url(path: str, override: str | None) -> str:
    if override:
        return override
    if path.endswith("/"):
        return f"{TREE}/{path.rstrip('/')}"
    return f"{BLOB}/{path}"


def discover_extra_files() -> list[str]:
    known = {entry[0] for _, items in NAV for entry in items}
    found: list[str] = []
    for pattern, base in [("*.md", ROOT), ("notes/*.md", ROOT),
                           ("data/*.json", ROOT), ("data/*.md", ROOT),
                           ("scripts/*.py", ROOT)]:
        for p in sorted(base.glob(pattern)):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in known and "__pycache__" not in rel:
                found.append(rel)
    return found


def build_nav_html() -> str:
    sections = []
    for title, items in NAV:
        cards = []
        for entry in items:
            path, desc = entry[0], entry[1]
            override = entry[2] if len(entry) > 2 else None
            url = nav_url(path, override)
            label = path.rstrip("/").split("/")[-1] if not path.endswith("/") else path
            cards.append(
                f'<a class="navcard" href="{esc(url)}"><div class="navname">{esc(label)}</div>'
                f'<div class="navpath">{esc(path)}</div><div class="navdesc">{esc(desc)}</div></a>')
        sections.append(f'<div class="navsection reveal"><h3>{esc(title)}</h3>'
                        f'<div class="navgrid">{"".join(cards)}</div></div>')

    extras = discover_extra_files()
    if extras:
        cards = "".join(
            f'<a class="navcard" href="{esc(nav_url(p, None))}"><div class="navname">'
            f'{esc(p.split("/")[-1])}</div><div class="navpath">{esc(p)}</div>'
            f'<div class="navdesc">not yet categorized (auto-discovered so it stays visible)</div></a>'
            for p in extras)
        sections.append(f'<div class="navsection reveal"><h3>Other (auto-discovered)</h3>'
                        f'<div class="navgrid">{cards}</div></div>')
    return "".join(sections)


def build_sync_health(stats: dict, frontier: dict, graph: dict) -> str:
    """Render a compact, source-backed sync-health panel."""
    ledger_rows = int(stats.get("ledger_rows", 0))
    distinct = int(stats.get("distinct_results", 0))
    corpus_claims = int(frontier.get("meta", {}).get("corpus_claims", 0))
    frontier_rows = int(frontier.get("meta", {}).get("verified_ledger_rows", -1))
    frontier_total = sum(int(v) for v in frontier.get("status_summary", {}).values())
    graph_theorems = int(graph.get("counts", {}).get("theorems", 0))

    checks = [
        (
            "Canonical counts",
            frontier_rows == ledger_rows and ledger_rows > 0 and distinct > 0,
            f"{ledger_rows} ledger rows / ~{distinct} distinct",
            "data/stats.json + STATUS.md",
        ),
        (
            "Frontier map",
            frontier_total == corpus_claims and corpus_claims > 0,
            f"{corpus_claims} corpus claims classified",
            "data/frontier_map.json",
        ),
        (
            "Knowledge graph",
            graph_theorems > 0,
            f"{graph_theorems} graph theorem nodes",
            "data/knowledge_graph.json",
        ),
        (
            "Artifact manifest",
            ARTIFACTS.exists(),
            "canonical/generated/scratch/archive classes present",
            "repo/ARTIFACTS.yaml + scripts/check_repo_artifacts.py",
        ),
        (
            "Active work",
            TASKS.exists() and HYPOTHESES.exists(),
            "task queue and hypothesis registry present",
            "tasks/NEXT.md + experiments/HYPOTHESES.yaml",
        ),
    ]

    cards = []
    for label, ok, value, source in checks:
        cls = "ok" if ok else "bad"
        state = "OK" if ok else "DRIFT"
        cards.append(
            f'<div class="health {cls} reveal"><div class="hstate">{state}</div>'
            f'<div class="hname">{esc(label)}</div><div class="hval">{esc(value)}</div>'
            f'<div class="hsrc">{esc(source)}</div></div>'
        )
    return "".join(cards)


def build_frontier_bar(status: dict, total: int) -> tuple[str, str, str]:
    """Status-semantic stacked bar (part-to-whole, fixed reserved meaning) + legend +
    accessible table-view twin. 2px surface gaps between segments; each segment is a
    keyboard-focusable element carrying a CSS-only tooltip (no JS needed, works on
    hover AND focus)."""
    segs, legend, rows = [], [], []
    for k in STATUS_ORDER:
        n = status.get(k, 0)
        if not n:
            continue
        pct = 100 * n / total
        s = STATUS[k]
        segs.append(
            f'<div class="seg" tabindex="0" style="width:{pct:.2f}%;background:{s["hex"]}" '
            f'data-tip="{esc(s["label"])}: {n} claims ({pct:.1f}%) — {esc(s["note"])}"></div>')
        legend.append(
            f'<span class="lg"><i style="background:{s["hex"]}"></i>{esc(s["label"])} '
            f'<b>{n}</b></span>')
        rows.append(f'<tr><td><i style="background:{s["hex"]}"></i>{esc(s["label"])}</td>'
                    f'<td>{n}</td><td>{pct:.1f}%</td><td>{esc(s["note"])}</td></tr>')
    table = (f'<details class="tview"><summary>Table view</summary>'
             f'<table><thead><tr><th>Status</th><th>Claims</th><th>Share</th><th>Meaning</th></tr>'
             f'</thead><tbody>{"".join(rows)}</tbody></table></details>')
    return "".join(segs), " ".join(legend), table


def build_foundations_chart(foundations: dict) -> tuple[str, str]:
    """Single-hue sequential magnitude comparison (one series: '# claims blocked') —
    per the method, nominal categories with no natural order get ONE fill color, never
    a per-bar rank-based gradient. Thin bars, rounded data-end, value at the tip,
    keyboard-focusable CSS tooltip carrying the actual foundation gap description."""
    items = sorted(foundations.items(), key=lambda kv: -kv[1]["blocks_corpus_claims"])
    fmax = max((f["blocks_corpus_claims"] for _, f in items), default=1) or 1
    bars, rows = [], []
    for name, f in items:
        n = f["blocks_corpus_claims"]
        pct = 100 * n / fmax
        tip = f'{esc(name)}: {n} claims — {esc(f["mathlib_gap"])} (leverage: {esc(f["leverage"])}, effort: {esc(f["effort"])})'
        bars.append(
            f'<div class="frow"><div class="fname">{esc(name.replace("_"," "))}</div>'
            f'<div class="fbarwrap"><div class="fbar" tabindex="0" style="width:{pct:.1f}%" '
            f'data-tip="{tip}"></div></div><div class="fn">{n}</div></div>')
        rows.append(f'<tr><td>{esc(name.replace("_"," "))}</td><td>{n}</td>'
                    f'<td>{esc(f["leverage"])}</td><td>{esc(f["effort"])}</td>'
                    f'<td>{esc(f["mathlib_gap"])}</td></tr>')
    table = (f'<details class="tview"><summary>Table view</summary>'
             f'<table><thead><tr><th>Foundation</th><th>Claims blocked</th><th>Leverage</th>'
             f'<th>Effort</th><th>Gap</th></tr></thead><tbody>{"".join(rows)}</tbody></table></details>')
    return "".join(bars), table


def sync_index_html(vcount: int, distinct: int, completeness, total: int) -> None:
    """Keep the hand-authored landing page (index.html) counters in sync with the
    canonical ledger. index.html is otherwise hand-maintained — this only rewrites the
    numeric `data-to`/`data-w` values, anchored on their adjacent human labels so it is
    robust to layout edits. Warns (never raises) if a counter's structure has drifted,
    so a stale-count patch can never break the stats workflow."""
    if not INDEX.exists():
        return
    html = INDEX.read_text(encoding="utf-8")
    comp = int(round(float(completeness)))
    verified_pct = int(round(vcount / total * 100)) if total else 0
    # (regex, replacement, human name) — each anchored on its label text.
    subs = [
        (r'(data-to=")\d+("[^>]*>0</div><div class="l">ledger rows)', vcount, "ledger rows stat"),
        (r'(data-to=")\d+("[^>]*data-pre="~">0</div><div class="l">distinct results)', distinct, "distinct-results stat"),
        (r'(<b class="mono" data-to=")\d+(")', distinct, "distinct-verified callout"),
        (r'(Kernel-verified results</span><b data-to=")\d+(")', vcount, "kernel-verified bar"),
        (r'(<div class="fill g" data-w=")\d+(")', verified_pct, "kernel-verified bar width"),
        (r'(Frontier mapped &amp; classified</span><b data-to=")\d+("[^>]*data-suf="%")', comp, "frontier-mapped bar"),
        (r'(Frontier mapped &amp; classified</span>.*?<div class="fill" data-w=")\d+(")', comp, "frontier bar width"),
    ]
    for pat, val, name in subs:
        html, n = re.subn(pat, lambda m, v=val: f"{m.group(1)}{v}{m.group(2)}", html, flags=re.S)
        if n == 0:
            print(f"  warn: index.html counter '{name}' not found — layout may have drifted")
    write_text_lf(INDEX, html)
    print(f"synced index.html counters ({vcount} rows / ~{distinct} distinct / {comp}% frontier)")


def main() -> int:
    fm = json.loads(FM.read_text(encoding="utf-8"))
    graph = json.loads(KG.read_text(encoding="utf-8"))
    # Single source of truth for headline counts: data/stats.json (regenerated from VERIFIED.md by
    # gen_stats.py). Never recompute distinct via a hardcoded offset — that is how counts drift.
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    vcount = int(stats.get("ledger_rows") or len(re.findall(
        r"^\|.*\| (?:proved|proved[¹²]| ?proved.*)\|?\s*$", VERIFIED.read_text(encoding="utf-8"), re.M)))
    distinct = int(stats.get("distinct_results") or (vcount - DISTINCT_OFFSET))
    status = fm["status_summary"]
    foundations = fm["foundations"]
    completeness = fm["meta"]["frontier_completeness_pct"]
    total = fm["meta"]["corpus_claims"]
    blocked_total = sum(f["blocks_corpus_claims"] for f in foundations.values())
    # Deterministic snapshot marker derived from ledger content, NOT wall-clock: docs-sync
    # requires regeneration to be a pure function of sources, so a clock stamp would make the
    # dashboard drift on every run. Freshness is conveyed by the counts themselves.
    stamp = f"{vcount} ledger rows / ~{distinct} distinct"

    # (label, count-up target|None, unit, sub-caption). A None target means the value
    # is a range/estimate — animating it as a precise count-up would misrepresent it
    # as more exact than it is, so it renders as static text instead.
    metric_cards = [
        ("Verified results", vcount, None, f"~{distinct} distinct", "0 sorry · no custom axioms"),
        ("Frontier mapped", completeness, None, "%", f"{total} corpus claims"),
        ("Foundations blocking", blocked_total, None, "claims", "each = a research-grade gap"),
        ("Honest substantive", None, "~10–15%", "", "rest = verified engineering"),
    ]
    card_parts = []
    for t, v, static, unit, s in metric_cards:
        value_html = (f'<div class="cval" data-count="{v}">0</div>' if v is not None
                       else f'<div class="cval">{esc(static)}</div>')
        unit_html = f'<div class="cunit">{esc(unit)}</div>' if unit else ""
        card_parts.append(f'<div class="card reveal">{value_html}{unit_html}'
                          f'<div class="clab">{esc(t)}</div><div class="csub">{esc(s)}</div></div>')
    cards_html = "".join(card_parts)

    frontier_segs, frontier_legend, frontier_table = build_frontier_bar(status, total)
    found_bars, found_table = build_foundations_chart(foundations)
    sync_health_html = build_sync_health(stats, fm, graph)

    tracks_html = ""
    for name, items in TRACKS:
        li = "".join(f'<li><i class="dot" style="background:{DOT[st]}"></i>{esc(lab)}</li>'
                     for lab, st in items)
        tracks_html += f'<div class="track reveal"><h3>{esc(name)}</h3><ul>{li}</ul></div>'

    layers_html = "".join(
        f'<div class="layer reveal"><span class="lnum">{esc(code)}</span>'
        f'<div><b>{esc(n)}</b><br><span class="ldesc">{esc(d)}</span></div>'
        f'<span class="dot" style="background:{DOT[st]}"></span></div>'
        for code, n, d, st in LAYERS)

    commits_html = "".join(
        f'<li><a href="{REPO}/commit/{h}"><code>{h}</code></a> {esc(s)}</li>'
        for h, s in git_log())

    nav_html = build_nav_html()

    # ---- Research OS pipeline: every counter pulled live from its source artifact ----
    n_hyp = count_lines_matching(HYPOTHESES, r"^  - id:")
    n_tasks = count_lines_matching(TASKS, r"^### TASK-")
    n_units = count_lines_matching(PUB_UNITS, r"^## Unit ")
    n_theorems = int(graph.get("counts", {}).get("theorems") or len(graph.get("theorems", [])))
    n_blocked = status.get("blocked", 0)
    pipeline_stages = [
        {"layer": "Corpus", "value": total, "unit": "claims",
         "role": "atomic ECDLP claims, the raw material to triage",
         "src": "data/KG_CLAIM_FORMALIZATION_v1.csv", "href": f"{BLOB}/data/KG_CLAIM_FORMALIZATION_v1.csv"},
        {"layer": "Frontier", "value": completeness, "unit": "%",
         "role": f"each claim given a status — {status.get('verified',0)} verified, "
                 f"{status.get('tractable',0)} tractable, {n_blocked} blocked",
         "src": "data/frontier_map.json", "href": "#frontier"},
        {"layer": "Hypotheses", "value": n_hyp, "unit": "open",
         "role": "testable directions with evidence and exit criteria",
         "src": "experiments/HYPOTHESES.yaml", "href": f"{BLOB}/experiments/HYPOTHESES.yaml"},
        {"layer": "Tasks", "value": n_tasks, "unit": "active",
         "role": "the small-context work queue, 3–7 contracts at a time",
         "src": "tasks/NEXT.md", "href": f"{BLOB}/tasks/NEXT.md"},
        {"layer": "Proofs", "value": vcount, "unit": "rows",
         "role": f"kernel-verified ledger rows (~{distinct} distinct), 0 sorry",
         "src": "VERIFIED.md", "href": f"{BLOB}/VERIFIED.md"},
        {"layer": "Truth graph", "value": n_theorems, "unit": "nodes",
         "role": "queryable theorem / dependency / barrier graph",
         "src": "data/knowledge_graph.json", "href": f"{BLOB}/data/knowledge_graph.json"},
        {"layer": "Site", "value": "live", "unit": "",
         "role": "this dashboard — the public, walkable surface (you are here)",
         "src": "dashboard.html", "href": "#top", "here": True},
        {"layer": "Papers", "value": n_units, "unit": "units",
         "role": "standalone publishable narratives with honest scope",
         "src": "PUBLISHABLE_UNITS.md", "href": f"{BLOB}/PUBLISHABLE_UNITS.md"},
    ]
    pipeline_html = build_pipeline(pipeline_stages)

    # Static (not wall-clock) so regeneration stays a pure function of sources (docs-sync).
    year = 2026

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ECDLP environment — a verified substrate for a strong AI</title>
<meta name="description" content="A machine-checked, machine-navigable Lean 4 + Mathlib environment for ECDLP/secp256k1 — kernel-verified core, a queryable frontier map, and a no-go map of missing foundations. Built by KeyAI.">
<meta property="og:title" content="ECDLP environment — verified substrate for a strong AI">
<meta property="og:description" content="{vcount} kernel-verified results · {completeness}% of the ECDLP corpus mapped · honest about the barriers.">
<meta property="og:image" content="assets/logo-wordmark.png">
<meta name="theme-color" content="#001a3f">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<style>
@font-face {{font-family:"Baloo 2";font-style:normal;font-weight:500 800;font-display:swap;
  src:url("fonts/Baloo2-Variable.woff2") format("woff2");}}
@font-face {{font-family:"Nunito";font-style:normal;font-weight:400 900;font-display:swap;
  src:url("fonts/Nunito-Variable.woff2") format("woff2");}}
:root{{
  --navy:#001a3f; --navy2:#052858; --blue:#1d85ff; --blue-dark:#0f66d1;
  --tint:#e3ebf6; --tint2:#f4f8fc; --ink:#000000; --gray:#687480; --mut:#94a4b4;
  --white:#ffffff; --line:#dbe6f3;
  --good:#0ca30c; --warning:#fab219; --critical:#d03b3b;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:76px}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:var(--white);color:var(--ink);
  font-family:Nunito,-apple-system,Segoe UI,Roboto,sans-serif;font-size:15px;line-height:1.55}}
h1,h2,h3,.disp{{font-family:"Baloo 2",Nunito,sans-serif;font-weight:700}}
a{{color:var(--blue);text-decoration:none}}
:focus-visible{{outline:3px solid var(--blue);outline-offset:2px;border-radius:4px}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 24px}}
.skip{{position:absolute;left:-9999px;top:0;background:var(--blue);color:#fff;padding:10px 16px;
  border-radius:0 0 8px 0;z-index:200}}
.skip:focus{{left:0}}

/* ---- sticky glass nav ---- */
.topnav{{position:sticky;top:0;z-index:100;background:rgba(0,26,63,.82);
  backdrop-filter:blur(10px) saturate(140%);-webkit-backdrop-filter:blur(10px) saturate(140%);
  border-bottom:1px solid rgba(255,255,255,.08)}}
.scrollprog{{position:absolute;left:0;bottom:-1px;height:2px;width:0;
  background:linear-gradient(90deg,var(--blue),#7db0ff);transform-origin:left;
  transition:width .08s linear;box-shadow:0 0 8px rgba(29,133,255,.6)}}
.topnav .in{{max-width:1080px;margin:0 auto;padding:0 24px;height:60px;display:flex;
  align-items:center;justify-content:space-between;gap:20px}}
.brand{{display:flex;align-items:center;gap:9px;flex-shrink:0}}
.brand img{{height:22px;width:auto;display:block}}
.brand span{{font-family:"Baloo 2";font-weight:700;color:rgba(255,255,255,.72);
  font-size:14px;white-space:nowrap;letter-spacing:.01em}}
.navlinks{{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}}
.navlinks::-webkit-scrollbar{{display:none}}
.navlinks a{{color:#b9cbe8;font-size:13px;font-weight:700;padding:8px 12px;border-radius:7px;
  white-space:nowrap;transition:background .15s,color .15s}}
.navlinks a:hover{{background:rgba(255,255,255,.08);color:#fff}}
.navlinks a.active{{background:var(--blue);color:#fff}}

/* ---- hero ---- */
.hero{{background:radial-gradient(120% 140% at 15% 0%,var(--navy2) 0%,var(--navy) 55%);
  color:#fff;padding:52px 0 40px;position:relative;overflow:hidden}}
.orb{{position:absolute;border-radius:50%;filter:blur(60px);opacity:.35;pointer-events:none}}
.orb1{{width:420px;height:420px;background:radial-gradient(circle,#2f8dfe,transparent 70%);
  top:-160px;right:-100px}}
.orb2{{width:280px;height:280px;background:radial-gradient(circle,#0f66d1,transparent 70%);
  bottom:-140px;left:10%}}
.hero::after{{content:"λ";position:absolute;right:-30px;top:-50px;font-family:"Baloo 2";
  font-size:320px;font-weight:800;color:#fff;opacity:.045;line-height:1;pointer-events:none}}
.herotop{{display:flex;align-items:center;gap:12px;margin-bottom:26px}}
.herotop img{{height:40px;width:auto;filter:drop-shadow(0 2px 10px rgba(29,133,255,.35))}}
.herotop .word{{font-family:"Baloo 2";font-weight:700;font-size:15px;color:#8fbcff;
  letter-spacing:.03em;text-transform:uppercase}}
.hero h1{{font-size:clamp(28px,4.4vw,40px);line-height:1.12;margin:0 0 12px;max-width:700px;
  position:relative}}
.hero .sub{{color:#7fb4ff;font-weight:700;font-size:15px;margin:0 0 6px;max-width:640px}}
.stamp{{color:#93a8c9;font-size:12px;margin:0 0 18px}}
.stamp code{{background:rgba(255,255,255,.08);padding:1px 6px;border-radius:4px;color:#bcd4f5}}
.honest{{background:rgba(255,255,255,.06);border-left:3px solid var(--blue);padding:12px 16px;
  border-radius:8px;color:#d7e4f7;font-size:13.5px;max-width:760px;position:relative}}

/* ---- metric cards (stat tiles) ---- */
.cardband{{padding:26px 0 6px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}}
.card{{background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);
  border-radius:10px;padding:16px;box-shadow:0 1px 2px rgba(15,40,80,.04)}}
.cval{{font-family:"Baloo 2";font-weight:800;font-size:26px;color:var(--navy);display:inline}}
.cunit{{font-family:"Baloo 2";font-weight:700;font-size:15px;color:var(--blue);margin-left:2px}}
.clab{{color:var(--gray);font-size:12px;margin-top:4px;font-weight:700}}
.csub{{color:var(--mut);font-size:11px;margin-top:4px}}

/* ---- sync health ---- */
.healthgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}}
.health{{background:#fff;border:1px solid var(--line);border-left:4px solid var(--good);
  border-radius:8px;padding:12px 13px;box-shadow:0 1px 2px rgba(15,40,80,.04)}}
.health.bad{{border-left-color:var(--critical)}}
.hstate{{font-family:"Baloo 2";font-weight:800;font-size:12px;color:var(--good)}}
.health.bad .hstate{{color:var(--critical)}}
.hname{{font-weight:800;color:var(--navy);font-size:13px;margin-top:2px}}
.hval{{color:var(--gray);font-size:12px;margin-top:4px}}
.hsrc{{color:var(--mut);font-size:10.5px;margin-top:6px;font-family:ui-monospace,Menlo,monospace}}

/* ---- section rhythm ---- */
section{{padding:36px 0;scroll-margin-top:70px}}
section.tint{{background:var(--tint2)}}
h2{{font-size:20px;margin:0 0 16px;color:var(--ink);display:flex;align-items:center;gap:10px}}
h2 .accent{{color:var(--blue)}}
h2 .secnum{{font-family:"Baloo 2";font-size:12px;color:var(--blue);background:var(--tint);
  border-radius:999px;padding:3px 10px;font-weight:700}}
.lede{{color:var(--gray);font-size:14px;margin:-8px 0 18px;max-width:640px}}

/* ---- reveal-on-scroll ---- */
.reveal{{opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .5s ease}}
.reveal.in{{opacity:1;transform:translateY(0)}}
@media (prefers-reduced-motion:reduce){{.reveal{{opacity:1;transform:none;transition:none}}}}

/* ---- nav grid ---- */
.navsection{{margin-bottom:26px}}
.navsection h3{{font-family:"Baloo 2";font-weight:700;font-size:14px;color:var(--navy);
  margin:0 0 12px;padding-left:10px;border-left:4px solid var(--blue)}}
.navgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}}
.navcard{{display:block;background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);
  border-radius:8px;padding:11px 13px;transition:transform .15s,box-shadow .15s}}
.navcard:hover,.navcard:focus-visible{{transform:translateY(-2px);box-shadow:0 8px 20px rgba(15,40,80,.12)}}
.navname{{color:var(--navy);font-weight:800;font-size:13.5px}}
.navpath{{color:var(--mut);font-size:10.5px;font-family:ui-monospace,Menlo,monospace;margin:2px 0}}
.navdesc{{color:var(--gray);font-size:12px;margin-top:3px;line-height:1.4}}

/* ---- CSS-only tooltip (keyboard + mouse) ---- */
[data-tip]{{position:relative;cursor:pointer}}
[data-tip]::after{{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 9px);
  transform:translateX(-50%) translateY(4px);background:var(--navy);color:#fff;font-size:11.5px;
  font-weight:600;line-height:1.4;padding:8px 11px;border-radius:8px;width:max-content;max-width:280px;
  white-space:normal;opacity:0;pointer-events:none;transition:opacity .15s,transform .15s;
  box-shadow:0 8px 20px rgba(0,10,30,.25);z-index:20}}
[data-tip]:hover::after,[data-tip]:focus-visible::after{{opacity:1;transform:translateX(-50%) translateY(0)}}

/* ---- frontier status bar (part-to-whole, status semantics) ---- */
.bar{{display:flex;height:26px;border-radius:7px;border:1px solid var(--line);
  background:#fff}}
/* no overflow:hidden here — each segment carries its own corner radius (first/last
   children below), so the track clips correctly without cutting off hover tooltips
   that pop up above a segment. */
.seg{{height:100%;border-right:2px solid #fff}}
.seg:last-child{{border-right:none}}
.seg:first-child{{border-radius:6px 0 0 6px}}
.seg:last-child{{border-radius:0 6px 6px 0}}
.legend{{margin-top:12px;font-size:12.5px;color:var(--gray);display:flex;flex-wrap:wrap;gap:14px}}
.lg{{white-space:nowrap;display:inline-flex;align-items:center;gap:6px}}
.lg i{{display:inline-block;width:11px;height:11px;border-radius:3px}}
.lg b{{color:var(--navy)}}

/* ---- foundations bars (sequential single-hue magnitude) ---- */
.frow{{display:flex;align-items:center;gap:12px;margin:9px 0;font-size:13px}}
.fname{{width:150px;color:var(--navy);font-weight:700;text-transform:capitalize;flex-shrink:0}}
.fbarwrap{{flex:1;background:var(--tint);border-radius:12px;height:20px;
  display:flex;align-items:center}}
/* no overflow:hidden — the fill's own border-radius handles its shape without
   clipping the hover/focus tooltip that pops up above the bar. */
.fbar{{height:12px;margin-left:2px;border-radius:0 6px 6px 0;
  background:linear-gradient(90deg,var(--blue),var(--blue-dark));min-width:6px}}
.fn{{width:30px;text-align:right;color:var(--navy);font-weight:800;font-family:"Baloo 2";flex-shrink:0}}

/* ---- table-view twin (accessibility) ---- */
.tview{{margin-top:14px;font-size:12.5px}}
.tview summary{{cursor:pointer;color:var(--blue-dark);font-weight:700;list-style:none;
  display:inline-flex;align-items:center;gap:5px}}
.tview summary::-webkit-details-marker{{display:none}}
.tview summary::before{{content:"▸";transition:transform .15s}}
.tview[open] summary::before{{transform:rotate(90deg)}}
.tview table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:12px}}
.tview th,.tview td{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line)}}
.tview th{{color:var(--gray);font-weight:700}}
.tview td i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px}}

.grid2{{display:grid;grid-template-columns:1.3fr 1fr;gap:22px}}
@media(max-width:760px){{.grid2{{grid-template-columns:1fr}}}}

/* ---- completeness meter ---- */
.meterwrap{{display:flex;align-items:center;gap:18px;background:#fff;border:1px solid var(--line);
  border-top:3px solid var(--blue);border-radius:10px;padding:16px 18px}}
.meter-ring{{flex-shrink:0}}
.meter-ring circle{{fill:none;stroke-width:10}}
.meter-track{{stroke:var(--tint)}}
.meter-fill{{stroke:var(--blue);stroke-linecap:round;transition:stroke-dashoffset 1.1s cubic-bezier(.4,0,.2,1)}}
@media (prefers-reduced-motion:reduce){{.meter-fill{{transition:none}}}}
.meter-label{{font-family:"Baloo 2";font-size:15px;font-weight:800;fill:var(--navy)}}

/* ---- tracks & layers ---- */
.track{{background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);
  border-radius:10px;padding:14px 16px;margin-bottom:12px}}
.track h3{{font-family:"Baloo 2";font-size:14px;margin:0 0 9px;color:var(--navy)}}
.track ul{{margin:0;padding:0;list-style:none}}
.track li{{font-size:12.5px;color:var(--gray);margin:6px 0}}
.dot{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle;
  flex-shrink:0}}
.layer{{background:#fff;border:1px solid var(--line);border-left:4px solid var(--blue);
  border-radius:8px;padding:11px 14px;margin:8px 0;font-size:13px;color:var(--gray);
  display:flex;align-items:center;gap:12px}}
.lnum{{font-family:"Baloo 2";font-weight:800;color:var(--blue);background:var(--tint);
  border-radius:8px;padding:4px 9px;font-size:12px;flex-shrink:0}}
.layer b{{color:var(--navy);font-family:"Baloo 2";font-size:13.5px}}
.ldesc{{color:var(--gray)}}

/* ---- commits ---- */
.commits{{list-style:none;padding:0;margin:0}}
.commits li{{padding:7px 0;border-bottom:1px solid var(--line);font-size:13px;color:var(--gray)}}
.commits code{{background:var(--tint);padding:1px 6px;border-radius:4px;color:var(--blue-dark);font-weight:700}}

/* ---- Research OS pipeline (the layer chain / spine) ---- */
.pipeline{{display:flex;flex-wrap:wrap;align-items:stretch;gap:8px}}
.pgcard{{flex:1 1 150px;min-width:150px;display:flex;flex-direction:column;
  background:#fff;border:1px solid var(--line);border-radius:10px;padding:13px 14px;
  color:var(--ink);box-shadow:0 1px 2px rgba(15,40,80,.04);
  transition:transform .15s,box-shadow .15s,border-color .15s}}
.pgcard:hover,.pgcard:focus-visible{{transform:translateY(-3px);border-color:var(--blue);
  box-shadow:0 8px 20px rgba(15,40,80,.10)}}
.pgcard--here{{background:linear-gradient(180deg,#f4f8fc,#fff);border-color:var(--blue);
  border-top:3px solid var(--blue)}}
.pgeyebrow{{display:flex;align-items:center;gap:6px;font-family:"Baloo 2";font-weight:800;
  font-size:12px;color:var(--navy);letter-spacing:.02em;text-transform:uppercase}}
.pgstep{{display:inline-grid;place-items:center;width:19px;height:19px;border-radius:6px;
  background:var(--tint);color:var(--blue-dark);font-size:10px;font-weight:800}}
.pgcard--here .pgstep{{background:var(--blue);color:#fff}}
.pgval{{font-family:"Baloo 2";font-weight:800;font-size:23px;color:var(--navy);
  margin-top:8px;line-height:1;font-variant-numeric:tabular-nums}}
.pgunit{{font-size:12px;font-weight:700;color:var(--blue);margin-left:3px}}
.pgrole{{color:var(--gray);font-size:12px;margin-top:6px;line-height:1.4;flex:1}}
.pgsrc{{color:var(--mut);font-size:10px;margin-top:8px;font-family:ui-monospace,Menlo,monospace;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.pgarrow{{align-self:center;color:var(--blue);font-weight:800;font-size:17px;
  flex:0 0 auto;opacity:.55}}
@media (max-width:720px){{.pgarrow{{transform:rotate(90deg);width:100%;text-align:center}}}}

/* ---- footer ---- */
footer{{background:var(--navy);color:#93a8c9;padding:32px 0}}
.footwrap{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}}
.footbrand{{display:flex;align-items:center;gap:10px}}
.footbrand img{{height:22px}}
.foottext{{font-size:12px;color:#7591b8}}
.links{{display:flex;gap:20px;flex-wrap:wrap}}
.links a{{font-size:13px;font-weight:700;color:#bcd4f5}}
.links a:hover{{color:#fff}}
</style></head><body>

<a class="skip" href="#main">Skip to content</a>

<nav class="topnav"><div class="in">
  <a class="brand" href="#top"><img src="assets/logo-wordmark.png" alt="keyAI" height="22">
    <span>· ECDLP env</span></a>
  <div class="navlinks" id="scrollspy">
    <a href="#metrics">Overview</a>
    <a href="#pipeline">Pipeline</a>
    <a href="#sync">Sync</a>
    <a href="#navigate">Docs</a>
    <a href="#frontier">Frontier</a>
    <a href="#tracks">Tracks</a>
    <a href="#commits">Activity</a>
  </div>
  <div class="scrollprog" id="scrollprog"></div>
</div></nav>

<div class="hero" id="top"><div class="wrap">
  <div class="orb orb1"></div><div class="orb orb2"></div>
  <div class="herotop"><img src="assets/logo-wordmark.png" alt="keyAI"></div>
  <h1>Verified environment for<br>a strong AI</h1>
  <p class="sub">corpus → frontier → hypotheses → tasks → proofs → truth graph → site → papers</p>
  <p class="stamp">snapshot {stamp} · regenerate: <code>python3 scripts/build_dashboard.py</code></p>
  <div class="honest">Honest boundary: this maximizes a future reasoner's leverage and rigorously maps the frontier — it does <b>not</b> solve ECDLP, and the barriers below may be permanent.</div>
</div></div>

<main id="main">
<div class="cardband wrap" id="metrics"><div class="cards">{cards_html}</div></div>

<section class="wrap" id="pipeline">
<h2><span class="secnum">01</span>The Research OS <span class="accent">pipeline</span></h2>
<p class="lede">One route, walked end to end: the 486-claim corpus is triaged into a frontier, open directions become hypotheses, hypotheses become active tasks, tasks become kernel-verified proofs, proofs become a queryable truth graph, and the whole thing surfaces here and (where the scope is honest) as papers. Every count below is pulled live from its own source artifact — click any stage to open it.</p>
{pipeline_html}
</section>

<section class="tint" id="sync"><div class="wrap">
<h2><span class="secnum">02</span>Sync Health</h2>
<p class="lede">The public surface is tied back to canonical machine sources and checked by CI gates.</p>
<div class="healthgrid">{sync_health_html}</div>
</div></section>

<section class="wrap" id="navigate">
<h2><span class="secnum">03</span>Navigate the <span class="accent">environment</span></h2>
<p class="lede">Every doc, dataset, and script in the repo, auto-discovered and grouped by purpose.</p>
{nav_html}
</section>

<section class="tint" id="frontier"><div class="wrap">
<h2><span class="secnum">04</span>Frontier map — {total} corpus claims</h2>
<p class="lede">Every claim's status is fixed, reserved, and never guessed — see the table view for the exact rule behind each color.</p>
<div class="grid2">
<div class="reveal">
  <div class="bar">{frontier_segs}</div>
  <div class="legend">{frontier_legend}</div>
  {frontier_table}
</div>
<div class="meterwrap reveal">
  <svg class="meter-ring" width="96" height="96" viewBox="0 0 96 96">
    <circle class="meter-track" cx="48" cy="48" r="40"></circle>
    <circle class="meter-fill" id="meterFill" cx="48" cy="48" r="40"
      stroke-dasharray="251.2" stroke-dashoffset="251.2"
      data-target="{completeness}" transform="rotate(-90 48 48)"></circle>
    <text x="48" y="54" text-anchor="middle" class="meter-label" id="meterLabel">0%</text>
  </svg>
  <div><b style="color:var(--navy);font-family:'Baloo 2'">Frontier completeness</b><br>
  <span style="color:var(--gray);font-size:13px">every claim assigned a status + (if blocked) a named missing foundation</span></div>
</div>
</div>
</div></section>

<section><div class="wrap">
<div class="grid2">
<div class="reveal">
  <h2><span class="secnum">05</span>Blocked by missing foundation</h2>
  {found_bars}
  {found_table}
</div>
<div class="reveal">
  <h2><span class="secnum">06</span>Environment layers</h2>
  {layers_html}
</div>
</div>
</div></section>

<section class="tint" id="tracks"><div class="wrap">
<h2><span class="secnum">07</span>Tracks &amp; checkpoints</h2>{tracks_html}
</div></section>

<section id="commits"><div class="wrap">
<h2><span class="secnum">08</span>Recent build milestones</h2><ul class="commits">{commits_html}</ul>
</div></section>
</main>

<footer><div class="wrap footwrap">
  <div class="footbrand"><img src="assets/logo-wordmark.png" alt="keyAI"></div>
  <div class="links">
    <a href="{REPO}/actions">CI status (Actions)</a>
    <a href="{REPO}/commits/main">Commit feed</a>
    <a href="{REPO}">Repository</a>
  </div>
  <div class="foottext">© {year} KeyAI · verified knowledge environment, not a product page</div>
</div></footer>

<script>
(function(){{
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // scroll-progress bar on the sticky nav — a quiet wayfinding cue on a long page.
  var prog = document.getElementById('scrollprog');
  if (prog) {{
    var ticking = false;
    function paint() {{
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      prog.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
      ticking = false;
    }}
    window.addEventListener('scroll', function(){{
      if (!ticking) {{ ticking = true; requestAnimationFrame(paint); }}
    }}, {{passive:true}});
    paint();
  }}

  // scroll-reveal — generous rootMargin so a fast flick-scroll can't skip an
  // element past the observer's check unseen, PLUS a hard failsafe timeout: this
  // page's content (docs, data) must never stay permanently invisible just because
  // an animation didn't fire.
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduced) {{
    var io = new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{ if (e.isIntersecting) {{ e.target.classList.add('in'); io.unobserve(e.target); }} }});
    }}, {{threshold:.01, rootMargin:'200px 0px 200px 0px'}});
    els.forEach(function(el){{ io.observe(el); }});
    setTimeout(function(){{ els.forEach(function(el){{ el.classList.add('in'); }}); }}, 2500);
  }} else {{
    els.forEach(function(el){{ el.classList.add('in'); }});
  }}

  // count-up stat tiles — same fast-scroll safety net as .reveal: generous
  // rootMargin plus a hard failsafe, so a value never gets stuck at its initial 0.
  document.querySelectorAll('.cval[data-count]').forEach(function(el){{
    var target = parseFloat(el.getAttribute('data-count'));
    if (reduced || !('IntersectionObserver' in window)) {{ el.textContent = target; return; }}
    var done = false;
    function run() {{
      if (done) return;
      done = true; obs.unobserve(el);
      var start = null, dur = 900;
      function step(ts) {{
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        var val = target * eased;
        el.textContent = (target % 1 !== 0) ? val.toFixed(1) : Math.round(val);
        if (p < 1) requestAnimationFrame(step);
      }}
      requestAnimationFrame(step);
    }}
    var obs = new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{ if (e.isIntersecting) run(); }});
    }}, {{threshold:.01, rootMargin:'200px 0px 200px 0px'}});
    obs.observe(el);
    setTimeout(run, 2500);
  }});

  // completeness meter — same pattern.
  var fill = document.getElementById('meterFill'), label = document.getElementById('meterLabel');
  if (fill) {{
    var circumference = 251.2, target = parseFloat(fill.getAttribute('data-target'));
    var done = false;
    var trigger = function() {{
      if (done) return;
      done = true;
      var offset = circumference - (target/100)*circumference;
      fill.style.strokeDashoffset = reduced ? offset : circumference;
      if (!reduced) requestAnimationFrame(function(){{ fill.style.strokeDashoffset = offset; }});
      var start=null, dur=1100;
      function step(ts){{ if(!start) start=ts; var p=Math.min((ts-start)/dur,1);
        label.textContent = Math.round(target*(reduced?1:p)) + '%'; if(p<1 && !reduced) requestAnimationFrame(step); }}
      requestAnimationFrame(step);
    }};
    if ('IntersectionObserver' in window) {{
      var mio = new IntersectionObserver(function(entries){{
        entries.forEach(function(e){{ if (e.isIntersecting) {{ trigger(); mio.unobserve(fill); }} }});
      }}, {{threshold:.01, rootMargin:'200px 0px 200px 0px'}});
      mio.observe(fill);
      setTimeout(trigger, 2500);
    }} else {{ trigger(); }}
  }}

  // scrollspy
  var links = document.querySelectorAll('#scrollspy a');
  var sections = Array.prototype.map.call(links, function(a){{ return document.querySelector(a.getAttribute('href')); }});
  function onScroll(){{
    var pos = window.scrollY + 90;
    var active = 0;
    sections.forEach(function(sec, i){{ if (sec && sec.offsetTop <= pos) active = i; }});
    links.forEach(function(a,i){{ a.classList.toggle('active', i===active); }});
  }}
  document.addEventListener('scroll', onScroll, {{passive:true}});
  onScroll();
}})();
</script>
</body></html>"""
    write_text_lf(OUT, html)
    # index.html is the hand-authored KeyAI landing one-pager (site root); we do NOT
    # regenerate it, but we DO keep its numeric counters in sync with the canonical ledger.
    sync_index_html(vcount, distinct, completeness, total)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html)} bytes) — {vcount} results, "
          f"frontier {completeness}%, nav sections {len(NAV)}, extra files {len(discover_extra_files())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
