// Step-2 backend: the platform Postgres. Domains/claims come from the DB (seeded from the repo
// truth layer, then mutable). Stats stay authoritative from the repo's published counts.

import { eq } from "drizzle-orm";
import { DataSource, Domain, Claim, Stats, fetchStats } from "./data";
import { db } from "./db/client";
import { domains as domainsTable, claims as claimsTable } from "./db/schema";

export const dbDataSource: DataSource = {
  getStats(): Promise<Stats> {
    return fetchStats();
  },

  async getDomains(): Promise<Domain[]> {
    const rows = await db.select().from(domainsTable);
    return rows.map((r) => ({
      id: r.id,
      title: r.title,
      status: r.status,
      one_liner: r.oneLiner ?? undefined,
      notes: r.notes ?? undefined,
      slots: {
        corpus: r.corpusRef,
        ontology: r.ontologyRef,
        verifier: r.verifier,
      },
    }));
  },

  async getClaims(domainId: string): Promise<Claim[]> {
    const rows = await db
      .select()
      .from(claimsTable)
      .where(eq(claimsTable.domainId, domainId));
    return rows.map((r) => ({
      id: r.id,
      domainId: r.domainId,
      statement: r.statement,
      status: r.status,
      evidenceRef: r.evidenceRef ?? undefined,
    }));
  },
};
