#!/usr/bin/env python3
"""Generate KeyAI's product site from canonical repository state."""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/KeyAIGit/-ecdlp-lean-verification"
BLOB = f"{REPO}/blob/main"
TREE = f"{REPO}/tree/main"
ASSET_VERSION = "20260722-1"

PRODUCT_PATH = ROOT / "repo" / "PRODUCT_MODEL.json"
DECISION_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
FORMAL_PATH = ROOT / "repo" / "FORMAL_SUBSTRATE.json"
STATS_PATH = ROOT / "data" / "stats.json"
FRONTIER_PATH = ROOT / "data" / "frontier_map.json"
GRAPH_PATH = ROOT / "data" / "knowledge_graph.json"
TASKS_PATH = ROOT / "tasks" / "NEXT.md"

INDEX_PATH = ROOT / "index.html"
DASHBOARD_PATH = ROOT / "dashboard.html"
EXPLORE_PATH = ROOT / "explore.html"

ROUTE_STATUS = {
    "guardrail": ("Guardrail", "guardrail"),
    "baseline": ("Baseline", "baseline"),
    "constant_factor_only": ("Constant factor", "constant_factor_only"),
    "ruled_out_for_target": ("Ruled out for target", "ruled_out_for_target"),
    "open_parked": ("Open, parked", "open_parked"),
    "monitor": ("Monitor", "monitor"),
    "conditional_only": ("Conditional inputs", "conditional_only"),
    "separate_threat_model": ("Separate threat model", "separate_threat_model"),
}

ROUTE_STATUS_ORDER = [
    "guardrail",
    "baseline",
    "constant_factor_only",
    "ruled_out_for_target",
    "open_parked",
    "monitor",
    "conditional_only",
    "separate_threat_model",
]

FORMAL_STATUS = {
    "closed": ("Closed", "closed"),
    "blocked": ("Blocked", "blocked"),
    "parked": ("Parked", "parked"),
    "out_of_release": ("Outside release", "out_of_release"),
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def repo_url(path: str) -> str:
    if path.endswith("/"):
        return f"{TREE}/{path.rstrip('/')}"
    return f"{BLOB}/{path}"


def evidence_links(paths: list[str], limit: int | None = None) -> str:
    selected = paths if limit is None else paths[:limit]
    return "".join(
        f'<a class="source-link" href="{esc(repo_url(path))}">{esc(path)}</a>'
        for path in selected
    )


def status_badge(status: str, label: str | None = None) -> str:
    route_meta = ROUTE_STATUS.get(status)
    formal_meta = FORMAL_STATUS.get(status)
    direct_status = status if status in {"blue", "green", "amber", "red", "violet", "gray"} else None
    default_label = route_meta[0] if route_meta else formal_meta[0] if formal_meta else status
    css_status = (
        route_meta[1]
        if route_meta
        else formal_meta[1]
        if formal_meta
        else direct_status or "gray"
    )
    return f'<span class="status status--{esc(css_status)}">{esc(label or default_label)}</span>'


def parse_tasks() -> list[dict[str, str]]:
    text = TASKS_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^### (TASK-\d+) - (.+?)\n\n"
        r"Status: ([^\n]+)\n"
        r"Kind: ([^\n]+)\n"
        r"Hypothesis: ([^\n]+)\n"
        r"Why it matters: (.*?)(?=\nInputs:)",
        re.MULTILINE | re.DOTALL,
    )
    tasks = []
    for match in pattern.finditer(text):
        why = re.sub(r"\s+", " ", match.group(6)).strip()
        tasks.append(
            {
                "id": match.group(1),
                "title": match.group(2).strip(),
                "status": match.group(3).strip(),
                "kind": match.group(4).strip(),
                "hypothesis": match.group(5).strip(),
                "why": why,
            }
        )
    return tasks


def task_status_badge(status: str) -> str:
    if status == "active":
        return status_badge("blue", "Active")
    if status.startswith("blocked"):
        return status_badge("blocked", "Blocked")
    if status.startswith("parked"):
        return status_badge("parked", "Parked")
    return status_badge("gray", status.replace("_", " ").title())


