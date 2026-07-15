// Seed the platform DB from the repo's git-backed truth layer, so the database starts as a
// faithful copy of what the Lean repo already publishes. Idempotent: upserts domains and
// replaces each seeded domain's claims. Run from platform/ with DATABASE_URL set:
//
//   npm run seed
//
// Reads ../domains/registry.json (all domains) and ../domains/<id>/corpus.md (structured
// claims, currently P-256). secp256k1's 486-claim corpus is a CSV triage source, not seeded
// here — its verified rows live in the Lean ledger.

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { eq } from "drizzle-orm";
import { db } from "../lib/db/client";
import { domains as domainsTable, claims as claimsTable } from "../lib/db/schema";

const REPO = join(process.cwd(), "..");

type RegDomain = {
  id: string;
  title: string;
  status: "live" | "planned" | "exploratory";
  one_liner?: string;
  notes?: string;
  slots?: { corpus: string | null; ontology: string | null; verifier: string };
};

/** Parse a markdown table `| id | claim | status | evidence |` into claim rows. */
function parseCorpusClaims(md: string) {
  const out: { statement: string; status: "verified" | "planned"; evidenceRef?: string }[] = [];
  for (const line of md.split("\n")) {
    const t = line.trim();
    if (!t.startsWith("|")) continue;
    const cells = t.split("|").slice(1, -1).map((c) => c.trim());
    if (cells.length < 4) continue;
    if (cells[0] === "id" || cells[0].startsWith("---")) continue; // header / separator
    const statusRaw = cells[2].replace(/\*/g, "").toLowerCase();
    const status = statusRaw.includes("verified") ? "verified" : "planned";
    out.push({ statement: cells[1], status, evidenceRef: cells[3] || undefined });
  }
  return out;
}

async function main() {
  const reg = JSON.parse(
    readFileSync(join(REPO, "domains", "registry.json"), "utf-8"),
  ) as { domains: RegDomain[] };

  for (const d of reg.domains) {
    await db
      .insert(domainsTable)
      .values({
        id: d.id,
        title: d.title,
        status: d.status,
        oneLiner: d.one_liner ?? null,
        notes: d.notes ?? null,
        corpusRef: d.slots?.corpus ?? null,
        ontologyRef: d.slots?.ontology ?? null,
        verifier: d.slots?.verifier ?? "lean-kernel",
      })
      .onConflictDoUpdate({
        target: domainsTable.id,
        set: {
          title: d.title,
          status: d.status,
          oneLiner: d.one_liner ?? null,
          notes: d.notes ?? null,
          corpusRef: d.slots?.corpus ?? null,
          ontologyRef: d.slots?.ontology ?? null,
          verifier: d.slots?.verifier ?? "lean-kernel",
        },
      });

    const corpusRel = d.slots?.corpus;
    if (corpusRel && corpusRel.endsWith(".md") && existsSync(join(REPO, corpusRel))) {
      const claims = parseCorpusClaims(readFileSync(join(REPO, corpusRel), "utf-8"));
      await db.delete(claimsTable).where(eq(claimsTable.domainId, d.id));
      if (claims.length) {
        await db
          .insert(claimsTable)
          .values(claims.map((c) => ({ ...c, domainId: d.id })));
      }
      console.log(`seeded ${d.id}: ${claims.length} claims`);
    } else {
      console.log(`seeded ${d.id}: domain only (no structured corpus)`);
    }
  }
  console.log(`done: ${reg.domains.length} domains`);
}

main().then(
  () => process.exit(0),
  (e) => {
    console.error(e);
    process.exit(1);
  },
);
