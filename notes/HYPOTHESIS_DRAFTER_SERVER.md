# External-host hypothesis drafter

The deterministic screening layer evaluates one million typed research-question
cells locally and retains only a bounded review queue. Language models do not
process the full million-cell universe.

The drafter has two explicit lanes:

- `typed_evidence` is the default provenance-bound drafting lane. It reads
  generated seeds from `data/research_engine_state.json`, resolves their exact
  cells and source claims in `data/typed_evidence_state.json`, and binds the
  prompt to the claim packet, typed locators such as source sections, Lean
  theorem names and certificate fields, artifact hashes, repository
  evidence-file hashes, and the matching
  `repo/ECDLP_DECISION_SUBSTRATE.json` mode and research object.
  Seeds that already have a submitted proposal are skipped unless a local caller
  explicitly requests a replay. The current research decision admits formulation
  only of `HYP-M16-SOLVER-SLOPE-001`; this reviewed drafter policy maps that
  object to seed `HGS-DC5FF2FC9E71`. The seed already has
  `HGP-M16-SOLVER-SLOPE-001`, so the default typed-evidence request count is
  intentionally zero. Skipping it prevents duplicate drafting; it is not a
  quality signal. The proposal remains `needs_revision`, unreviewed,
  non-executable, unauthorized, and blocked on `missing_exact_mechanism`. The
  parked auxiliary-curve seed is not silently drafted. A zero-request dispatch
  records `skipped_no_eligible_seed`, provisions no provider secret, and makes
  no provider call. Submitted seeds may be included only in a local dry
  request-plan replay with `--include-submitted`; live mode rejects that flag.
- `brainstorm_queue` reads bounded representatives from the broad structural
  map. It carries no source assurance. Its fragments must cite zero source-claim
  IDs and cannot enter scientific review until a later typed-evidence binding.

`.github/workflows/hypothesis-drafter-server.yml` is the manual bridge from that
queue to Featherless. The GitHub runner builds the expected request plan from
the exact clean commit; evidence and context bytes are read from immutable Git
blobs at that commit, not reread from the mutable worktree. The runner
orchestrates SSH, compares the returned request records and their digest-bound
identities against the independently generated plan,
rehashes provider artifacts, and reparses each raw response. Only the provider
API request originates from `SERVER_HOST`; Featherless performs inference
remotely. This avoids the Cloudflare 1010 block observed from GitHub-hosted
runner egress.

## Required infrastructure

- any small always-on Linux CPU host with Git, Python 3, SSH, and outbound HTTPS;
- a `hypothesis-drafter-production` GitHub Environment restricted to protected
  `main`;
- environment variable `DRAFTER_ENVIRONMENT_READY=protected-main-v1`, set only
  after that branch policy is independently checked;
- `SERVER_HOST`, exact `SERVER_KNOWN_HOSTS`, `SSH_PRIVATE_KEY`, and
  `FEATHERLESS_API_KEY` environment secrets;
- optional `SERVER_USER` (defaults to `root`).

Do not retain repository-level copies of those secrets. Nonzero live use remains
blocked until the Environment branch policy, required reviewer policy, variable,
and secret scope have been checked in authenticated GitHub settings; repository
code cannot prove that external configuration.

No GPU, local model weights, Lean toolchain, or direct DeepSeek/Kimi key is needed
for this workflow. Featherless performs inference remotely. The zero-token probe
must confirm that the selected model is available on the current plan before any
completion is requested.

For a nonzero batch, `SERVER_HOST` is credential-trusted: its administrator can
observe or retain the long-lived Featherless key despite cleanup commands. The
30-call code limit is a scientific budget, not a defense against host compromise.
Use a dedicated host, a provider-side quota where available, and rotate the key
after decommissioning that host. `SERVER_KNOWN_HOSTS` pins its SSH public key;
trust-on-first-use is prohibited.

## Safety boundary

The workflow is manual-only, accepts one of four policy-pinned models, and drafts
at most 30 queue items sequentially. It checks out the exact workflow commit on
the external host, retrieves a sanitized probe plus an untrusted JSON batch, and
attempts best-effort deletion of the remote run directory; the credential-trusted
host may still retain data. The artifact expires after 14 days.

Each output path has a single-writer lease and every checkpoint uses a unique
same-directory temporary file. A partial provider failure returns a nonzero CLI
status, retains completed responses plus replayable HTTP status/body metadata,
uploads that bounded partial batch, and leaves the workflow red.

Drafts cannot become admissible, recommended, authorized, executable, or route
promoting. Model output does not satisfy independent review. Provenance-bound
means only that the supplied claim packet, typed locators, context documents,
and evidence-file hashes are identifiable and immutable. Model-authored claim
links are schema assertions, not evidence support, source assurance, or
scientific validation. The external host also cannot provide cryptographic
attestation that an unsigned response came from the named model; the raw body
is retained for replay, not promoted to an independent review. A later ingestion
step must bind a retained fragment to its seed and review records; this workflow
does not write to the repository or Research Engine state.
