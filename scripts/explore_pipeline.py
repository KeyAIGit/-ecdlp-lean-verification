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
FABLE_MODEL = os.environ.get("EXPLORE_FABLE_MODEL", "claude-fable-5")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# Per-tier model routing — any tier is (provider, model). Provider ∈ {"anthropic", "deepseek",
# "featherless"}. Default config is all-Anthropic (Opus + Fable), no DeepSeek: Fable generates the
# ideas and writes the rigour scripts (strong, cheaper/faster than Opus); Opus is the faithfulness
# gate. Override any tier via the EXPLORE_*_PROVIDER / EXPLORE_*_MODEL env vars (or workflow inputs).
BREADTH_PROVIDER = os.environ.get("EXPLORE_BREADTH_PROVIDER", "anthropic")
BREADTH_MODEL = os.environ.get("EXPLORE_BREADTH_MODEL", FABLE_MODEL)
RIGOUR_PROVIDER = os.environ.get("EXPLORE_RIGOUR_PROVIDER", "anthropic")
RIGOUR_MODEL = os.environ.get("EXPLORE_RIGOUR_MODEL", FABLE_MODEL)
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
_spend = {"breadth": 0.0, "deepseek": 0.0, "rigour": 0.0, "gate": 0.0}
# Output-token tally per tier, tracked ALONGSIDE spend so an unpriced model (e.g. a flat-rate
# Featherless model, or an Anthropic id not in PRICES) still shows visible activity — otherwise a
# successful-but-unpriced run reads as "$0.000 / did nothing", which is how run #13 hid a real Fable run.
_toks = {"breadth": 0, "deepseek": 0, "rigour": 0, "gate": 0}


def _add_spend(bucket: str, usd: float) -> None:
    with _spend_lock:
        _spend[bucket] += usd


def _record(bucket: str, model: str, usage) -> None:
    """Record both USD spend and output tokens for a completed call (single source of truth)."""
    with _spend_lock:
        _spend[bucket] += _usd(model, usage)
        _toks[bucket] += _tok(usage, "output_tokens", "completion_tokens")


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
    # Hard per-request timeout (env EXPLORE_LLM_TIMEOUT_S) + a couple retries, so a slow/stuck heavy
    # model can never hang the whole run (a 397B request must return or fail, not stall indefinitely).
    to = float(os.environ.get("EXPLORE_LLM_TIMEOUT_S", "120"))
    client = OpenAI(api_key=key, base_url=base, timeout=to, max_retries=2)
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    kw = dict(model=model, messages=msgs, temperature=temperature, max_tokens=max_tokens)
    for attempt in ((json_mode, kw), (False, kw)):   # some open models reject json_mode; retry without
        use_json, base_kw = attempt
        k = {**base_kw, **({"response_format": {"type": "json_object"}} if use_json else {})}
        try:
            resp = client.chat.completions.create(**k)
            _record(bucket, model, resp.usage)
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


# ---------------------------------------------------------------- Tier 1: breadth (ideas)
def deepseek(prompt: str) -> str | None:  # kept for the optional DeepSeek peer-refine tier
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


def run_breadth(n_agents: int, workers: int, seen: set[str], client=None) -> list[dict]:
    n_seen = len(seen)
    assignments = [AXES[i % len(AXES)] for i in range(n_agents)]
    out, local_seen = [], set(seen)
    # Anthropic (Fable) has a low concurrency ceiling vs DeepSeek; cap breadth workers when on Anthropic.
    w = min(workers, 4) if BREADTH_PROVIDER == "anthropic" else workers

    def _one(axis: str) -> str:
        return llm(BREADTH_PROVIDER, BREADTH_MODEL, "", breadth_prompt(axis, n_seen), "breadth",
                   client=client, json_mode=True, max_tokens=2200, temperature=1.0)

    # Funnel counters so a silent 0-idea run tells us WHERE it collapsed (API → parse → dedup), instead
    # of the opaque "0 novel ideas" that hid run #13. Emitted to stderr, visible in the Actions log.
    raw_nonempty = parsed_ok = dup = 0
    with ThreadPoolExecutor(max_workers=max(1, w)) as ex:
        futs = {ex.submit(_one, ax): ax for ax in assignments}
        for fut in as_completed(futs):
            txt = fut.result() or ""
            if txt.strip():
                raw_nonempty += 1
            obj = parse_json(txt)
            if not obj or not (obj.get("hypothesis") or "").strip():
                if txt.strip():   # got text but couldn't extract a hypothesis → show why
                    print(f"::warning:: breadth[{futs[fut][:16]}] unparseable ({len(txt)} chars): "
                          f"{txt.strip()[:180]!r}", file=sys.stderr)
                continue
            parsed_ok += 1
            h = obj["hypothesis"].strip()
            s = sig(h)
            if s in local_seen:
                dup += 1
                continue
            local_seen.add(s)
            out.append({"hypothesis": h, "why_novel": obj.get("why_novel", ""),
                        "checkable_direction": obj.get("checkable_direction", ""),
                        "_sig": s, "_axis": futs[fut]})
    print(f"breadth funnel: {raw_nonempty}/{n_agents} non-empty · {parsed_ok} parsed · "
          f"{dup} dup · {len(out)} novel", file=sys.stderr)
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


