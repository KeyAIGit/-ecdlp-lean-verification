import { getStats, getDomains } from "../lib/data";

// Public overview: the verified asset, re-presented behind the platform (no login needed).
export const revalidate = 3600;

const BADGE: Record<string, { bg: string; fg: string }> = {
  live: { bg: "#e6f6e6", fg: "#0ca30c" },
  planned: { bg: "#e7f1ff", fg: "#1d85ff" },
  exploratory: { bg: "#eef1f5", fg: "#64748b" },
};

export default async function Home() {
  const [stats, domains] = await Promise.all([getStats(), getDomains()]);
  const live = domains.filter((d) => d.status === "live").length;

  return (
    <>
      <h1 style={{ fontSize: 30, margin: "0 0 8px" }}>
        A machine-verifiable Research OS
      </h1>
      <p style={{ color: "#48607f", marginTop: 0 }}>
        Every listed result is checked by the Lean kernel — {stats.sorry_count}{" "}
        <code>sorry</code>, {stats.custom_axioms} custom axioms. This is the public
        surface; sign in for the private research area.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))",
          gap: 12,
          margin: "20px 0",
        }}
      >
        {[
          [stats.ledger_rows, "ledger rows"],
          [stats.distinct_results, "distinct results"],
          [stats.proved_modules, "proved modules"],
          [live, "live domains"],
        ].map(([n, label]) => (
          <div
            key={String(label)}
            style={{
              background: "#fff",
              border: "1px solid #dbe6f3",
              borderTop: "3px solid #1d85ff",
              borderRadius: 10,
              padding: 16,
            }}
          >
            <div style={{ fontSize: 26, fontWeight: 800, color: "#001a3f" }}>
              {String(n)}
            </div>
            <div style={{ fontSize: 12, color: "#687480", fontWeight: 700 }}>
              {label}
            </div>
          </div>
        ))}
      </div>

      <h2 style={{ fontSize: 20 }}>Domain portfolio</h2>
      <div style={{ display: "grid", gap: 12 }}>
        {domains.map((d) => {
          const b = BADGE[d.status] ?? BADGE.exploratory;
          return (
            <div
              key={d.id}
              style={{
                background: "#fff",
                border: "1px solid #dbe6f3",
                borderRadius: 10,
                padding: "14px 16px",
              }}
            >
              <div
                style={{ display: "flex", alignItems: "center", gap: 10 }}
              >
                <span
                  style={{
                    background: b.bg,
                    color: b.fg,
                    fontWeight: 800,
                    fontSize: 11,
                    textTransform: "uppercase",
                    padding: "2px 9px",
                    borderRadius: 999,
                  }}
                >
                  {d.status}
                </span>
                <strong style={{ color: "#001a3f" }}>{d.title}</strong>
              </div>
              {d.one_liner && (
                <p style={{ color: "#48607f", fontSize: 14, margin: "8px 0 0" }}>
                  {d.one_liner}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}
