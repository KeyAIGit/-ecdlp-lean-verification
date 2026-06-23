# Ecdlp/Proved/

Promoted, machine-checked theorems. Every `.lean` file here is **imported by
`Ecdlp.lean`**, so `lake build` compiles and verifies it, and the CI no-`sorry`
gate applies. A file lands here only after the Lean kernel accepts its proof with
no `sorry`/`admit`, at which point a row is added to `../../VERIFIED.md`.

Do not place open conjectures here — those live in `../Targets/` until proved.