# If a configured model id isn't available on the account (e.g. Fable not enabled for this API key),
# fall back to a model that is — logged loudly, and cached so we don't re-probe the dead id every call.
FALLBACK_MODELS = ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5"]
_resolved: dict[str, str] = {}
_resolve_lock = threading.Lock()


def _anthropic_one(client, model: str, system: str, user: str, max_tokens: int):
    """Try ONE model with graceful param-degradation. Returns resp, or None if the MODEL itself is
    rejected (model-not-found), or re-raises a genuine transport error."""
    # Anthropic requires max_tokens > thinking.budget_tokens. Size the budget to the request so a short
    # call (breadth, max_tokens≈2200) simply runs plain instead of eating a guaranteed-rejected round-trip.
    plain = dict(model=model, max_tokens=max_tokens, system=system,
                 messages=[{"role": "user", "content": user}])
    think_budget = max_tokens - 1024
    variants = []
    if think_budget >= 1024:
        variants.append({**plain, "thinking": {"type": "enabled", "budget_tokens": think_budget}})
    variants.append(plain)
    for i, kwargs in enumerate(variants):
        try:
            return client.messages.create(**kwargs)
        except TypeError:
            continue  # SDK doesn't accept a newer param → try the plainer variant
        except Exception as e:  # noqa: BLE001
            n = e.__class__.__name__
            if n in ("BadRequestError", "UnprocessableEntityError", "NotFoundError"):
                if i < len(variants) - 1:
                    continue  # could be the `thinking` param → try the plain variant of THIS model
                print(f"::warning:: anthropic model '{model}' rejected: {e}", file=sys.stderr)
                return None   # plain variant also rejected → the model id itself is unavailable
            raise
    return None


def claude(client, model: str, system: str, user: str, bucket: str, max_tokens: int = 8000) -> str:
    """One Anthropic call with model fallback (Fable→Sonnet→Opus→Haiku) if the id is unavailable."""
    with _resolve_lock:
        eff = _resolved.get(model, model)
    for cand in [eff] + [m for m in FALLBACK_MODELS if m != eff]:
        resp = _anthropic_one(client, cand, system, user, max_tokens)
        if resp is not None:
            if cand != model:
                print(f"::warning:: using '{cand}' in place of unavailable '{model}'", file=sys.stderr)
            with _resolve_lock:
                _resolved[model] = cand   # cache the working substitute
            _record(bucket, cand, resp.usage)
            return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    print(f"::warning:: no anthropic model available for '{model}' (tried fallbacks)", file=sys.stderr)
    return ""


def llm(provider: str, model: str, system: str, user: str, bucket: str, client=None,
        json_mode: bool = True, max_tokens: int = 6000, temperature: float = 0.5) -> str:
    """Unified per-tier call. Routes to Anthropic (Opus/Fable) or an OpenAI-compatible provider."""
    if provider == "anthropic":
        return claude(client, model, system, user, bucket, max_tokens=max_tokens)
    return oai_call(provider, model, system, user, bucket,
                    json_mode=json_mode, max_tokens=max_tokens, temperature=temperature) or ""


def rigour_llm(client, system: str, user: str) -> str:
    return llm(RIGOUR_PROVIDER, RIGOUR_MODEL, system, user, "rigour", client=client,
               json_mode=True, max_tokens=8000, temperature=0.4)


