# External-host hypothesis drafter

The deterministic screening layer evaluates one million typed research-question
cells locally and retains only a bounded review queue. Language models do not
process the full million-cell universe.

`.github/workflows/hypothesis-drafter-server.yml` is the manual bridge from that
queue to Featherless. A GitHub-hosted runner only orchestrates SSH. The actual
Featherless request originates from the machine named by `SERVER_HOST`, avoiding
the Cloudflare 1010 block observed from GitHub-hosted runner egress.

## Required infrastructure

- any small always-on Linux CPU host with Git, Python 3, SSH, and outbound HTTPS;
- `SERVER_HOST`, `SSH_PRIVATE_KEY`, and `FEATHERLESS_API_KEY` repository secrets;
- optional `SERVER_USER` (defaults to `root`).

No GPU, local model weights, Lean toolchain, or direct DeepSeek/Kimi key is needed
for this workflow. Featherless performs inference remotely. The zero-token probe
must confirm that the selected model is available on the current plan before any
completion is requested.

## Safety boundary

The workflow is manual-only, accepts one of four policy-pinned models, and drafts
at most 30 queue items sequentially. It checks out the exact workflow commit on
the external host, retrieves a sanitized probe plus an untrusted JSON batch, and
deletes the remote run directory. The artifact expires after 14 days.

Drafts cannot become admissible, recommended, authorized, executable, or route
promoting. Model output does not satisfy independent review. A later ingestion
step must bind a retained fragment to its seed and review records; this workflow
does not write to the repository or Research Engine state.
