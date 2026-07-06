#!/usr/bin/env python3
"""Three-tier ECDLP hypothesis pipeline (the honest division of labour).

  Tier 1  BREADTH   — DeepSeek, N axis-scoped agents. Each returns ONE novel research angle plus the
                      KIND of small checkable consequence it would have. NO script (DeepSeek is weak at
                      rigour; keep it off the critical path). Cheap, diverse, deduped by signature.
  Tier 2  RIGOUR    — Opus. Turns each unique idea into a PRECISE small sub-claim AND a faithful,
                      self-contained sympy script that tests exactly that sub-claim.
  Tier 3  VERIFY    — sympy, offline. supported / refuted / parked (a crash is `parked`, NOT a
                      mathematical refutation — a broken script never pollutes the no-go map).
  Tier 4  GATE      — Opus cross-check panel. K independent skeptics per survivor judge (a) does the
                      script actually test the stated sub-claim, (b) is it non-trivial / not
                      already-known, (c) does it bear on the hypothesis. UNANIMOUS pass ⇒ a real lead.

Only leads that clear Tier 4 are handed to the Fable depth tier; everything else grows the honest
ledger (refuted = real no-go; parked = broken/uncertain; rejected = failed the gate). Costs are
tracked per tier so we can measure whether the cheap breadth tier earns its place.

Runs where the keys live (GitHub Actions): needs DEEPSEEK_API_KEY and ANTHROPIC_API_KEY. Safe no-op
(zero spend) if either is absent.

Usage:
    python3 scripts/explore_pipeline.py --breadth 20 --gate-panel 2 --budget-usd 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "notes" / "HYPOTHESIS_LEDGER.md"
LEADS = ROOT / "notes" / "HYPOTHESIS_LEADS.md"
CERT_MARKER = "CERT_OK"
SYMPY_TIMEOUT_S = int(os.environ.get("CERTIFY_TIMEOUT_S", "60"))
OPUS_MODEL = os.environ.get("EXPLORE_OPUS_MODEL", "claude-opus-4-8")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# Per-tier model routing — any tier can use a different provider/model to control cost. The rigour
# tier (write a sympy script) is backstopped by sympy AND the gate, so a cheap model is fine there;
# the GATE (faithfulness judge) is the quality guarantee, so it defaults to the strongest reasoner.
# Providers: "deepseek" / "featherless" (both OpenAI-compatible) or "anthropic".
RIGOUR_PROVIDER = os.environ.get("EXPLORE_RIGOUR_PROVIDER", "featherless")
RIGOUR_MODEL = os.environ.get("EXPLORE_RIGOUR_MODEL", "deepseek-ai/DeepSeek-R1")
GATE_PROVIDER = os.environ.get("EXPLORE_GATE_PROVIDER", "anthropic")
GATE_MODEL = os.environ.get("EXPLORE_GATE_MODEL", OPUS_MODEL)

# OpenAI-compatible providers: (base_url, api-key env var).
PROVIDERS = {
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    "featherless": ("https://api.featherless.ai/v1", "FEATHERLESS_API_KEY"),
}

# Per-1M-token USD (input, output). Anthropic + DeepSeek published rates; Featherless is a flat-rate
# subscription, so marginal per-token cost within the plan is ~0 (logged as 0). Unknown models → 0.
PRICES = {
    "claude-opus-4-8": (5.0, 25.0), "claude-sonnet-5": (3.0, 15.0), "claude-haiku-4-5": (1.0, 5.0),
    "deepseek-chat": (0.28, 0.42), "deepseek-reasoner": (0.55, 2.19),
}

AXES = [
    "algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n])",
    "index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases)",
    "analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions)",
    "geometric (higher genus, abelian varieties, moduli, covers)",
    "cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory)",
    "reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants)",
]

KNOWN_NOGO = """\
- secp256k1 resists MOV/Frey-Ruck (embedding degree > 100). PROVEN here.
- Not anomalous / not supersingular (trace of Frobenius t != 0, 1). PROVEN here.
- Semaev polynomials give NO subexponential edge over a PRIME field. Documented.
- Generic (black-box) attacks are Omega(sqrt n). PROVEN here.
- Distinct-prime torsion x-loci are disjoint: gcd(psi_l, psi_l')=1 (E[2]-E[3], E[5]-E[7] certified).
- Standard dead ends (do NOT restate): plain index calculus on prime-field EC, generic Weil descent,
  isogeny-to-weak-curve search, generic Groebner on the point equations."""

_spend_lock = threading.Lock()
_spend = {"deepseek": 0.0, "rigour": 0.0, "gate": 0.0}


def _add_spend(bucket: str, usd: float) -> None:
    with _spend_lock:
        _spend[bucket] += usd


def _tok(usage, *names) -> int:
    for n in names:
        v = getattr(usage, n, None)
        if v:
            return int(v)
    return 0


def _usd(model: str, usage) -> float:
    pin, pout = PRICES.get(model, (0.0, 0.0))                     # unknown/Featherless flat-rate → 0
    inp = _tok(usage, "input_tokens", "prompt_tokens")           # anthropic / openai shapes
    out = _tok(usage, "output_tokens", "completion_tokens")
    return (inp * pin + out * pout) / 1_000_000


def oai_call(provider: str, model: str, system: str, user: str, bucket: str,
             json_mode: bool = True, max_tokens: int = 4000, temperature: float = 0.7) -> str | None:
    """Call any OpenAI-compatible provider (DeepSeek / Featherless). Returns content or None."""
    base, keyenv = PROVIDERS[provider]
    key = os.environ.get(keyenv)
    if not key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None
    client = OpenAI(api_key=key, base_url=base)
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    kw = dict(model=model, messages=msgs, temperature=temperature, max_tokens=max_tokens)
    for attempt in ((json_mode, kw), (False, kw)):   # some open models reject json_mode; retry without
        use_json, base_kw = attempt
        k = {**base_kw, **({"response_format": {"type": "json_object"}} if use_json else {})}
        try:
            resp = client.chat.completions.create(**k)
            _add_spend(bucket, _usd(model, resp.usage))
            return resp.choices[0].message.content
        except Exception as e:  # noqa: BLE001
            last = e
    print(f"::warning:: {provider}/{model} failed: {last}", file=sys.stderr)
    return None


def featherless_models_hint() -> None:
    """Print the strong general models actually available on the Featherless plan, so the exact
    model ids are visible in the run log (self-documenting; no guessing which id is valid)."""
    key = os.environ.get("FEATHERLESS_API_KEY")
    if not key:
        return
    try:
        from openai import OpenAI
        ids = [m.id for m in OpenAI(api_key=key, base_url=PROVIDERS["featherless"][0]).models.list().data]
    except Exception as e:  # noqa: BLE001
        print(f"::warning:: could not list Featherless models: {e}", file=sys.stderr)
        return
    # Search the plan for the 2026 frontier families and print the EXACT ids present, so we pick the
    # strongest available id rather than guessing. Families ranked by current coding/reasoning benches.
    fam = re.compile(r"(DeepSeek[-_.]?V4|DeepSeek[-_.]?V3\.?2|GLM-?5|Kimi[-_.]?K2|Qwen3\.5|"
                     r"Qwen3-235B|DeepSeek[-_.]?R1|Kimina|Goedel-?Prover-?V2)", re.I)
    hits = sorted({i for i in ids if fam.search(i)})
    # prefer official-org repos (deepseek-ai/, zai-org/, moonshotai/, Qwen/, AI-MO/, Goedel-LM/)
    official = [i for i in hits if i.split("/")[0] in
                {"deepseek-ai", "zai-org", "THUDM", "moonshotai", "Qwen", "AI-MO", "Goedel-LM"}]
    print(f"Featherless plan: {len(ids)} models. Frontier ids present ({len(hits)}); "
          f"official: {official[:25]}")


def sig(text: str) -> str:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return hashlib.sha1((" ".join(sorted(set(toks)))).encode()).hexdigest()[:12]


def load_seen() -> set[str]:
    if not LEDGER.exists():
        return set()
    return set(re.findall(r"`sig:([0-9a-f]{12})`", LEDGER.read_text(encoding="utf-8")))


def parse_json(raw: str) -> dict | None:
    if not raw:
        return None
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    try:
        return json.loads(s[s.index("{"):s.rindex("}") + 1])
    except Exception:
        return None


# ---------------------------------------------------------------- Tier 1: DeepSeek breadth
def deepseek(prompt: str) -> str | None:
    return oai_call("deepseek", DEEPSEEK_MODEL, "", prompt, "deepseek",
                    json_mode=True, max_tokens=1200, temperature=1.1)


def breadth_prompt(axis: str, n_seen: int) -> str:
    return f"""You are the BREADTH tier of a machine-verified ECDLP research system. Propose ONE genuinely
novel research ANGLE on the structure of the discrete-log problem for secp256k1 (y^2 = x^3 + 7 over
F_p), strictly along the axis: **{axis}**.

Do NOT restate any known / machine-checked fact or standard dead end:
{KNOWN_NOGO}
Be orthogonal to the {n_seen} angles already explored. Do NOT write any code — just the idea and the
KIND of small, exact, sympy-checkable consequence it would have (a polynomial identity, a
resultant/coprimality fact, a torsion/degree count, an explicit map).

Reply as STRICT JSON: {{"hypothesis": "...", "why_novel": "...", "checkable_direction": "..."}}."""


def run_breadth(n_agents: int, workers: int, seen: set[str]) -> list[dict]:
    n_seen = len(seen)
    assignments = [AXES[i % len(AXES)] for i in range(n_agents)]
    out, local_seen = [], set(seen)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(deepseek, breadth_prompt(ax, n_seen)): ax for ax in assignments}
        for fut in as_completed(futs):
            obj = parse_json(fut.result() or "")
            if not obj or not (obj.get("hypothesis") or "").strip():
                continue
            h = obj["hypothesis"].strip()
            s = sig(h)
            if s in local_seen:
                continue
            local_seen.add(s)
            out.append({"hypothesis": h, "why_novel": obj.get("why_novel", ""),
                        "checkable_direction": obj.get("checkable_direction", ""),
                        "_sig": s, "_axis": futs[fut]})
    return out


# ---------------------------------------------------------------- Tier 1.5: DeepSeek peer refine
def refine_prompt(idea: dict) -> str:
    return f"""You are a PEER REVIEWER (a second, independent model) on a machine-verified ECDLP research
system. Here is a colleague's raw research angle (axis: {idea['_axis']}):
  hypothesis: {idea['hypothesis']}
  checkable direction: {idea['checkable_direction']}

Do NOT restate any known / machine-checked fact or standard dead end:
{KNOWN_NOGO}

Your job — add a little reasoning and IMPROVE it, cheaply:
1. If it is a duplicate, already-known, vacuous, or hopeless, set "keep": false.
2. Otherwise, REWRITE it sharper: a clearer hypothesis and a MORE PRECISE, genuinely checkable
   direction (name the exact object to compute — a specific resultant, degree, factorization, map).
   Do NOT write code. Do NOT claim it is proved — only sharpen the ANGLE so the rigour tier can test it.

Reply as STRICT JSON: {{"keep": true/false, "improved_hypothesis": "...", "improved_direction": "...",
"why": "one sentence"}}."""


def refine_one(idea: dict) -> dict | None:
    """A second DeepSeek instance cross-checks and sharpens one idea (cheap 'more reasoning').
    Returns an improved idea, or None if the peer rejects it. Same-model, so this improves the
    IDEA — it is NOT the faithfulness judge (that stays Opus, a stronger reasoner)."""
    obj = parse_json(deepseek(refine_prompt(idea)) or "")
    if not obj or not obj.get("keep", False):
        return None
    h = (obj.get("improved_hypothesis") or idea["hypothesis"]).strip()
    return {**idea, "hypothesis": h, "_sig": sig(h),
            "checkable_direction": (obj.get("improved_direction") or idea["checkable_direction"]).strip(),
            "_refined": True}


def run_refine(ideas: list[dict], workers: int) -> list[dict]:
    kept, seen_sigs = [], set()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(refine_one, ideas):
            if r and r["_sig"] not in seen_sigs:   # peer refinement can collapse near-dupes together
                seen_sigs.add(r["_sig"])
                kept.append(r)
    return kept


# ---------------------------------------------------------------- Anthropic / Opus
def _anthropic():
    try:
        import anthropic
    except Exception:
        return None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    return anthropic.Anthropic()


def opus(client, system: str, user: str, bucket: str, max_tokens: int = 8000) -> str:
    for kwargs in (
        dict(model=OPUS_MODEL, max_tokens=max_tokens, system=system,
             messages=[{"role": "user", "content": user}], thinking={"type": "enabled", "budget_tokens": 6000}),
        dict(model=OPUS_MODEL, max_tokens=max_tokens, system=system,
             messages=[{"role": "user", "content": user}]),
    ):
        try:
            resp = client.messages.create(**kwargs)
            _add_spend(bucket, _usd(OPUS_MODEL, resp.usage))
            return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        except TypeError:
            continue
        except Exception as e:  # noqa: BLE001
            if e.__class__.__name__ in ("BadRequestError", "UnprocessableEntityError"):
                continue
            raise
    return ""


def rigour_llm(client, system: str, user: str) -> str:
    """Rigour tier — Featherless/DeepSeek (cheap; sympy + gate backstop it) or Anthropic."""
    if RIGOUR_PROVIDER == "anthropic":
        return opus(client, system, user, "rigour", max_tokens=8000)
    return oai_call(RIGOUR_PROVIDER, RIGOUR_MODEL, system, user, "rigour",
                    json_mode=True, max_tokens=6000, temperature=0.4) or ""


def gate_llm(client, system: str, user: str) -> str:
    """Gate tier — the faithfulness judge; defaults to the strongest reasoner (Anthropic/Opus)."""
    if GATE_PROVIDER == "anthropic":
        return opus(client, system, user, "gate", max_tokens=1500)
    return oai_call(GATE_PROVIDER, GATE_MODEL, system, user, "gate",
                    json_mode=True, max_tokens=1500, temperature=0.2) or ""


# ---------------------------------------------------------------- Tier 2: rigour
RIGOUR_SYS = ("You are the RIGOUR tier of a machine-verified ECDLP research system. You turn a raw "
              "research angle into a PRECISE, SMALL, exactly-checkable sub-claim and a faithful sympy "
              "script that verifies THAT EXACT sub-claim. secp256k1: y^2 = x^3 + 7 over "
              "F_p, p = 2^256 - 2^32 - 977, group order n known.")


def rigour_prompt(idea: dict) -> str:
    return f"""Research angle (axis: {idea['_axis']}):
  hypothesis: {idea['hypothesis']}
  intended checkable direction: {idea['checkable_direction']}

Produce: (1) a PRECISE small sub-claim (a first, isolable test of the angle — a polynomial identity,
resultant/coprimality fact, torsion/degree count, or explicit map), and (2) a SELF-CONTAINED python+
sympy script that verifies THAT EXACT sub-claim by exact symbolic computation (expand/cancel/
Poly.rem/resultant, GF(p)/Poly(...,modulus=p); NO floats, NO simplify-as-proof) and prints exactly
`{CERT_MARKER}` as the LAST line IFF all assertions pass (else it raises). Only sympy + stdlib; no
files/network; runs in seconds. The script MUST test the stated sub-claim — never substitute an
easier / already-known / unrelated check. If the sub-claim is not actually checkable, REPLACE it with
one that is and that still tests the angle. Reply as STRICT JSON:
{{"subclaim": "...", "sympy_script": "..."}} (return ONLY the JSON)."""


def run_sympy(script: str) -> tuple[str, str]:
    if not (script or "").strip():
        return "parked", "(no script)"
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "cert.py"
        p.write_text(script, encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True,
                               timeout=SYMPY_TIMEOUT_S, cwd=td,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            out = (r.stdout + r.stderr)[-1500:]
        except subprocess.TimeoutExpired:
            return "parked", f"(timeout {SYMPY_TIMEOUT_S}s)"
        except Exception as e:  # noqa: BLE001
            return "parked", f"(failed to run: {e})"
    if CERT_MARKER in out and r.returncode == 0:
        return "supported", out
    if out.strip():
        last = out.rstrip().splitlines()[-1]
        if last.startswith("AssertionError") or last.strip() == "AssertionError":
            return "refuted", out
    if "Traceback" in out or "Error" in out:
        return "parked", "(script error — broken certificate, not a math refutation)\n" + out[-300:]
    return "parked", out


def rigour_and_verify(client, idea: dict) -> dict:
    reply = rigour_llm(client, RIGOUR_SYS, rigour_prompt(idea))
    obj = parse_json(reply) or {}
    subclaim = (obj.get("subclaim") or "").strip()
    script = obj.get("sympy_script") or ""
    if not subclaim or not script.strip():
        return {**idea, "_outcome": "parked", "subclaim": subclaim, "sympy_script": script,
                "_evidence": "(rigour tier produced no checkable sub-claim/script)"}
    outcome, tail = run_sympy(script)
    return {**idea, "subclaim": subclaim, "sympy_script": script,
            "_outcome": outcome, "_evidence": tail[-400:]}


# ---------------------------------------------------------------- Tier 4: Opus gate panel (cross-check)
GATE_SYS = ("You are an adversarial VERIFIER on a machine-checked ECDLP system. Default to rejection. "
            "A candidate 'lead' is only worth the expensive depth tier if its sympy script GENUINELY "
            "tests the stated sub-claim, the sub-claim is NON-TRIVIAL and not already-known, and it "
            "actually bears on the hypothesis. Known/among-trivial facts (do not accept as novel):\n"
            + KNOWN_NOGO)


def gate_prompt(c: dict) -> str:
    return f"""Candidate:
  hypothesis: {c['hypothesis']}
  sub-claim (sympy said CERT_OK): {c['subclaim']}
  sympy script:
```python
{c['sympy_script'][:4000]}
```
Judge strictly. Reply STRICT JSON:
{{"faithful": true/false,   // does the script actually verify THIS sub-claim (not a substituted/trivial check)?
  "nontrivial": true/false, // is the sub-claim non-trivial and NOT already in the known list?
  "relevant": true/false,   // does it genuinely bear on the hypothesis / advance the angle?
  "reason": "one sentence"}}"""


def run_gate(client, c: dict, panel: int) -> dict:
    votes = []
    for _ in range(panel):
        v = parse_json(gate_llm(client, GATE_SYS, gate_prompt(c))) or {}
        votes.append(bool(v.get("faithful") and v.get("nontrivial") and v.get("relevant")))
    passed = sum(votes)
    return {**c, "_gate_votes": f"{passed}/{panel}", "_is_lead": passed == panel and panel > 0}


# ---------------------------------------------------------------- orchestration
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--breadth", type=int, default=20, help="DeepSeek breadth agents")
    ap.add_argument("--workers", type=int, default=8, help="max concurrent API calls per tier")
    ap.add_argument("--gate-panel", type=int, default=2, help="independent Opus verifiers per survivor")
    ap.add_argument("--no-refine", action="store_true", help="skip the DeepSeek peer-refine tier")
    ap.add_argument("--budget-usd", type=float, default=float(os.environ.get("EXPLORE_BUDGET_USD", "4")))
    args = ap.parse_args()

    # Breadth needs DeepSeek; rigour/gate need the key of whichever provider each is routed to.
    need = {"DEEPSEEK_API_KEY"}
    for prov in (RIGOUR_PROVIDER, GATE_PROVIDER):
        need.add("ANTHROPIC_API_KEY" if prov == "anthropic" else PROVIDERS[prov][1])
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        print(f"missing key(s) {missing} — pipeline no-ops (no spend).")
        return 0
    client = _anthropic() if "anthropic" in (RIGOUR_PROVIDER, GATE_PROVIDER) else None
    print(f"routing: breadth=deepseek/{DEEPSEEK_MODEL}  rigour={RIGOUR_PROVIDER}/{RIGOUR_MODEL}  "
          f"gate={GATE_PROVIDER}/{GATE_MODEL}")
    if "featherless" in (RIGOUR_PROVIDER, GATE_PROVIDER):
        featherless_models_hint()

    seen = load_seen()
    # Tier 1 — DeepSeek breadth
    ideas = run_breadth(args.breadth, args.workers, seen)
    print(f"tier1 breadth: {len(ideas)} novel ideas from {args.breadth} DeepSeek agents "
          f"(~${_spend['deepseek']:.3f})")
    if not ideas:
        print("no novel ideas this run.")
        return 0

    # Tier 1.5 — DeepSeek peer cross-check + refine (cheap 'more reasoning'; improves the idea,
    # NOT the faithfulness judge). Raises input quality so the expensive Opus tiers run on fewer,
    # sharper ideas. Disable with --no-refine.
    if not args.no_refine:
        refined = run_refine(ideas, args.workers)
        print(f"tier1.5 DeepSeek peer-refine: {len(refined)}/{len(ideas)} kept + sharpened "
              f"(~${_spend['deepseek']:.3f} total DeepSeek)")
        ideas = refined
        if not ideas:
            print("peer review rejected all ideas this run.")
            return 0

    # Tier 2 + 3 (rigour then verify), budget-bounded
    processed = []
    with ThreadPoolExecutor(max_workers=min(args.workers, 4)) as ex:
        futs = [ex.submit(rigour_and_verify, client, idea) for idea in ideas]
        for fut in as_completed(futs):
            processed.append(fut.result())
            if _spend["rigour"] + _spend["gate"] >= args.budget_usd:
                print(f"::warning:: budget ${args.budget_usd} reached in rigour tier; stopping early")
                break
    supported = [c for c in processed if c["_outcome"] == "supported"]
    print(f"tier2/3 rigour+verify: {len(supported)} supported, "
          f"{sum(c['_outcome']=='refuted' for c in processed)} refuted, "
          f"{sum(c['_outcome']=='parked' for c in processed)} parked (~${_spend['rigour']:.3f})")

    # Tier 4 gate panel on supported
    leads = []
    for c in supported:
        if _spend["rigour"] + _spend["gate"] >= args.budget_usd:
            print(f"::warning:: budget reached before gating all survivors")
            break
        g = run_gate(client, c, args.gate_panel)
        c["_gate_votes"], c["_is_lead"] = g["_gate_votes"], g["_is_lead"]
        if c["_is_lead"]:
            leads.append(c)
    rejected = [c for c in supported if not c.get("_is_lead")]
    print(f"tier4 gate: {len(leads)} real leads, {len(rejected)} rejected by cross-check "
          f"(~${_spend['gate']:.3f})")
    print(f"TOTAL spend ~${sum(_spend.values()):.3f} "
          f"(deepseek ${_spend['deepseek']:.3f} / opus ${_spend['rigour']+_spend['gate']:.3f})")

    _write_ledger(processed, leads)
    return 0


def _write_ledger(processed: list[dict], leads: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    new = not LEDGER.exists() or LEDGER.stat().st_size == 0
    with LEDGER.open("a", encoding="utf-8") as f:
        if new:
            f.write("# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)\n\n")
        for c in processed:
            status = "lead" if c.get("_is_lead") else (
                "rejected-by-gate" if c["_outcome"] == "supported" else c["_outcome"])
            f.write(f"## `sig:{c['_sig']}` — axis: {c['_axis']} — outcome: **{status}**"
                    + (f" (gate {c.get('_gate_votes')})" if c["_outcome"] == "supported" else "") + "\n")
            f.write(f"- **Hypothesis:** {c['hypothesis']}\n")
            f.write(f"- **Sub-claim:** {c.get('subclaim','')}\n")
            if status not in ("lead",):
                f.write(f"- **Evidence:** `{(c.get('_evidence','') or '')[-180:].strip()}`\n")
            f.write("\n")
    if leads:
        LEADS.parent.mkdir(parents=True, exist_ok=True)
        newl = not LEADS.exists() or LEADS.stat().st_size == 0
        with LEADS.open("a", encoding="utf-8") as f:
            if newl:
                f.write("# Live leads — cross-checked sub-claims for the Fable depth tier\n\n"
                        "Each: sympy `CERT_OK` AND unanimous Opus cross-check (faithful + non-trivial "
                        "+ relevant). Fable is spent ONLY on these.\n\n")
            for c in leads:
                f.write(f"## `sig:{c['_sig']}` — axis: {c['_axis']} — gate {c.get('_gate_votes')}\n")
                f.write(f"- **Hypothesis:** {c['hypothesis']}\n")
                f.write(f"- **Sub-claim:** {c['subclaim']}\n")
                f.write("- **Verified certificate (sympy):**\n\n```python\n" + c['sympy_script'].strip() + "\n```\n\n")
    print(f"wrote ledger (+{len(processed)}) " + (f"and {len(leads)} leads" if leads else "(no leads)"))


if __name__ == "__main__":
    raise SystemExit(main())
