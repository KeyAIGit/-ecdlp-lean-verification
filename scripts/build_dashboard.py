#!/usr/bin/env python3
"""Build dashboard.html — a single self-contained page to OBSERVE the environment.

Consolidates the live state into one visual panel: headline metrics, the L1-L5 layers,
the 3 tracks + checkpoints, the frontier map (status + blocked-by-foundation), and the
recent build milestones (git log). Open dashboard.html in a browser, or view it rendered.

This is a SNAPSHOT (regenerate with this script). For truly-live status use the GitHub
Actions tab (CI green/red in real time) and the commit history (each verified step = a
commit). Run: python3 scripts/build_dashboard.py
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

STATUS_COLOR = {
    "verified": "#22c55e", "tractable": "#84cc16", "partial": "#eab308",
    "blocked": "#ef4444", "informal": "#94a3b8", "unassigned": "#64748b",
}
# current track/checkpoint state (update as tracks advance)
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
DOT = {"done": "#22c55e", "wip": "#eab308", "todo": "#64748b",
       "strong": "#22c55e", "growing": "#84cc16", "exists": "#eab308", "underused": "#94a3b8"}


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


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main() -> int:
    fm = json.loads(FM.read_text(encoding="utf-8"))
    vcount = len(re.findall(r"^\|.*\| (?:proved|proved[¹²]| ?proved.*)\|?\s*$",
                            VERIFIED.read_text(encoding="utf-8"), re.M))
    status = fm["status_summary"]
    foundations = fm["foundations"]
    completeness = fm["meta"]["frontier_completeness_pct"]
    total = fm["meta"]["corpus_claims"]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # metric cards
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

    # status bar
    order = ["verified", "tractable", "partial", "blocked", "informal", "unassigned"]
    seg = "".join(
        f'<div class="seg" style="width:{100*status.get(k,0)/total:.1f}%;background:{STATUS_COLOR[k]}" '
        f'title="{k}: {status.get(k,0)}"></div>' for k in order if status.get(k, 0))
    legend = " ".join(
        f'<span class="lg"><i style="background:{STATUS_COLOR[k]}"></i>{k} {status.get(k,0)}</span>'
        for k in order if status.get(k, 0))

    # foundations bars
    fmax = max((f["blocks_corpus_claims"] for f in foundations.values()), default=1) or 1
    frows = "".join(
        f'<div class="frow"><div class="fname">{esc(k)}</div>'
        f'<div class="fbarwrap"><div class="fbar" style="width:{100*f["blocks_corpus_claims"]/fmax:.0f}%"></div></div>'
        f'<div class="fn">{f["blocks_corpus_claims"]}</div></div>'
        for k, f in sorted(foundations.items(), key=lambda kv: -kv[1]["blocks_corpus_claims"]))

    # tracks
    tracks_html = ""
    for name, items in TRACKS:
        li = "".join(f'<li><i class="dot" style="background:{DOT[st]}"></i>{esc(lab)}</li>'
                     for lab, st in items)
        tracks_html += f'<div class="track"><h3>{esc(name)}</h3><ul>{li}</ul></div>'

    # layers
    layers_html = "".join(
        f'<div class="layer"><span class="dot" style="background:{DOT[st]}"></span>'
        f'<b>{esc(n)}</b> — {esc(d)}</div>' for n, d, st in LAYERS)

    # commits
    commits_html = "".join(
        f'<li><a href="{REPO}/commit/{h}"><code>{h}</code></a> {esc(s)}</li>'
        for h, s in git_log())

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ECDLP environment — dashboard</title><style>
:root{{--bg:#0b1020;--panel:#141b30;--line:#243049;--tx:#e2e8f0;--mut:#94a3b8;--acc:#60a5fa}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--tx);
font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}}a{{color:var(--acc);text-decoration:none}}
.wrap{{max-width:960px;margin:0 auto;padding:24px}}
h1{{font-size:22px;margin:0 0 4px}}.sub{{color:var(--mut);margin:0 0 4px}}
.stamp{{color:var(--mut);font-size:12px}}
.honest{{background:#1e293b;border-left:3px solid var(--acc);padding:10px 14px;border-radius:6px;
margin:16px 0;color:#cbd5e1;font-size:13px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:18px 0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}}
.cval{{font-size:22px;font-weight:700;color:#fff}}.clab{{color:var(--mut);font-size:12px;margin-top:2px}}
.csub{{color:#64748b;font-size:11px;margin-top:4px}}
h2{{font-size:15px;margin:26px 0 10px;color:#cbd5e1;border-bottom:1px solid var(--line);padding-bottom:6px}}
.bar{{display:flex;height:22px;border-radius:6px;overflow:hidden;border:1px solid var(--line)}}
.seg{{height:100%}}.legend{{margin-top:8px;font-size:12px;color:var(--mut)}}
.lg{{margin-right:12px;white-space:nowrap}}.lg i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:middle}}
.frow{{display:flex;align-items:center;gap:10px;margin:5px 0;font-size:13px}}
.fname{{width:170px;color:#cbd5e1}}.fbarwrap{{flex:1;background:#0f172a;border-radius:4px;height:14px;overflow:hidden}}
.fbar{{height:100%;background:linear-gradient(90deg,#ef4444,#f97316)}}.fn{{width:28px;text-align:right;color:var(--mut)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}@media(max-width:700px){{.grid2{{grid-template-columns:1fr}}}}
.track{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:12px}}
.track h3{{font-size:13px;margin:0 0 8px;color:#fff}}.track ul{{margin:0;padding:0;list-style:none}}
.track li{{font-size:12.5px;color:#cbd5e1;margin:5px 0}}
.dot{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}}
.layer{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:9px 12px;margin:6px 0;font-size:13px}}
.commits{{list-style:none;padding:0;margin:0}}.commits li{{padding:5px 0;border-bottom:1px solid var(--line);font-size:13px}}
.commits code{{background:#0f172a;padding:1px 6px;border-radius:4px;color:#93c5fd}}
.links a{{margin-right:16px;font-size:13px}}
</style></head><body><div class="wrap">
<h1>ECDLP · verified environment for a strong AI</h1>
<p class="sub">A machine-checked, machine-navigable substrate — L1 verified core · L2 frontier map · L3 navigable structure · L4 objects · L5 engine.</p>
<p class="stamp">snapshot {stamp} · regenerate: <code>python3 scripts/build_dashboard.py</code></p>
<div class="honest">Honest boundary: this maximizes a future reasoner's leverage and rigorously maps the frontier — it does <b>not</b> solve ECDLP, and the barriers below may be permanent.</div>
<div class="cards">{cards_html}</div>

<h2>Frontier map — {total} corpus claims ({completeness}% mapped)</h2>
<div class="bar">{seg}</div><div class="legend">{legend}</div>

<div class="grid2" style="margin-top:16px">
<div><h2 style="margin-top:0">Blocked by missing foundation</h2>{frows}</div>
<div><h2 style="margin-top:0">Environment layers</h2>{layers_html}</div>
</div>

<h2>Tracks &amp; checkpoints</h2>{tracks_html}

<h2>Recent build milestones</h2><ul class="commits">{commits_html}</ul>

<h2>Live views (real-time, external)</h2>
<div class="links">
<a href="{REPO}/actions">▶ CI status (Actions)</a>
<a href="{REPO}/commits/main">▶ commit feed</a>
<a href="{REPO}/blob/main/VERIFIED.md">▶ ledger</a>
<a href="{REPO}/blob/main/COVERAGE.md">▶ coverage</a>
<a href="{REPO}/blob/main/data/frontier_map.json">▶ frontier map (json)</a>
</div>
</div></body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html)} bytes) — {vcount} results, "
          f"frontier {completeness}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
