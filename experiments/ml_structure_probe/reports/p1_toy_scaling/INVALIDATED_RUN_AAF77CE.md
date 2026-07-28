# Invalidated P1E run at `aaf77ce`

Status: invalidated before any result was retained.

The independent result validator found 274 errors after 899,041 EC scalar
multiplications. All errors traced to an incomplete committed selection
ledger:

- selection summary: 196 screen, 7 confirmation, 16 control fits;
- committed ledger: 191 screen, 7 confirmation, 16 control fits;
- missing identities: 16-bit `rbf-compressed-c128` at seeds 307, 401, 503,
  601, and 701;
- the selected winner remained `trees-glv-d8-l32`, but the provenance was
  invalid regardless of whether the winner changed.

Within one runner process this state is unreachable because each successful
row is appended before its in-memory success count is incremented. File
timestamps show that the shared ledger path was recreated during selection.
The cause is therefore a concurrent mutation of the same output path through
the previous unprotected truncate-and-append protocol.

Audit bindings:

- selection source commit:
  `13e5c43836adb12f7a2e46be1fecf256205aa5da`;
- selection artifact commit:
  `aaf77ce0523280d60a0e0fa98bafa911b7a2fe88`;
- failed validator report SHA-256:
  `3950a3d5be76723cb752ffaac91bb37b9ca12b98c4d3f0a87e9752a471d3cf56`;
- invalid assay result SHA-256:
  `bae56ec6940928a4e2df4b1927e6b33df2714a656dd0cbfe655e35c08c2739ca`;
- invalid evaluation ledger SHA-256:
  `d48d8e0910d1dda09bfd251cda40107c70e0824450148b6287bd07838cbf9a97`.

Corrective action:

1. retire every blind shard opened by this run;
2. use replacement catalog nonce `output-lock-recovery-r2`, exclude all 40
   retired field primes by a committed SHA-256 list, and move the exhausted
   12-bit rung to 13 bits;
3. lock the output stage against concurrent writers;
4. publish ledgers atomically from a complete identity matrix and read them
   back before hashing;
5. require an independent committed selection validation before opening any
   replacement blind shard;
6. repeat selection, evaluation, and independent result validation.

The large failed artifacts remain local and ignored. Their hashes above retain
the audit linkage without treating an invalid run as a result.
