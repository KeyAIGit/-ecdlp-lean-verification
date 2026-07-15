// The data layer. A single `DataSource` interface with two implementations chosen at runtime:
//   - static (Step 1): reads the git-backed truth layer published to the public site.
//   - db     (Step 2): reads the platform's Postgres (domains/claims/submissions/users).
// Connecting a database is therefore a CONFIG change (set DATABASE_URL), not a rewrite: the
// pages and API routes call `getDataSource()` and never know which backend answered.
//
// The canonical Lean counts (ledger rows, distinct results) are always owned by the repo, so
// `getStats()` reads them from the published site in BOTH backends — the DB only holds the
// platform's own mutable data.

export type Stats = {
  ledger_rows: number;
  distinct_results: number;
  proved_modules: number;
  sorry_count: number;
  custom_axioms: number;
  curve: string;
  toolchain: string;
};

export type DomainStatus = "live" | "planned" | "exploratory";

export type Domain = {
  id: string;
  title: string;
  status: DomainStatus;
  one_liner?: string;
  notes?: string;
  slots?: { corpus: string | null; ontology: string | null; verifier: string };
};

export type ClaimStatus = "verified" | "planned";

export type Claim = {
  id: string;
  domainId: string;
  statement: string;
  status: ClaimStatus;
  evidenceRef?: string;
};

export interface DataSource {
  getStats(): Promise<Stats>;
  getDomains(): Promise<Domain[]>;
  getClaims(domainId: string): Promise<Claim[]>;
}

const BASE = process.env.NEXT_PUBLIC_DATA_BASE ?? "https://keyai.org";

/** Shared: the authoritative Lean counts always come from the repo's published stats.json. */
export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${BASE}/data/stats.json`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`fetch stats.json failed: ${res.status}`);
  return (await res.json()) as Stats;
}

/** Pick the backend from the environment. DB when DATABASE_URL is set, else the static site. */
export async function getDataSource(): Promise<DataSource> {
  if (process.env.DATABASE_URL) {
    const { dbDataSource } = await import("./data.db");
    return dbDataSource;
  }
  const { staticDataSource } = await import("./data.static");
  return staticDataSource;
}
