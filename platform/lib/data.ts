// Reads the already-verified truth layer that the Lean repo publishes to the public site.
// Step 1 has NO database: the platform re-presents the git-backed asset behind auth. When
// Step 2 adds Postgres, only this module changes — the pages call the same functions.

const BASE = process.env.NEXT_PUBLIC_DATA_BASE ?? "https://keyai.org";

export type Stats = {
  ledger_rows: number;
  distinct_results: number;
  proved_modules: number;
  sorry_count: number;
  custom_axioms: number;
  curve: string;
  toolchain: string;
};

export type Domain = {
  id: string;
  title: string;
  status: "live" | "planned" | "exploratory";
  one_liner?: string;
  notes?: string;
  slots?: { corpus: string | null; ontology: string | null; verifier: string };
};

async function getJSON<T>(path: string): Promise<T> {
  // Revalidate hourly: the source of truth is the repo; this is a cached read of it.
  const res = await fetch(`${BASE}/${path}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`fetch ${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

export async function getStats(): Promise<Stats> {
  return getJSON<Stats>("data/stats.json");
}

export async function getDomains(): Promise<Domain[]> {
  const reg = await getJSON<{ domains: Domain[] }>("domains/registry.json");
  return reg.domains;
}
