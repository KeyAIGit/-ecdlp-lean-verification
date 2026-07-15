// Step-1 backend: the git-backed truth layer, read from the published public site.
// No database. Used whenever DATABASE_URL is unset.

import { DataSource, Domain, Claim, Stats, fetchStats } from "./data";

const BASE = process.env.NEXT_PUBLIC_DATA_BASE ?? "https://keyai.org";

export const staticDataSource: DataSource = {
  getStats(): Promise<Stats> {
    return fetchStats();
  },

  async getDomains(): Promise<Domain[]> {
    const res = await fetch(`${BASE}/domains/registry.json`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) throw new Error(`fetch registry.json failed: ${res.status}`);
    const reg = (await res.json()) as { domains: Domain[] };
    return reg.domains;
  },

  // Step 1 has no structured claims store; the per-domain corpus lives as markdown in the
  // repo. Claims become first-class in Step 2 (DB). Return empty until then.
  async getClaims(): Promise<Claim[]> {
    return [];
  },
};