def gate_llm(client, system: str, user: str) -> str:
    return llm(GATE_PROVIDER, GATE_MODEL, system, user, "gate", client=client,
               json_mode=True, max_tokens=1500, temperature=0.2)


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
    ap.add_argument("--breadth", type=int, default=12, help="breadth (idea) agents")
    ap.add_argument("--workers", type=int, default=8, help="max concurrent API calls per tier")
    ap.add_argument("--gate-panel", type=int, default=2, help="independent gate verifiers per survivor")
    ap.add_argument("--rigour-workers", type=int,
                    default=int(os.environ.get("EXPLORE_RIGOUR_WORKERS", "1")),
                    help="concurrent rigour calls (keep at 1 for heavy Featherless models — a 397B "
                         "model costs 4 of 4 plan concurrency units, so only ONE may run at a time)")
    ap.add_argument("--refine", action="store_true",
                    help="run the optional DeepSeek peer-refine tier (off by default; needs DeepSeek)")
    ap.add_argument("--budget-usd", type=float, default=float(os.environ.get("EXPLORE_BUDGET_USD", "6")))
    args = ap.parse_args()

    # Each tier needs the key of whichever provider it's routed to.
    tiers = {BREADTH_PROVIDER, RIGOUR_PROVIDER, GATE_PROVIDER}
    need = {"ANTHROPIC_API_KEY" if p == "anthropic" else PROVIDERS[p][1] for p in tiers}
    if args.refine:
        need.add("DEEPSEEK_API_KEY")
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        print(f"missing key(s) {missing} — pipeline no-ops (no spend).")
        return 0
    client = _anthropic() if "anthropic" in tiers else None
    print(f"routing: breadth={BREADTH_PROVIDER}/{BREADTH_MODEL}  rigour={RIGOUR_PROVIDER}/{RIGOUR_MODEL}  "
          f"gate={GATE_PROVIDER}/{GATE_MODEL}")
    if "featherless" in tiers:
        featherless_models_hint()

    seen = load_seen()
    # Tier 1 — breadth (ideas)
    ideas = run_breadth(args.breadth, args.workers, seen, client=client)
    print(f"tier1 breadth: {len(ideas)} novel ideas from {args.breadth} {BREADTH_PROVIDER} agents "
          f"(~${_spend['breadth']:.3f}, {_toks['breadth']} out-tok)")
    if not ideas:
        print("no novel ideas this run.")
        return 0

    # Tier 1.5 — optional DeepSeek peer cross-check + refine (off unless --refine and a DeepSeek key).
    if args.refine and os.environ.get("DEEPSEEK_API_KEY"):
        refined = run_refine(ideas, args.workers)
        print(f"tier1.5 DeepSeek peer-refine: {len(refined)}/{len(ideas)} kept + sharpened "
              f"(~${_spend['deepseek']:.3f} total DeepSeek)")
        ideas = refined
        if not ideas:
            print("peer review rejected all ideas this run.")
            return 0

    # Tier 2 + 3 (rigour then verify), budget-bounded
    processed = []
    with ThreadPoolExecutor(max_workers=max(1, args.rigour_workers)) as ex:
        futs = [ex.submit(rigour_and_verify, client, idea) for idea in ideas]
        for fut in as_completed(futs):
            processed.append(fut.result())
            if _spend["rigour"] + _spend["gate"] >= args.budget_usd:
                print(f"::warning:: budget ${args.budget_usd} reached in rigour tier; stopping early")
                break
    supported = [c for c in processed if c["_outcome"] == "supported"]
    print(f"tier2/3 rigour+verify: {len(supported)} supported, "
          f"{sum(c['_outcome']=='refuted' for c in processed)} refuted, "
          f"{sum(c['_outcome']=='parked' for c in processed)} parked "
          f"(~${_spend['rigour']:.3f}, {_toks['rigour']} out-tok)")

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
          f"(breadth ${_spend['breadth']:.3f} / rigour ${_spend['rigour']:.3f} / "
          f"gate ${_spend['gate']:.3f}" + (f" / deepseek ${_spend['deepseek']:.3f}" if _spend['deepseek'] else "") + ")")

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
