#!/usr/bin/env python3
"""Build dashboard.html / index.html — the navigable home page of the environment.

Visual identity matches the KeyAI pitch-deck brand (navy #001a3f, accent blue #1d85ff,
rounded geometric type): a dark hero band, white/light-tint content sections, cards with
a thin blue top rule, bold black section headings. Colors were sampled directly from the
deck's rendered slides, not guessed.

Consolidates live state (metrics, L1-L5 layers, tracks/checkpoints, frontier map, recent
milestones) AND a full, auto-discovered navigation of every doc/data/script in the repo,
grouped by purpose, so nothing is ever missing or hard to find. Unknown/new files fall
into an "Other" bucket automatically rather than being silently dropped.

This is a SNAPSHOT (regenerate with this script — also run on every ledger change so the
live GitHub Pages / htmlpreview link stays current). For truly-live status use the GitHub
Actions tab (CI green/red in real time) and the commit history.

Run: python3 scripts/build_dashboard.py
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FM = ROOT / "data" / "frontier_map.json"
VERIFIED = ROOT / "VERIFIED.md"
OUT = ROOT / "dashboard.html"
REPO = "https://github.com/KeyAIGit/-ecdlp-lean-verification"
BLOB = f"{REPO}/blob/main"
TREE = f"{REPO}/tree/main"

# status-encoding colors (data semantics, not brand chrome — kept distinct on purpose)
STATUS_COLOR = {
    "verified": "#22c55e", "tractable": "#84cc16", "partial": "#eab308",
    "blocked": "#ef4444", "informal": "#94a3b8", "unassigned": "#64748b",
}
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
    ("L1 Verified core", "kernel-checked theorems (absolute trust)", "strong"),
    ("L2 Frontier map", "what's open/blocked & by which missing foundation", "growing"),
    ("L3 Navigable structure", "machine-readable graph + queryable data", "exists"),
    ("L4 Formalized objects", "GLV (cube-root + torsion-preserving), torsion, division polys", "growing"),
    ("L5 Engine", "AI+kernel pipeline; self-extensible substrate", "underused"),
]
DOT = {"done": "#22c55e", "wip": "#eab308", "todo": "#94a3b8",
       "strong": "#22c55e", "growing": "#1d85ff", "exists": "#eab308", "underused": "#94a3b8"}

NAV = [
    ("Start here", [
        ("README.md", "Project overview, layout, build instructions"),
        ("AGENTS.md", "Orientation for any Claude instance — read this first"),
        ("ENVIRONMENT_PLAN.md", "The strategic plan: L1-L5 layers, 3 tracks, checkpoints"),
        ("CLAUDE.md", "Working conventions for automated/assisted runs"),
        ("AGENT.md", "The authoritative protocol"),
        ("SETUP.md", "Minimal build command"),
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


def git_log(n: int = 14) -> list[tuple[str, str]]:
    try:
        out = subprocess.run(["git", "log", "--format=%h\t%s", f"-{n}", "origin/main"],
                             cwd=ROOT, text=True, capture_output=True, timeout=20).stdout
    except Exception:
        out = ""
    rows = []
    for line in out.strip().splitlines():
        if "\t" in line:
            h, s = line.split("\t", 1)
            rows.append((h, s))
    return rows


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
            rel = str(p.relative_to(ROOT))
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
        sections.append(f'<div class="navsection"><h3>{esc(title)}</h3>'
                        f'<div class="navgrid">{"".join(cards)}</div></div>')

    extras = discover_extra_files()
    if extras:
        cards = "".join(
            f'<a class="navcard" href="{esc(nav_url(p, None))}"><div class="navname">'
            f'{esc(p.split("/")[-1])}</div><div class="navpath">{esc(p)}</div>'
            f'<div class="navdesc">not yet categorized (auto-discovered so it stays visible)</div></a>'
            for p in extras)
        sections.append(f'<div class="navsection"><h3>Other (auto-discovered)</h3>'
                        f'<div class="navgrid">{cards}</div></div>')
    return "".join(sections)


def main() -> int:
    fm = json.loads(FM.read_text(encoding="utf-8"))
    vcount = len(re.findall(r"^\|.*\| (?:proved|proved[¹²]| ?proved.*)\|?\s*$",
                            VERIFIED.read_text(encoding="utf-8"), re.M))
    status = fm["status_summary"]
    foundations = fm["foundations"]
    completeness = fm["meta"]["frontier_completeness_pct"]
    total = fm["meta"]["corpus_claims"]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cards = [
        ("Verified results", f"{vcount} rows / ~{vcount-10} distinct", "0 sorry · no custom axioms"),
        ("Frontier map", f"{completeness}% mapped", f"{total} corpus claims"),
        ("Foundations blocking", f"{sum(f['blocks_corpus_claims'] for f in foundations.values())} claims",
         "each = a research-grade gap"),
        ("Honest substantive", "~10–15%", "rest = verified engineering"),
    ]
    cards_html = "".join(
        f'<div class="card"><div class="cval">{esc(v)}</div>'
        f'<div class="clab">{esc(t)}</div><div class="csub">{esc(s)}</div></div>'
        for t, v, s in cards)

    order = ["verified", "tractable", "partial", "blocked", "informal", "unassigned"]
    seg = "".join(
        f'<div class="seg" style="width:{100*status.get(k,0)/total:.1f}%;background:{STATUS_COLOR[k]}" '
        f'title="{k}: {status.get(k,0)}"></div>' for k in order if status.get(k, 0))
    legend = " ".join(
        f'<span class="lg"><i style="background:{STATUS_COLOR[k]}"></i>{k} {status.get(k,0)}</span>'
        for k in order if status.get(k, 0))

    fmax = max((f["blocks_corpus_claims"] for f in foundations.values()), default=1) or 1
    frows = "".join(
        f'<div class="frow"><div class="fname">{esc(k)}</div>'
        f'<div class="fbarwrap"><div class="fbar" style="width:{100*f["blocks_corpus_claims"]/fmax:.0f}%"></div></div>'
        f'<div class="fn">{f["blocks_corpus_claims"]}</div></div>'
        for k, f in sorted(foundations.items(), key=lambda kv: -kv[1]["blocks_corpus_claims"]))

    tracks_html = ""
    for name, items in TRACKS:
        li = "".join(f'<li><i class="dot" style="background:{DOT[st]}"></i>{esc(lab)}</li>'
                     for lab, st in items)
        tracks_html += f'<div class="track"><h3>{esc(name)}</h3><ul>{li}</ul></div>'

    layers_html = "".join(
        f'<div class="layer"><span class="dot" style="background:{DOT[st]}"></span>'
        f'<b>{esc(n)}</b> — {esc(d)}</div>' for n, d, st in LAYERS)

    commits_html = "".join(
        f'<li><a href="{REPO}/commit/{h}"><code>{h}</code></a> {esc(s)}</li>'
        for h, s in git_log())

    nav_html = build_nav_html()

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ECDLP environment — dashboard</title>
<style>
/* Self-hosted (variable-weight) fonts — no external CDN dependency, matches the KeyAI
   deck's rounded geometric type: Baloo 2 for headings/display, Nunito for body. */
@font-face {{font-family:"Baloo 2";font-style:normal;font-weight:500 800;font-display:swap;
  src:url("fonts/Baloo2-Variable.woff2") format("woff2");}}
@font-face {{font-family:"Nunito";font-style:normal;font-weight:400 900;font-display:swap;
  src:url("fonts/Nunito-Variable.woff2") format("woff2");}}
:root{{
  --navy:#001a3f; --navy2:#052858; --blue:#1d85ff; --blue-dark:#0f66d1;
  --tint:#e3ebf6; --tint2:#eef4fc; --ink:#000000; --gray:#687480; --mut:#94a4b4;
  --white:#ffffff; --line:#dbe6f3;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--white);color:var(--ink);
  font-family:Nunito,-apple-system,Segoe UI,Roboto,sans-serif;font-size:15px;line-height:1.55}}
h1,h2,h3,.disp{{font-family:"Baloo 2",Nunito,sans-serif;font-weight:700}}
a{{color:var(--blue);text-decoration:none}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 24px}}

/* ---- hero (navy, matches the deck's cover slide) ---- */
.hero{{background:radial-gradient(120% 140% at 15% 0%,var(--navy2) 0%,var(--navy) 55%);
  color:#fff;padding:56px 0 40px;position:relative;overflow:hidden}}
.hero::after{{content:"λ";position:absolute;right:-40px;top:-60px;font-family:"Baloo 2";
  font-size:340px;font-weight:800;color:#ffffff;opacity:.045;line-height:1;pointer-events:none}}
.mark{{display:flex;align-items:center;gap:10px;margin-bottom:22px}}
.mark .dot{{width:16px;height:16px;border:3px solid var(--blue);border-radius:50%;background:transparent}}
.mark .stem{{width:3px;height:20px;background:var(--blue);margin-left:-9px;border-radius:2px}}
.mark .word{{font-family:"Baloo 2";font-weight:700;font-size:20px;color:var(--blue);letter-spacing:.2px}}
.hero h1{{font-size:34px;line-height:1.15;margin:0 0 10px;max-width:680px}}
.hero .sub{{color:var(--blue);font-weight:700;font-size:15px;margin:0 0 6px}}
.stamp{{color:#93a8c9;font-size:12px;margin:0 0 18px}}
.stamp code{{background:rgba(255,255,255,.08);padding:1px 6px;border-radius:4px;color:#bcd4f5}}
.honest{{background:rgba(255,255,255,.06);border-left:3px solid var(--blue);padding:12px 16px;
  border-radius:8px;color:#d7e4f7;font-size:13.5px;max-width:760px;position:relative}}

/* ---- metric cards ---- */
.cardband{{padding:26px 0 6px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}}
.card{{background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);
  border-radius:10px;padding:16px;box-shadow:0 1px 2px rgba(15,40,80,.04)}}
.cval{{font-family:"Baloo 2";font-weight:800;font-size:23px;color:var(--navy)}}
.clab{{color:var(--gray);font-size:12px;margin-top:3px;font-weight:700}}
.csub{{color:var(--mut);font-size:11px;margin-top:4px}}

/* ---- section bands (alternate white / light tint like the deck) ---- */
section{{padding:34px 0}}
section.tint{{background:var(--tint2)}}
h2{{font-size:20px;margin:0 0 16px;color:var(--ink)}}
h2 .accent{{color:var(--blue)}}

/* ---- nav ---- */
.navsection{{margin-bottom:26px}}
.navsection h3{{font-family:"Baloo 2";font-weight:700;font-size:14px;color:var(--navy);
  margin:0 0 12px;padding-left:10px;border-left:4px solid var(--blue)}}
.navgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}}
.navcard{{display:block;background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);
  border-radius:8px;padding:11px 13px;transition:transform .15s,box-shadow .15s}}
.navcard:hover{{transform:translateY(-2px);box-shadow:0 6px 16px rgba(15,40,80,.10)}}
.navname{{color:var(--navy);font-weight:800;font-size:13.5px}}
.navpath{{color:var(--mut);font-size:10.5px;font-family:ui-monospace,Menlo,monospace;margin:2px 0}}
.navdesc{{color:var(--gray);font-size:12px;margin-top:3px;line-height:1.4}}

/* ---- frontier bar ---- */
.bar{{display:flex;height:22px;border-radius:6px;overflow:hidden;border:1px solid var(--line)}}
.seg{{height:100%}}.legend{{margin-top:10px;font-size:12px;color:var(--gray)}}
.lg{{margin-right:14px;white-space:nowrap}}.lg i{{display:inline-block;width:10px;height:10px;
  border-radius:2px;margin-right:5px;vertical-align:middle}}

/* ---- foundations bars ---- */
.frow{{display:flex;align-items:center;gap:10px;margin:6px 0;font-size:13px}}
.fname{{width:170px;color:var(--navy);font-weight:700}}
.fbarwrap{{flex:1;background:var(--tint);border-radius:4px;height:14px;overflow:hidden}}
.fbar{{height:100%;background:linear-gradient(90deg,var(--blue),var(--navy))}}
.fn{{width:28px;text-align:right;color:var(--gray);font-weight:700}}

.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media(max-width:700px){{.grid2{{grid-template-columns:1fr}}}}

/* ---- tracks & layers ---- */
.track{{background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);
  border-radius:10px;padding:14px 16px;margin-bottom:12px}}
.track h3{{font-family:"Baloo 2";font-size:14px;margin:0 0 9px;color:var(--navy)}}
.track ul{{margin:0;padding:0;list-style:none}}
.track li{{font-size:12.5px;color:var(--gray);margin:6px 0}}
.dot{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}}
.layer{{background:#fff;border:1px solid var(--line);border-left:4px solid var(--blue);
  border-radius:8px;padding:10px 14px;margin:7px 0;font-size:13px;color:var(--gray)}}
.layer b{{color:var(--navy)}}

/* ---- commits + footer links ---- */
.commits{{list-style:none;padding:0;margin:0}}
.commits li{{padding:6px 0;border-bottom:1px solid var(--line);font-size:13px;color:var(--gray)}}
.commits code{{background:var(--tint);padding:1px 6px;border-radius:4px;color:var(--blue-dark);font-weight:700}}
.links{{display:flex;gap:22px;flex-wrap:wrap}}
.links a{{font-size:13.5px;font-weight:700}}
footer{{padding:28px 0 40px;color:var(--mut);font-size:12px}}
</style></head><body>

<div class="hero"><div class="wrap">
  <div class="mark"><span class="dot"></span><span class="stem"></span><span class="word">ECDLP&nbsp;·&nbsp;env</span></div>
  <h1>Verified environment for<br>a strong AI</h1>
  <p class="sub">L1 verified core · L2 frontier map · L3 navigable structure · L4 objects · L5 engine</p>
  <p class="stamp">snapshot {stamp} · regenerate: <code>python3 scripts/build_dashboard.py</code></p>
  <div class="honest">Honest boundary: this maximizes a future reasoner's leverage and rigorously maps the frontier — it does <b>not</b> solve ECDLP, and the barriers below may be permanent.</div>
</div></div>

<div class="cardband wrap">{cards_html}</div>

<section class="wrap">
<h2>Navigate the <span class="accent">environment</span></h2>
{nav_html}
</section>

<section class="tint"><div class="wrap">
<h2>Frontier map — {total} corpus claims ({completeness}% mapped)</h2>
<div class="bar">{seg}</div><div class="legend">{legend}</div>
</div></section>

<section><div class="wrap">
<div class="grid2">
<div><h2>Blocked by missing foundation</h2>{frows}</div>
<div><h2>Environment layers</h2>{layers_html}</div>
</div>
</div></section>

<section class="tint"><div class="wrap">
<h2>Tracks &amp; checkpoints</h2>{tracks_html}
</div></section>

<section><div class="wrap">
<h2>Recent build milestones</h2><ul class="commits">{commits_html}</ul>
</div></section>

<footer><div class="wrap">
<div class="links">
<a href="{REPO}/actions">▶ CI status (Actions)</a>
<a href="{REPO}/commits/main">▶ commit feed</a>
<a href="{REPO}">▶ repository root</a>
</div>
</div></footer>
</body></html>"""
    OUT.write_text(html, encoding="utf-8")
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} + index.html ({len(html)} bytes) — {vcount} results, "
          f"frontier {completeness}%, nav sections {len(NAV)}, extra files {len(discover_extra_files())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