def page_head(title: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="assets/logo-wordmark.png">
  <meta name="theme-color" content="#f7f8f6">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <link rel="stylesheet" href="assets/site.css?v={ASSET_VERSION}">
</head>"""


def site_header() -> str:
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="shell site-header__inner">
    <a class="brand-link" href="index.html" aria-label="KeyAI home">
      <img src="assets/logo-wordmark.png" alt="KeyAI" width="116" height="44">
    </a>
    <nav class="primary-nav" aria-label="Primary navigation">
      <a data-nav-page="product" href="index.html">Product</a>
      <a data-nav-page="workspace" href="dashboard.html">Workspace</a>
      <a data-nav-page="routes" href="explore.html">Route map</a>
      <a href="{REPO}/blob/main/STATUS.md">Status</a>
      <a class="nav-cta" href="{REPO}">GitHub</a>
    </nav>
  </div>
</header>"""


def site_footer(product: dict) -> str:
    return f"""<footer class="site-footer">
  <div class="shell site-footer__inner">
    <img src="assets/logo-wordmark.png" alt="KeyAI" width="100" height="38">
    <p>{esc(product["category"])}. Current stage: {esc(product["current_stage"]["label"])}.
      Lean is the current exact verifier; product and customer claims remain evidence-gated.</p>
    <nav class="footer-links" aria-label="Footer navigation">
      <a href="dashboard.html">Reference workspace</a>
      <a href="explore.html">Decision routes</a>
      <a href="{REPO}/blob/main/repo/PRODUCT_MODEL.json">Product model</a>
      <a href="{REPO}">Repository</a>
    </nav>
  </div>
</footer>
<script src="assets/site.js?v={ASSET_VERSION}"></script>
</body>
</html>"""


def build_index(
    product: dict,
    stats: dict,
    frontier: dict,
    decisions: dict,
    formal: dict,
) -> str:
    selection = decisions["route_selection"]
    routes = decisions["routes"]
    current_stage = product["current_stage"]
    mvp = product["mvp"]
    workflow_html = "".join(
        f"""<article class="workflow__step">
  <span class="workflow__index">{index:02d}</span>
  <h3>{esc(step["label"])}</h3>
  <p>{esc(step["outcome"])}</p>
</article>"""
        for index, step in enumerate(product["workflow"], start=1)
    )
    capabilities_html = "".join(
        f"""<article class="evidence-card">
  <h3>{esc(capability["label"])}</h3>
  <p>Inspectable in the reference repository and checked by the repository gates.</p>
  {evidence_links(capability["evidence"], limit=1)}
</article>"""
        for capability in current_stage["capabilities_now"]
    )
    current_html = "".join(f"<li>{esc(item['label'])}</li>" for item in current_stage["capabilities_now"])
    not_yet_html = "".join(f"<li>{esc(item)}</li>" for item in current_stage["not_yet"])
    metric_html = "".join(
        f"""<div class="metric-line">
  <span class="metric-line__id">{esc(metric["id"])}</span>
  <p>{esc(metric["target"])}</p>
</div>"""
        for metric in mvp["exit_metrics"]
    )
    rationale_html = "".join(f"<li>{esc(item)}</li>" for item in selection["rationale"][:3])
    route_visual = json.dumps(
        [{"id": route["id"], "status": route["status"]} for route in routes],
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    proof_closed = sum(1 for node in formal["critical_nodes"] if node["status"] == "closed")
    description = product["one_liner"]
    return f"""{page_head("KeyAI | Verification workspace for AI research", description)}
<body data-page="product">
{site_header()}
<main id="main">
  <section class="hero" aria-labelledby="hero-title">
    <canvas class="hero__canvas" id="route-canvas" aria-hidden="true"></canvas>
    <div class="shell hero__inner">
      <div class="hero__copy">
        <p class="eyebrow">{esc(product["category"])}</p>
        <h1 id="hero-title">The verification workspace for AI research.</h1>
        <p class="hero__lede">{esc(product["one_liner"])}
          It keeps claims, evidence, decisions, verifier outcomes, and provenance in one inspectable state.</p>
        <div class="actions">
          <a class="button button--primary" href="dashboard.html">Open the reference workspace</a>
          <a class="button" href="{REPO}/blob/main/repo/PRODUCT_MODEL.json">Inspect the product contract</a>
        </div>
        <p class="stage-note">{status_badge("blue", current_stage["label"])}
          <span>{esc(current_stage["summary"])}</span></p>
      </div>
    </div>
    <script type="application/json" id="route-visual-data">{route_visual}</script>
  </section>

  <section class="live-band" aria-label="Live reference environment">
    <div class="shell live-band__inner">
      <div class="live-band__context">
        <strong>Live reference: secp256k1 ECDLP</strong>
        <span>{esc(product["reference_environment"]["boundary"])}</span>
      </div>
      <div class="live-metric"><div class="live-metric__value" data-metric="ledger-rows">{stats["ledger_rows"]}</div>
        <div class="live-metric__label">verified ledger rows</div></div>
      <div class="live-metric"><div class="live-metric__value" data-metric="distinct-results">~{stats["distinct_results"]}</div>
        <div class="live-metric__label">distinct results</div></div>
      <div class="live-metric"><div class="live-metric__value">{len(routes)}</div>
        <div class="live-metric__label">routes evaluated</div></div>
      <div class="live-metric"><div class="live-metric__value">{len(selection["selected_route_ids"])}</div>
        <div class="live-metric__label">routes selected</div></div>
    </div>
  </section>

  <section class="band band--white" id="product">
    <div class="shell split">
      <div class="split__lead">
        <p class="eyebrow">The missing layer</p>
        <h2>AI can propose. KeyAI keeps the research state.</h2>
        <p>Individual agents already write proofs and code. A long research program needs a durable answer
          to a different question: what should the next agent trust, challenge, or stop doing?</p>
      </div>
      <div class="principle-list">
        <article class="principle">
          <span class="principle__number">01</span>
          <div><h3>Before execution</h3><p>Bind each task to a source, exact scope, route, and falsifiable exit condition.</p></div>
        </article>
        <article class="principle">
          <span class="principle__number">02</span>
          <div><h3>At verification</h3><p>Record what the declared verifier accepted and what remains a semantic or empirical assumption.</p></div>
        </article>
        <article class="principle">
          <span class="principle__number">03</span>
          <div><h3>After the attempt</h3><p>Retain accepted results, negative evidence, stop conditions, and a reproducible rollback path.</p></div>
        </article>
      </div>
    </div>
  </section>

  <section class="band" id="workflow">
    <div class="shell">
      <div class="section-heading">
        <p class="eyebrow">Product loop</p>
        <h2>One state from source material to verified asset.</h2>
        <p>The current repository implements this loop through machine-readable contracts. The next product
          step is to make the same loop configurable for an external team.</p>
      </div>
      <div class="workflow">{workflow_html}</div>
    </div>
  </section>

  <section class="band band--muted" id="reference">
    <div class="shell">
      <div class="section-heading">
        <p class="eyebrow">Reference deployment</p>
        <h2>A difficult research boundary, represented honestly.</h2>
        <p>secp256k1 is the test case, not the product claim. It forces KeyAI to distinguish a theorem,
          an experiment, a threat model, a failed route, and a practical attack.</p>
      </div>
      <div class="reference-grid">
        <article class="surface decision-summary">
          <div class="surface__head">
            <div><h3>Current route decision</h3><p>{esc(selection["decision_id"])} · {esc(selection["performed_on"])}</p></div>
            {status_badge("amber", "Monitoring")}
          </div>
          <div class="surface__body">
            <div class="decision-summary__code">SELECT_NONE</div>
            <h3>No current route clears the proposal gate.</h3>
            <p>{esc(selection["gate_result"])}</p>
            <ul>{rationale_html}</ul>
            <p><a href="explore.html">Inspect all {len(routes)} route dispositions</a></p>
          </div>
        </article>
        <aside class="surface">
          <div class="surface__head"><div><h3>Trust snapshot</h3><p>Current generated repository state</p></div></div>
          <div class="surface__body trust-list">
            <div class="trust-row"><div><strong>Lean ledger</strong><span>{stats["ledger_rows"]} rows / ~{stats["distinct_results"]} distinct</span></div>{status_badge("closed", "Checked")}</div>
            <div class="trust-row"><div><strong>Built proof surface</strong><span>{stats["proved_modules"]} proved modules</span></div>{status_badge("closed", "0 sorry")}</div>
            <div class="trust-row"><div><strong>Formal release map</strong><span>{proof_closed} of {len(formal["critical_nodes"])} critical nodes closed</span></div>{status_badge("blue", "Mapped")}</div>
            <div class="trust-row"><div><strong>Corpus frontier</strong><span>{frontier["meta"]["corpus_claims"]} claims classified</span></div>{status_badge("blue", f'{frontier["meta"]["frontier_completeness_pct"]}%')}</div>
          </div>
        </aside>
      </div>
    </div>
  </section>

  <section class="band band--white">
    <div class="shell">
      <div class="section-heading">
        <p class="eyebrow">What exists now</p>
        <h2>Evidence, not a product demo made of placeholders.</h2>
        <p>Each capability below links to a live artifact in the reference repository.</p>
      </div>
      <div class="evidence-grid">{capabilities_html}</div>
    </div>
  </section>

  <section class="band">
    <div class="shell boundary-columns">
      <div class="boundary-column">
        <p class="eyebrow">Current capability</p>
        <h3>Reference system</h3>
        <ul class="check-list">{current_html}</ul>
      </div>
      <div class="boundary-column">
        <p class="eyebrow">Not yet</p>
        <h3>Hosted product</h3>
        <ul class="check-list check-list--not">{not_yet_html}</ul>
      </div>
    </div>
  </section>

  <section class="band mvp-band" id="mvp">
    <div class="shell">
      <div class="section-heading">
        <p class="eyebrow">The next product milestone</p>
        <h2>We will call it an MVP when another team can run the loop.</h2>
        <p>{esc(mvp["definition"])} This is also the evidence threshold before a credible accelerator application.</p>
      </div>
      <div class="metric-lines">{metric_html}</div>
    </div>
  </section>
</main>
{site_footer(product)}"""


def route_distribution(routes: list[dict]) -> tuple[str, str]:
    counts = Counter(route["status"] for route in routes)
    total = len(routes) or 1
    segments = []
    legend = []
    for status in ROUTE_STATUS_ORDER:
        count = counts.get(status, 0)
        if not count:
            continue
        label, css_status = ROUTE_STATUS[status]
        width = count / total * 100
        segments.append(
            f'<span class="distribution__segment segment--{esc(css_status)}" '
            f'style="width:{width:.3f}%" title="{esc(label)}: {count}"></span>'
        )
        legend.append(
            f'<span class="legend-item"><i class="segment--{esc(css_status)}"></i>'
            f'{esc(label)} <strong>{count}</strong></span>'
        )
    return "".join(segments), "".join(legend)


def build_dashboard(
    product: dict,
    stats: dict,
    frontier: dict,
    decisions: dict,
    formal: dict,
    graph: dict,
    tasks: list[dict[str, str]],
) -> str:
    selection = decisions["route_selection"]
    routes = decisions["routes"]
    distribution_html, legend_html = route_distribution(routes)
    task_rows = [
        (
            task,
            f"""<article class="task-row">
  <div class="task-row__top"><div><h4>{esc(task["id"])} · {esc(task["title"])}</h4>
    <p>{esc(task["why"])}</p></div>{task_status_badge(task["status"])}</div>
</article>""",
        )
        for task in tasks
    ]
    task_html = "".join(row for _task, row in task_rows)
    active_task_html = "".join(
        row for task, row in task_rows if task["status"] == "active"
    ) or '<p class="empty-state">No task contract is currently active.</p>'
    route_rows = "".join(
        f"""<tr>
  <td><strong>{esc(route["title"])}</strong><small>{esc(route["id"])}</small></td>
  <td>{status_badge(route["status"])}</td>
  <td>{esc(", ".join(route.get("threat_models", [])))}</td>
  <td>{esc(route.get("priority", "unassigned"))}</td>
  <td>{esc(route.get("next_action", ""))}</td>
</tr>"""
        for route in routes
    )
    formal_rows = "".join(
        f"""<tr>
  <td><strong>{esc(node["title"])}</strong><small>{esc(node["id"])}</small></td>
  <td>{status_badge(node["status"])}</td>
  <td>{esc(", ".join(node.get("depends_on", [])) or "none")}</td>
  <td>{esc(", ".join(node.get("blocker_ids", [])) or "none")}</td>
  <td>{evidence_links(node.get("evidence_files", []), limit=2)}</td>
</tr>"""
        for node in formal["critical_nodes"]
    )
    blocker_rows = "".join(
        f"""<tr>
  <td><strong>{esc(blocker["title"])}</strong><small>{esc(blocker["kind"])}</small></td>
  <td>{esc(blocker["description"])}</td>
  <td>{esc(blocker["resume_condition"])}</td>
</tr>"""
        for blocker in formal["blockers"]
    )
    decision_reasons = "".join(f"<li>{esc(item)}</li>" for item in selection["rationale"])
    triggers = "".join(f"<li>{esc(item)}</li>" for item in selection["reconsideration_triggers"])
    phase_policy = decisions["phase_policy"]
    graph_counts = graph["counts"]
    active_count = sum(task["status"] == "active" for task in tasks)
    closed_count = sum(node["status"] == "closed" for node in formal["critical_nodes"])

    health_cards = [
        (
            "Canonical counts",
            f'{stats["ledger_rows"]} ledger rows / ~{stats["distinct_results"]} distinct',
            ["data/stats.json", "scripts/check_status_consistency.py"],
            "closed",
        ),
        (
            "Decision state",
            f'{len(routes)} routes evaluated / {len(selection["selected_route_ids"])} selected',
            ["repo/ECDLP_DECISION_SUBSTRATE.json", "scripts/check_ecdlp_decision_substrate.py"],
            "closed",
        ),
        (
            "Generated closure",
            f'{graph_counts["theorems"]} theorem nodes in the knowledge graph',
            ["repo/ARTIFACTS.yaml", "scripts/check_repo_artifacts.py"],
            "closed",
        ),
        (
            "Product boundary",
            product["current_stage"]["label"],
            ["repo/PRODUCT_MODEL.json", "scripts/check_product_model.py"],
            "blue",
        ),
    ]
    health_html = "".join(
        f"""<article class="surface">
  <div class="surface__head"><div><h3>{esc(label)}</h3><p>{esc(value)}</p></div>{status_badge(status, "OK")}</div>
  <div class="surface__body">{evidence_links(paths)}</div>
</article>"""
        for label, value, paths, status in health_cards
    )
    description = (
        "The live KeyAI operator workspace for the secp256k1 ECDLP reference environment: "
        "decision routes, formal state, evidence, tasks, and trust boundaries."
    )
    return f"""{page_head("KeyAI Workspace | secp256k1 reference environment", description)}
<body data-page="workspace">
{site_header()}
<main id="main">
  <section class="workspace-mast">
    <div class="shell">
      <p class="breadcrumb">Reference workspace / secp256k1 ECDLP</p>
      <div class="workspace-title">
        <div><h1>secp256k1 research state</h1>
          <p>One operator view for the current decision, formal substrate, evidence, active work,
            and generated trust checks.</p></div>
        <div class="snapshot">Canonical snapshot
          <code>snapshot {stats["ledger_rows"]} ledger rows / ~{stats["distinct_results"]} distinct</code></div>
      </div>
      <div class="boundary-notice"><strong>Scope boundary.</strong>
        {esc(product["reference_environment"]["boundary"])}
        Monitoring means new evidence can reopen a route; it does not mean impossibility was proved.</div>
      <div class="workspace-metrics">
        <div class="workspace-metric"><div class="workspace-metric__value">{stats["ledger_rows"]}</div><div class="workspace-metric__label">ledger rows</div></div>
        <div class="workspace-metric"><div class="workspace-metric__value">~{stats["distinct_results"]}</div><div class="workspace-metric__label">distinct results</div></div>
        <div class="workspace-metric"><div class="workspace-metric__value">{stats["proved_modules"]}</div><div class="workspace-metric__label">proved modules</div></div>
        <div class="workspace-metric"><div class="workspace-metric__value">{frontier["meta"]["corpus_claims"]}</div><div class="workspace-metric__label">corpus claims</div></div>
        <div class="workspace-metric"><div class="workspace-metric__value">{len(routes)}</div><div class="workspace-metric__label">routes evaluated</div></div>
        <div class="workspace-metric"><div class="workspace-metric__value">{len(selection["selected_route_ids"])}</div><div class="workspace-metric__label">routes selected</div></div>
      </div>
    </div>
  </section>

  <div class="tabbar-wrap">
    <div class="shell tabbar" role="tablist" aria-label="Workspace views" data-tabs>
      <button type="button" role="tab" id="tab-overview" aria-controls="panel-overview" aria-selected="true" data-tab="overview">Overview</button>
      <button type="button" role="tab" id="tab-routes" aria-controls="panel-routes" aria-selected="false" tabindex="-1" data-tab="routes">Routes</button>
      <button type="button" role="tab" id="tab-formal" aria-controls="panel-formal" aria-selected="false" tabindex="-1" data-tab="formal">Formal substrate</button>
      <button type="button" role="tab" id="tab-evidence" aria-controls="panel-evidence" aria-selected="false" tabindex="-1" data-tab="evidence">Evidence</button>
      <button type="button" role="tab" id="tab-activity" aria-controls="panel-activity" aria-selected="false" tabindex="-1" data-tab="activity">Queue</button>
    </div>
  </div>

  <div class="shell workspace-body">
    <section class="tab-panel" role="tabpanel" id="panel-overview" aria-labelledby="tab-overview" data-tab-panel="overview">
      <div class="panel-heading"><div><h2>Current operating state</h2>
        <p>The decision layer controls what work is justified; proof volume does not select an attack route.</p></div>
        {status_badge("blue", product["current_stage"]["label"])}</div>
      <article class="decision-band">
        <div class="decision-band__state"><span>{esc(selection["decision_id"])}</span><strong>Select none</strong></div>
        <div class="decision-band__copy"><h3>No experiment is currently authorized.</h3>
          <p>{esc(selection["gate_result"])}</p></div>
      </article>
      <div class="layout-two">
        <article class="surface">
          <div class="surface__head"><div><h3>Why this decision</h3><p>Canonical rationale, not a claim of impossibility</p></div></div>
          <div class="surface__body"><ul class="plain-list">{decision_reasons}</ul></div>
        </article>
        <aside class="surface">
          <div class="surface__head"><div><h3>Active queue</h3><p>{active_count} active of {len(tasks)} task contracts</p></div>
            <a href="{REPO}/blob/main/tasks/NEXT.md">Open source</a></div>
          <div class="surface__body">{active_task_html}</div>
        </aside>
      </div>
    </section>

    <section class="tab-panel" role="tabpanel" id="panel-routes" aria-labelledby="tab-routes" data-tab-panel="routes" hidden>
      <div class="panel-heading"><div><h2>Route portfolio</h2>
        <p>All routes are bound to an exact threat model, evidence gate, stop condition, and next action.</p></div>
        <a class="button" href="explore.html">Open detailed route map</a></div>
      <div class="surface" style="margin-bottom:22px">
        <div class="surface__head"><div><h3>Disposition distribution</h3><p>{len(routes)} canonical routes</p></div></div>
        <div class="surface__body"><div class="distribution">{distribution_html}</div><div class="legend-list">{legend_html}</div></div>
      </div>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>Route</th><th>Disposition</th><th>Threat model</th><th>Priority</th><th>Next action</th></tr></thead>
        <tbody>{route_rows}</tbody>
      </table></div>
    </section>

    <section class="tab-panel" role="tabpanel" id="panel-formal" aria-labelledby="tab-formal" data-tab-panel="formal" hidden>
      <div class="panel-heading"><div><h2>Formal substrate</h2>
        <p>{closed_count} of {len(formal["critical_nodes"])} critical nodes are closed. Blocked nodes retain exact resume conditions.</p></div>
        <a class="button" href="{REPO}/blob/main/repo/FORMAL_SUBSTRATE.json">Open canonical map</a></div>
      <div class="table-wrap" style="margin-bottom:28px"><table class="data-table">
        <thead><tr><th>Critical node</th><th>Status</th><th>Depends on</th><th>Blocker</th><th>Evidence</th></tr></thead>
        <tbody>{formal_rows}</tbody>
      </table></div>
      <div class="panel-heading"><div><h2>Accepted blockers</h2>
        <p>Missing foundations are recorded, but do not authorize work without a selected route.</p></div></div>
      <div class="table-wrap"><table class="data-table">
        <thead><tr><th>Blocker</th><th>What is missing</th><th>Resume condition</th></tr></thead>
        <tbody>{blocker_rows}</tbody>
      </table></div>
    </section>

    <section class="tab-panel" role="tabpanel" id="panel-evidence" aria-labelledby="tab-evidence" data-tab-panel="evidence" hidden>
      <div class="panel-heading"><div><h2>Sync Health</h2>
        <p>The public and agent-facing views resolve back to canonical machine sources and their gates.</p></div></div>
      <div class="layout-two" style="margin-bottom:30px">{health_html}</div>
      <div class="layout-two">
        <article class="surface">
          <div class="surface__head"><div><h3>Reconsideration triggers</h3><p>What can legitimately reopen route selection</p></div></div>
          <div class="surface__body"><ul class="plain-list">{triggers}</ul></div>
        </article>
        <article class="surface">
          <div class="surface__head"><div><h3>Operating policy</h3><p>{esc(phase_policy["phase"])}</p></div></div>
          <div class="surface__body">
            <ul class="compact-list">
              <li><strong>Experiments authorized</strong><span>{str(phase_policy["experiments_authorized"]).lower()}</span></li>
              <li><strong>Selected route</strong><span>{esc(phase_policy["selected_attack_route"] or "none")}</span></li>
              <li><strong>Merge rule</strong><span>{esc(phase_policy["merge_rule"])}</span></li>
              <li><strong>Product claim policy</strong>{evidence_links(["repo/PRODUCT_MODEL.json", "scripts/check_product_model.py"])}</li>
            </ul>
          </div>
        </article>
      </div>
    </section>

    <section class="tab-panel" role="tabpanel" id="panel-activity" aria-labelledby="tab-activity" data-tab-panel="activity" hidden>
      <div class="panel-heading"><div><h2>Work queue</h2>
        <p>Every active, blocked, or parked item is generated from a bounded task contract with an exit condition.</p></div>
        <a class="button" href="{REPO}/blob/main/tasks/NEXT.md">Open canonical queue</a></div>
      <div class="surface"><div class="surface__body">{task_html}</div></div>
    </section>
  </div>
</main>
{site_footer(product)}"""


def build_explore(product: dict, stats: dict, decisions: dict) -> str:
    routes = decisions["routes"]
    selection = decisions["route_selection"]
    counts = Counter(route["status"] for route in routes)
    filter_buttons = [
        f'<li><button class="filter-button" type="button" aria-pressed="true" data-route-filter="all">'
        f'<span>All routes</span><span>{len(routes)}</span></button></li>'
    ]
    for status in ROUTE_STATUS_ORDER:
        count = counts.get(status, 0)
        if not count:
            continue
        label, _css_status = ROUTE_STATUS[status]
        filter_buttons.append(
            f'<li><button class="filter-button" type="button" aria-pressed="false" '
            f'data-route-filter="{esc(status)}"><span>{esc(label)}</span><span>{count}</span></button></li>'
        )

    route_cards = []
    for route in routes:
        searchable = " ".join(
            [
                route["id"],
                route["title"],
                route["status"],
                " ".join(route.get("threat_models", [])),
                route.get("applicability", ""),
                route.get("current_evidence", ""),
                route.get("next_action", ""),
            ]
        )
        evidence = route.get("evidence_files", [])
        assumptions = route.get("assumptions", [])
        assumptions_text = "; ".join(assumptions) if assumptions else "No extra assumptions recorded."
        route_cards.append(
            f"""<details class="route-card" data-route-status="{esc(route["status"])}"
  data-route-searchable="{esc(searchable)}">
  <summary>
    <div class="route-title"><strong>{esc(route["title"])}</strong><code>{esc(route["id"])}</code></div>
    <div>{status_badge(route["status"])}</div>
    <div class="route-meta"><strong>{esc(route.get("priority", "unassigned"))}</strong>
      {esc(", ".join(route.get("threat_models", [])))}</div>
  </summary>
  <div class="route-card__body">
    <section class="route-detail"><h3>Applicability</h3><p>{esc(route.get("applicability", ""))}</p></section>
    <section class="route-detail"><h3>Known cost</h3><p>{esc(route.get("known_cost", ""))}</p></section>
    <section class="route-detail"><h3>Current evidence</h3><p>{esc(route.get("current_evidence", ""))}</p></section>
    <section class="route-detail"><h3>Assumptions</h3><p>{esc(assumptions_text)}</p></section>
    <section class="route-detail"><h3>Success gate</h3><p>{esc(route.get("success_gate", ""))}</p></section>
    <section class="route-detail"><h3>Stop condition</h3><p>{esc(route.get("stop_condition", ""))}</p></section>
    <section class="route-detail route-detail--wide"><h3>Next action</h3><p>{esc(route.get("next_action", ""))}</p></section>
    <section class="route-detail route-detail--wide"><h3>Evidence files</h3>{evidence_links(evidence)}</section>
  </div>
</details>"""
        )
    description = (
        "A canonical, searchable map of all ECDLP routes evaluated for the plain single-target "
        "secp256k1 objective, including scope, evidence, gates, and stop conditions."
    )
    return f"""{page_head("KeyAI Route Map | secp256k1 ECDLP", description)}
<body data-page="routes">
{site_header()}
<main id="main">
  <section class="explorer-mast">
    <div class="shell explorer-mast__title">
      <div><p class="eyebrow">Canonical decision explorer</p>
        <h1>secp256k1 ECDLP route map</h1>
        <p>Every route is generated from <code>repo/ECDLP_DECISION_SUBSTRATE.json</code>.
          Search by mechanism, scope, evidence, or next action.</p></div>
      <aside class="decision-inline"><strong>{esc(selection["decision_id"])} · Select none</strong>
        <span>{esc(selection["gate_result"])}</span></aside>
    </div>
  </section>

  <div class="shell explorer-layout">
    <aside class="explorer-sidebar">
      <h2>Disposition</h2>
      <ul class="filter-list">{"".join(filter_buttons)}</ul>
      <label for="route-search"><h2>Search</h2></label>
      <input class="route-search" id="route-search" type="search" placeholder="GLV, leakage, pairing..."
        autocomplete="off" data-route-search>
      <p style="margin-top:18px"><span data-metric="ledger-rows">{stats["ledger_rows"]}</span> verified ledger rows support the surrounding
        substrate. A formal result is not automatically an attack route.</p>
    </aside>

    <section class="explorer-results" aria-labelledby="route-results-title">
      <div class="explorer-results__head"><h2 id="route-results-title">Evaluated routes</h2>
        <span class="result-count" data-route-count>{len(routes)} routes</span></div>
      <div class="route-list" data-route-list>{"".join(route_cards)}</div>
      <div class="empty-state" hidden data-route-empty>No route matches this filter.</div>
    </section>
  </div>
</main>
{site_footer(product)}"""


def main() -> int:
    product = load_json(PRODUCT_PATH)
    stats = load_json(STATS_PATH)
    frontier = load_json(FRONTIER_PATH)
    decisions = load_json(DECISION_PATH)
    formal = load_json(FORMAL_PATH)
    graph = load_json(GRAPH_PATH)
    tasks = parse_tasks()

    index = build_index(product, stats, frontier, decisions, formal)
    dashboard = build_dashboard(product, stats, frontier, decisions, formal, graph, tasks)
    explore = build_explore(product, stats, decisions)
    write_text(INDEX_PATH, index)
    write_text(DASHBOARD_PATH, dashboard)
    write_text(EXPLORE_PATH, explore)

    print(
        "wrote KeyAI public site: "
        f"{stats['ledger_rows']} ledger rows, "
        f"{len(decisions['routes'])} decision routes, "
        f"{len(formal['critical_nodes'])} formal nodes, "
        f"{len(tasks)} task contracts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
