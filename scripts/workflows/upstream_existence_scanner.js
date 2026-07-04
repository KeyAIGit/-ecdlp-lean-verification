export const meta = {
  name: 'upstream-existence-scanner',
  description: 'Scan mathlib4 (master + open PRs + Zulip) for existing Lean proofs of our open ECDLP targets/barriers',
  phases: [
    { title: 'Scan', detail: 'one web-research agent per topic' },
    { title: 'Synthesize', detail: 'aggregate into a free-ports / barriers map' },
  ],
}

const TOPICS = [
  { key: 'weil-pairing', q: 'the Weil pairing on elliptic curves (e_n on n-torsion E[n], bilinearity, values in mu_n), and n-torsion structure E[n] ~= (Z/n)^2, in Lean 4 / mathlib4' },
  { key: 'semaev-summation-poly', q: 'Semaev summation polynomials / elliptic summation polynomials S_n (the polynomial that vanishes iff n points sum to O) in Lean 4 / mathlib4' },
  { key: 'elliptic-nets-general', q: 'general (multi-index, rank >= 2) elliptic nets a la Stange (IsEllipticNet over a free abelian group, net recurrences, subnet functoriality) in Lean 4 / mathlib4, beyond the rank-1 IsEllSequence' },
  { key: 'ec-endomorphism-frobenius', q: 'elliptic-curve endomorphisms / isogenies realized as additive group homomorphisms of the point group, the q-power Frobenius endomorphism on E(F_q) points, and the general theorem that an O-fixing rational map is a group hom, in Lean 4 / mathlib4 (EllipticCurve.Isogeny)' },
  { key: 'division-polynomials-torsion', q: 'general division polynomials psi_n of an elliptic curve and the equivalence psi_n(P)=0 iff P is n-torsion (the n-torsion / division-polynomial bridge) in Lean 4 / mathlib4' },
  { key: 'generic-group-cost-model', q: 'a generic group model / oracle query-complexity / cost model framework (counting group operations or oracle queries) for cryptographic lower bounds in Lean 4 / mathlib4' },
  { key: 'lattice-reduction-lll', q: 'lattice reduction (LLL, BKZ), shortest/closest vector problem (SVP/CVP), or the hidden number problem, formalized in Lean 4 / mathlib4' },
  { key: 'other-standard-curves', q: 'formalizations of specific standard elliptic curves other than a generic Weierstrass curve — NIST P-256, Curve25519 / ed25519, or their group orders / parameters — in Lean 4 / mathlib4' },
]

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['topic', 'verdict', 'locations', 'adapt_effort', 'notes'],
  properties: {
    topic: { type: 'string' },
    verdict: { type: 'string', enum: ['in_master', 'open_pr', 'partial', 'none', 'unclear'] },
    locations: { type: 'string', description: 'concrete URLs: mathlib4 files / PR numbers / Zulip threads, or "none found"' },
    adapt_effort: { type: 'string', description: 'if it exists: what adopting/porting it into a pinned Mathlib v4.31 downstream repo would take (transcription / rebase / from-scratch)' },
    notes: { type: 'string', description: 'one-paragraph evidence-based summary; flag uncertainty explicitly' },
  },
}

phase('Scan')
const scans = await parallel(TOPICS.map(t => () =>
  agent([
    'Research task (read-only, web). Determine whether the following already has an existing Lean 4 / mathlib4 formalization — in master, in an open/stalled pull request, or not at all.',
    '',
    'TARGET: ' + t.q,
    '',
    'Use WebSearch / WebFetch (load them via ToolSearch if needed). Check, with evidence:',
    '1. mathlib4 master (search the leanprover-community/mathlib4 repo / mathlib4_docs) for the relevant definitions/theorems.',
    '2. Open or recently-merged mathlib4 pull requests (github.com/leanprover-community/mathlib4/pulls) — search PR titles/bodies.',
    '3. Lean Zulip (leanprover.zulipchat.com) threads discussing formalizing it.',
    '4. Personal Lean repos / branches of known contributors if surfaced.',
    '',
    'Be rigorous and skeptical. Distinguish "the generic theory exists" from "this specific object exists". Cite every claim with a URL. If you cannot verify, say verdict=unclear rather than guessing.',
    'Note: a downstream repo pins Mathlib v4.31.0. "adapt_effort" should say whether adopting a found result is transcription (exists in a form portable to v4.31), a PR rebase (stalled PR like the EllipticDivisibilitySequence net-relation), or genuinely from-scratch (nothing exists).',
    '',
    'Return exactly the schema fields for this one topic (topic = "' + t.key + '").',
  ].join('\n'),
    { label: 'scan:' + t.key, phase: 'Scan', agentType: 'general-purpose', effort: 'medium', schema: SCHEMA }
  ).then(v => v).catch(() => null)
))

const found = scans.filter(Boolean)

phase('Synthesize')
const report = await agent([
  'You are synthesizing an upstream-existence scan for a Lean 4 ECDLP/secp256k1 formalization project.',
  'Below are per-topic findings (JSON). Produce a concise, evidence-based markdown report with THREE sections:',
  '1. FREE PORTS / ADOPTABLE NOW — things that exist in master or a portable form and could be adopted into a pinned-Mathlib-v4.31 repo, ranked by value/effort (like the recently-found EllipticDivisibilitySequence net-relation port). Give links.',
  '2. STALLED-UPSTREAM (exists but in an open/stalled PR) — worth watching or helping land; give PR links.',
  '3. CONFIRMED BARRIERS — genuinely not formalized anywhere; these are the real gaps (publishable no-go map). Give the precise missing object.',
  'End with a one-paragraph honest bottom-line: how much of the ECDLP foundation is already formalized upstream vs genuinely missing, and what the highest-ROI next port would be.',
  'Do not invent links; only use what the findings provide. Flag any topic marked unclear.',
  '',
  'FINDINGS:',
  JSON.stringify(found, null, 1),
].join('\n'), { label: 'synthesize', phase: 'Synthesize', effort: 'high' })

return { scans: found, report }
