# Server runbook — turn the Hetzner box into an autonomous prover node

Goal: run the Layer-2 prover loop (`scripts/prover_loop.py`) on the rented server
with a **warm local Lean toolchain**, so each proof attempt is verified by
`lake env lean` in *seconds* instead of a ~10-minute CI round-trip. This is the
10–50× speedup: CI stays the trusted gate, the server becomes the fast search.

> **I cannot run these steps for you.** This container has no SSH key for the box
> and no outbound route to it. The commands below are for you to run (or paste to
> me only the *outputs* you want analysed). Every proof the server finds still
> comes back through a reviewed PR and the CI gate — the server never bypasses the
> kernel.

## 0. SECURITY FIRST (do this before anything else)

The root password for `<old-server-host>` was posted in plain chat — **treat it as
compromised**. On a machine you trust:

```sh
# 1) log in once with the current password, then immediately rotate it:
ssh root@<old-server-host>
passwd                      # set a new strong password

# 2) add key-based auth (run the keygen on YOUR laptop, not the server):
#    (local)  ssh-keygen -t ed25519 -C "ecdlp-prover"
#    (local)  ssh-copy-id root@<old-server-host>

# 3) disable password login:
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh
```

After this, only your key opens the box. Do **not** paste the new password or the
private key anywhere.

## 1. Bootstrap (Lean + Mathlib warm cache)

```sh
ssh root@<old-server-host>
git clone https://github.com/KeyAIGit/-ecdlp-lean-verification.git
cd -ecdlp-lean-verification
bash scripts/server-setup.sh          # elan + Lean v4.31.0 + `lake exe cache get` + build
# verify the toolchain is warm:
lake env lean Ecdlp/Proved/CubeRoot.lean   # should exit 0 with no output
```

`lake exe cache get` pulls the prebuilt Mathlib `.olean`s (~5–7 GB) so nothing
recompiles. After this, `lake env lean <file>` verifies a single file in seconds.

## 2. Run the prover loop once (Tier 0, no API key needed)

```sh
python3 scripts/prover_loop.py --tier0-only     # see --help for flags
```

Tier 0 is the zero-cost tactic ladder (`rfl/decide/native_decide/simp/omega/ring/
aesop`). It needs no API key and closes the easy targets immediately.

## 3. Enable the model tiers (optional)

Tiers 1–2 call Featherless (Pythagoras-Prover-4B → Goedel-Prover-V2-32B). Provide
the key as an **environment variable only** — never commit it:

```sh
export FEATHERLESS_API_KEY=...           # same secret as the GitHub Actions one
python3 scripts/prover_loop.py
```

## 4. Run an unattended cycle after explicit dispatch

Do not install a recurring cron on a secret-bearing verifier host. The scheduled
triggers were removed by the 2026-07 execution-security audit; repository workflows
remain manual-only until model-generated code runs in a secret-free, network-off,
ephemeral sandbox. See `notes/EXECUTION_SECURITY.md`.

An explicitly dispatched server or GitHub Actions run may complete one bounded
cycle and capture logs. A separate external Codex scheduler may dispatch repository
maintenance work, but it is not configured or claimed by this repository.

For a Lean-accepted candidate, the loop writes it under `candidates/`. To close the
loop end-to-end on the server, the promotion step (move `Targets/`→`Proved/`, import
in `Ecdlp.lean`, row in `VERIFIED.md`, open a PR) should run as a separate reviewed
step — mirror `.github/workflows/prove.yml` Stage B. Keep a human in the merge path.

## 5. What flows back

- The server **finds** proofs fast (warm `lake env lean`).
- Candidates → a branch → a **draft PR** → CI re-verifies with the no-`sorry` gate →
  a delegated maintainer reviews and merges. The trust boundary is unchanged; the server only accelerates
  search. The kernel remains the only judge.

## 6. GitHub Actions → server bridge (automation)

`.github/workflows/server-run.yml` lets a GitHub Actions runner SSH into the server
and run a command in the repo there (warm Lean + CAS), bringing the output back as a
log + artifact. The runner has internet access, so this works even though the
ephemeral dev sandbox cannot reach the box. Manual-only (`workflow_dispatch`) — it
never auto-runs and does not touch the build gate.

**One-time setup (you):**
1. Server side: rebuild/create the box with the SSH **public** key (so it is in
   `~/.ssh/authorized_keys`), then run steps 1–2 above so Lean+Mathlib are warm.
2. GitHub → repo **Settings → Secrets and variables → Actions → New repository
   secret**, add:
   - `SSH_PRIVATE_KEY` — the OpenSSH **private** key (whole `-----BEGIN…END-----`).
   - `SERVER_HOST` — the server IP (e.g. `<SERVER_HOST>`).
   - `SERVER_USER` *(optional)* — login user, defaults to `root`.

**Run it:** GitHub → **Actions → "Run on server (warm Lean + CAS)" → Run workflow**.
Leave the default command (a Lean + sympy smoke test) or type your own, e.g.
`python3 -c "import sympy; print(sympy.factorint(<n>-1))"` or
`lake env lean Ecdlp/Proved/EmbeddingDegree.lean`. The output appears in the run log
and as the `server-output` artifact.

**Security:** the private key lives only in the GitHub secret and is written to the
runner's `~/.ssh` for the job. The command input is interpreted by the *server's*
shell — only the repo owner can dispatch, so treat it as your own shell on the box.
`StrictHostKeyChecking=accept-new` trusts the host key on first connect (TOFU); pin
it later if you want stricter checking.

## Notes / honest limits

- I can't SSH in from here, so I can't confirm the box's state — paste me
  `lake env lean ...` output or `prover.log` tails and I'll analyse them.
- A CAS scratchpad (PARI/sympy) for number-theory experiments is available via
  `WITH_CAS=1 bash scripts/server-setup.sh` if you want it.
- Disk: Mathlib cache is ~5–7 GB; the 8 GB box is enough for Lean but tight if you
  also add SageMath — install that only on a larger box.
