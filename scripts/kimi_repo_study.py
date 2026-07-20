#!/usr/bin/env python3
"""Kimi repo-study — feed the machine-checked ECDLP repo state to Kimi (kimi-k3),
have it STUDY the actual frontier and propose GROUNDED, checkable next theorems,
then write the study to ``notes/KIMI_REPO_STUDY.md``.

Kimi is a DRAFTER only. Every proposal is a LEAD for the Lean kernel / CI to
verify — nothing here is trusted as proved, and no proposal enters the corpus
until Lean accepts it. This keeps the one invariant intact.

Standalone (only the ``openai`` SDK). Dispatch via
``.github/workflows/kimi-repo-study.yml`` with ``KIMI_API_KEY`` set; no key ⇒
clean no-op (green, zero spend).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Curated frontier context. The open walls + what is proved + the registered
# open stems — enough for Kimi to ground its proposals in real repo state.
CONTEXT_FILES = [
    ("BARRIERS.md", 24000),
    ("ABSTRACT_SCOPE.md", 12000),
    ("notes/DIVISION_POLY_TORSION_MAP.md", 16000),
    ("notes/POINT_COUNTING_KEYSTONE.md", 12000),
    ("notes/N7_EVEN_X_REDUCTION.md", 16000),
    ("VERIFIED.md", 18000),
]


def _read(rel: str, cap: int) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")[:cap]


def gather_context() -> str:
    parts: list[str] = []
    for rel, cap in CONTEXT_FILES:
        t = _read(rel, cap)
        if t:
            parts.append(f"===== FILE: {rel} =====\n{t}")
    # The registered OPEN TARGET stems — the actual open problems, in full.
    tdir = ROOT / "Ecdlp" / "Targets"
    if tdir.exists():
        for f in sorted(tdir.glob("*.lean")):
            parts.append(
                f"===== OPEN TARGET: Ecdlp/Targets/{f.name} =====\n"
                + f.read_text(encoding="utf-8")[:30000]
            )
    # Inventory of proved theorem/lemma names — the toolbox Kimi must build on.
    names: list[str] = []
    pdir = ROOT / "Ecdlp" / "Proved"
    if pdir.exists():
        for f in sorted(pdir.glob("*.lean")):
            for line in f.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s.startswith(("theorem ", "lemma ")):
                    names.append(f"{f.stem}: {s[:120]}")
    parts.append(
        "===== PROVED THEOREM INVENTORY (available lemmas — build ON these) =====\n"
        + "\n".join(names[:900])
    )
    return "\n\n".join(parts)


PROMPT = """You are a research mathematician auditing a MACHINE-CHECKED formalization \
(Lean 4 + Mathlib, pinned v4.31.0) of the elliptic-curve discrete-log problem for \
secp256k1 (y^2 = x^3 + 7 over F_p). Below is the repository state: the open barriers, \
what is already proved (with a theorem inventory), and the registered OPEN TARGET stems.

STUDY it, then propose {n} GROUNDED, checkable NEXT theorems that would advance an OPEN \
barrier or target. Hard requirements:
- Each proposal MUST build on lemmas that ALREADY EXIST in the inventory (cite exact names).
- Each must be plausibly provable in Lean 4 + Mathlib at the pinned version (no missing-foundation wishes).
- Prefer proposals that unblock the N7 uniform multiplication carrier, the division-polynomial \
walls (even_x/odd_x/y algebra, the ω y-coordinate), or the Frobenius / point-counting frontier.
- Do NOT restate things already proved; check the inventory first.

For EACH proposal give: id (slug), title (one line), statement (precise, Lean-ish), \
builds_on (2-5 EXACT inventory theorem names), barrier (which open wall/target it advances), \
difficulty (S|M|L), issue_body (2-4 sentences a Lean prover could pick up).

Reply as STRICT JSON, no prose outside it:
{{"proposals":[{{"id":"","title":"","statement":"","builds_on":[""],"barrier":"","difficulty":"S","issue_body":""}}]}}

===== REPOSITORY STATE =====
{context}
"""


def parse_json(raw: str) -> dict | None:
    s = (raw or "").strip()
    if "{" not in s or "}" not in s:
        return None
    try:
        return json.loads(s[s.index("{"): s.rindex("}") + 1])
    except Exception:
        return None


def call_kimi(prompt: str, max_tokens: int) -> str | None:
    from openai import OpenAI

    # `or` (not a get-default): CI sets KIMI_BASE_URL to "" when the secret is undefined, and an
    # empty base_url makes the OpenAI client raise a bare "Connection error". Fall back to the
    # public endpoint on empty; a real KIMI_BASE_URL secret (e.g. the .cn platform) still wins.
    client = OpenAI(
        base_url=os.environ.get("KIMI_BASE_URL") or "https://api.moonshot.ai/v1",
        api_key=os.environ["KIMI_API_KEY"],
    )
    model = os.environ.get("KIMI_MODEL") or "kimi-k3"
    # json_object first; retry plain if the provider rejects response_format.
    for use_json in (True, False):
        kw = {"model": model, "temperature": 0.6, "max_tokens": max_tokens,
              "messages": [{"role": "user", "content": prompt}]}
        if use_json:
            kw["response_format"] = {"type": "json_object"}
        try:
            resp = client.chat.completions.create(**kw)
            return resp.choices[0].message.content
        except Exception as e:  # noqa: BLE001
            print(f"::warning::kimi call failed (json={use_json}): {e}")
    return None


def render(proposals: list[dict], model: str) -> str:
    lines = [
        "# Kimi repo-study — grounded next-theorem proposals",
        "",
        f"> Generated by `{model}` (Moonshot) studying the repository frontier. "
        "**Drafter only** — every proposal is a LEAD for the Lean kernel / CI to verify; "
        "nothing here is proved, and none of it enters the corpus until Lean accepts it.",
        "",
    ]
    for i, p in enumerate(proposals, 1):
        builds = ", ".join("`" + str(b) + "`" for b in (p.get("builds_on") or []))
        lines += [
            f"## {i}. {p.get('title', '(untitled)')}  `[{p.get('difficulty', '?')}]`",
            f"- **id**: `{p.get('id', '')}`",
            f"- **barrier**: {p.get('barrier', '')}",
            f"- **statement**: {p.get('statement', '')}",
            f"- **builds on**: {builds}",
            f"- **issue body**: {p.get('issue_body', '')}",
            "",
        ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8, help="number of proposals to request")
    ap.add_argument("--max-tokens", type=int, default=16000,
                    help="output cap (kimi-k3 is verbose; keep generous to avoid truncation)")
    args = ap.parse_args()

    if not os.environ.get("KIMI_API_KEY"):
        print("KIMI_API_KEY absent — no-op (green, zero spend).")
        return 0

    ctx = gather_context()
    model = os.environ.get("KIMI_MODEL", "kimi-k3")
    print(f"context: {len(ctx)} chars; asking {model} for {args.n} grounded proposals")
    raw = call_kimi(PROMPT.format(n=args.n, context=ctx), args.max_tokens)
    obj = parse_json(raw or "")
    if not obj or not obj.get("proposals"):
        print(f"::warning::no proposals parsed. raw preview: {(raw or '')[:400]!r}")
        return 0
    proposals = [p for p in obj["proposals"] if isinstance(p, dict) and p.get("title")]
    print(f"Kimi returned {len(proposals)} proposals")
    if not proposals:
        return 0

    out = ROOT / "notes" / "KIMI_REPO_STUDY.md"
    out.write_text(render(proposals, model), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} with {len(proposals)} proposals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
