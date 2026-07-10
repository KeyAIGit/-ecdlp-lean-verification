"use client";

import { useEffect, useState } from "react";

// Gated submit flow (Step 3): paste a Lean statement + source, enqueue it, watch for the
// worker's verdict. The client only ever CREATES a queued submission; the verdict is written
// server-side by the sandboxed worker (worker/README.md). Needs DATABASE_URL to be live.

type Submission = {
  id: string;
  statement: string;
  verdict: string | null;
  createdAt: string;
};

export default function Submit() {
  const [statement, setStatement] = useState("");
  const [leanSource, setLeanSource] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [rows, setRows] = useState<Submission[]>([]);

  async function refresh() {
    const r = await fetch("/api/submissions");
    if (r.ok) setRows(await r.json());
  }
  useEffect(() => {
    refresh();
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setMsg("submitting…");
    const r = await fetch("/api/submissions", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ statement, leanSource }),
    });
    const body = await r.json().catch(() => ({}));
    if (r.ok) {
      setMsg(`queued (${body.id}). The worker will verify it and record a verdict.`);
      setStatement("");
      setLeanSource("");
      refresh();
    } else {
      setMsg(`error: ${body.error ?? r.status}`);
    }
  }

  return (
    <>
      <h1 style={{ fontSize: 28, margin: "0 0 8px" }}>Submit for verification</h1>
      <p style={{ color: "#48607f", marginTop: 0 }}>
        Enqueue a Lean statement. A sandboxed worker runs <code>lake</code> and records a
        kernel verdict — the same judge as the rest of the asset. This is Step 3; it needs the
        database + worker running.
      </p>

      <form onSubmit={submit} style={{ display: "grid", gap: 10, margin: "16px 0" }}>
        <input
          value={statement}
          onChange={(e) => setStatement(e.target.value)}
          placeholder="Human-readable statement (e.g. 'P-256 base point has order n')"
          style={{ padding: 10, border: "1px solid #dbe6f3", borderRadius: 8 }}
        />
        <textarea
          value={leanSource}
          onChange={(e) => setLeanSource(e.target.value)}
          placeholder={"import Mathlib\n\ntheorem my_claim : 2 + 2 = 4 := by decide"}
          rows={10}
          style={{
            padding: 10,
            border: "1px solid #dbe6f3",
            borderRadius: 8,
            fontFamily: "ui-monospace, Menlo, monospace",
            fontSize: 13,
          }}
        />
        <button
          type="submit"
          style={{
            justifySelf: "start",
            background: "#1d85ff",
            color: "#fff",
            border: 0,
            borderRadius: 8,
            padding: "10px 18px",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Queue for verification
        </button>
      </form>
      {msg && <p style={{ color: "#48607f", fontSize: 14 }}>{msg}</p>}

      <h2 style={{ fontSize: 18, marginTop: 24 }}>Your submissions</h2>
      {rows.length === 0 ? (
        <p style={{ color: "#94a4b4" }}>None yet.</p>
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          {rows.map((s) => (
            <div
              key={s.id}
              style={{
                background: "#fff",
                border: "1px solid #dbe6f3",
                borderRadius: 8,
                padding: "10px 12px",
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
              }}
            >
              <span>{s.statement}</span>
              <span
                style={{
                  fontWeight: 800,
                  color:
                    s.verdict === "verified"
                      ? "#0ca30c"
                      : s.verdict
                        ? "#d03b3b"
                        : "#94a4b4",
                }}
              >
                {s.verdict ?? "queued"}
              </span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
