# Connecting the Hetzner CPU server as an autonomous Layer-2 prover node

The server has no SSH access (the key was never created), and this assistant is
**network-walled from the Hetzner API** (the dev container's egress policy denies
`api.hetzner.cloud`). So the one-time connect must be done by a human through the
**Hetzner Cloud Console** — the browser-based root shell that needs **no SSH key**.

After this one-time setup the node runs itself: it pulls the dev branch, runs the
prover loop (Tier-0 tactic ladder + Featherless Pythagoras-4B / Goedel-32B) in a
warm Lean toolchain, and pushes any kernel-accepted candidates to the
`server/candidates` branch for review. The verified base (`main`, `Ecdlp/Proved`)
is never touched here; promotion stays a reviewed PR.

## What the CPU server is good for (honest scope)
- **Warm verification:** `lake env lean` in ~30s vs ~5min on CI → the prover loop
  runs ~10× faster and can run 24/7.
- It is **CPU-only (no GPU)**: it does *not* host the prover models — those are the
  Featherless cloud API. It drives them and validates their output fast.
- **Yield expectation:** Tier-0 closes concrete/decidable goals; the hard structural
  targets still need human/assistant formalization. This node thickens the verified
  graph's breadth and offloads the mechanical search — it is not a shortcut to the
  deep theorems.

## One-time setup (paste in the Hetzner Cloud Console → your server → "Console")

```bash
# 1. base tools + clone (public repo, no auth needed for clone)
apt-get update -y && apt-get install -y git tmux curl
cd /root
git clone https://github.com/KeyAIGit/-ecdlp-lean-verification.git
cd -ecdlp-lean-verification

# 2. install Lean v4.31.0 + Mathlib cache + build  (~10–15 min, ~6 GB oleans)
bash scripts/server-setup.sh
~/.elan/bin/lake env lean Ecdlp/Proved/CubeRoot.lean && echo "LEAN OK"   # sanity check

# 3. provide the two secrets (typed, NOT echoed, stored 0600 — never in the repo)
read -rsp "Featherless API key: " FK; echo; printf '%s' "$FK" > ~/.featherless_key; chmod 600 ~/.featherless_key
read -rsp "GitHub PAT: " PAT; echo
git config --global credential.helper store
printf 'https://x-access-token:%s@github.com\n' "$PAT" > ~/.git-credentials; chmod 600 ~/.git-credentials

# 4. launch the daemon in tmux (survives Console disconnect)
tmux new -d -s prover 'bash scripts/prover_daemon.sh >> ~/prover-daemon.log 2>&1'
echo "started; watch with:  tail -f ~/prover-daemon.log"
```

## The GitHub PAT (step 3)
Create a **fine-grained personal access token** (github.com → Settings → Developer
settings → Fine-grained tokens):
- **Repository access:** only `KeyAIGit/-ecdlp-lean-verification`.
- **Permissions:** *Contents* → Read and write (that is all the daemon needs to push
  the `server/candidates` branch).
- Short expiry is fine (30–90 days); the daemon only pushes a scratch branch.

## Security
- **Rotate the Hetzner API token** you pasted in chat — it grants full account control
  (create/delete servers, billing). Hetzner Console → Security → API Tokens → delete →
  create new. Do not paste the new one anywhere shared.
- Both server secrets live only in `~/.featherless_key` and `~/.git-credentials`
  (0600) on the box — never in the repo or in CI logs.

## Operating the node
- Watch: `tail -f ~/prover-daemon.log`
- Stop:  `tmux kill-session -t prover`
- Restart after reboot: re-run step 4 (everything else persists).
- Results: review the `server/candidates` branch; accepted candidates are promoted
  into `Ecdlp/Proved/` via a normal reviewed PR, then the target's status flips to
  `verified`.
