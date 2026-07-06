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

# Per-1M-token USD (input, output). Anthropic from agent_day PRICES; DeepSeek chat ~ published rates.
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
_spend = {"deepseek": 0.0, "opus_rigour": 0.0, "opus_gate": 0.0}


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
    pin, pout = PRICES.get(model, PRICES["claude-opus-4-8"])
    inp = _tok(usage, "input_tokens", "prompt_tokens")           # anthropic / openai shapes
    out = _tok(usage, "output_tokens", "completion_tokens")
    return (inp * pin + out * pout) / 1_000_000


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
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL, messages=[{"role": "user", "content": prompt}],
            temperature=1.1, max_tokens=1200, response_format={"type": "json_object"},
        )
        _add_spend("deepseek", _usd(DEEPSEEK_MODEL, resp.usage))
        return resp.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        print(f"::warning:: DeepSeek failed: {e}", file=sys.stderr)
        return None


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


# ---------------------------------------------------------------- Tier 2: Opus rigour
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
    reply = opus(client, RIGOUR_SYS, rigour_prompt(idea), "opus_rigour")
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
        v = parse_json(opus(client, GATE_SYS, gate_prompt(c), "opus_gate", max_tokens=1500)) or {}
        votes.append(bool(v.get("faithful") and v.get("nontrivial") and v.get("relevant")))
    passed = sum(votes)
    return {**c, "_gate_votes": f"{passed}/{panel}", "_is_lead": passed == panel and panel > 0}


# ---------------------------------------------------------------- orchestration
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--breadth", type=int, default=20, help="DeepSeek breadth agents")
    ap.add_argument("--workers", type=int, default=8, help="max concurrent API calls per tier")
    ap.add_argument("--gate-panel", type=int, default=2, help="independent Opus verifiers per survivor")
    ap.add_argument("--budget-usd", type=float, default=float(os.environ.get("EXPLORE_BUDGET_USD", "4")))
    args = ap.parse_args()

    if not os.environ.get("DEEPSEEK_API_KEY") or not os.environ.get("ANTHROPIC_API_KEY"):
        print("DEEPSEEK_API_KEY and/or ANTHROPIC_API_KEY absent — pipeline no-ops (no spend).")
        return 0
    client = _anthropic()
    if client is None:
        print("anthropic SDK unavailable — no-op.")
        return 0

    seen = load_seen()
    # Tier 1
    ideas = run_breadth(args.breadth, args.workers, seen)
    print(f"tier1 breadth: {len(ideas)} novel ideas from {args.breadth} DeepSeek agents "
          f"(~${_spend['deepseek']:.3f})")
    if not ideas:
        print("no novel ideas this run.")
        return 0

    # Tier 2 + 3 (rigour then verify), budget-bounded
    processed = []
    with ThreadPoolExecutor(max_workers=min(args.workers, 4)) as ex:
        futs = [ex.submit(rigour_and_verify, client, idea) for idea in ideas]
        for fut in as_completed(futs):
            processed.append(fut.result())
            if _spend["opus_rigour"] + _spend["opus_gate"] >= args.budget_usd:
                print(f"::warning:: budget ${args.budget_usd} reached in rigour tier; stopping early")
                break
    supported = [c for c in processed if c["_outcome"] == "supported"]
    print(f"tier2/3 rigour+verify: {len(supported)} supported, "
          f"{sum(c['_outcome']=='refuted' for c in processed)} refuted, "
          f"{sum(c['_outcome']=='parked' for c in processed)} parked (~${_spend['opus_rigour']:.3f})")

    # Tier 4 gate panel on supported
    leads = []
    for c in supported:
        if _spend["opus_rigour"] + _spend["opus_gate"] >= args.budget_usd:
            print(f"::warning:: budget reached before gating all survivors")
            break
        g = run_gate(client, c, args.gate_panel)
        c["_gate_votes"], c["_is_lead"] = g["_gate_votes"], g["_is_lead"]
        if c["_is_lead"]:
            leads.append(c)
    rejected = [c for c in supported if not c.get("_is_lead")]
    print(f"tier4 gate: {len(leads)} real leads, {len(rejected)} rejected by cross-check "
          f"(~${_spend['opus_gate']:.3f})")
    print(f"TOTAL spend ~${sum(_spend.values()):.3f} "
          f"(deepseek ${_spend['deepseek']:.3f} / opus ${_spend['opus_rigour']+_spend['opus_gate']:.3f})")

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
