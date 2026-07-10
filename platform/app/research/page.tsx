import { auth } from "@clerk/nextjs/server";

// The private area — only reachable after sign-in (enforced in middleware.ts, re-checked here).
// This is the home for speculative / work-in-progress research that must NOT sit on the public
// honest surface. Content is a placeholder until Step 2 wires a private data source.
export default async function Research() {
  const { userId } = await auth();

  return (
    <>
      <h1 style={{ fontSize: 28, margin: "0 0 8px" }}>Private research</h1>
      <p style={{ color: "#48607f", marginTop: 0 }}>
        You are signed in (<code>{userId}</code>). This gated area is the home for
        speculative and work-in-progress research kept off the public surface — the
        public brand only shows what the Lean kernel has accepted.
      </p>
      <div
        style={{
          background: "#fff",
          border: "1px dashed #b9cbe8",
          borderRadius: 10,
          padding: 20,
          color: "#48607f",
        }}
      >
        <strong>Placeholder.</strong> Step 2 of the platform plan connects this page to a
        private data source (a private repo or the platform database). Nothing here weakens
        the verified asset — this is a publishing boundary, not a second source of truth.
      </div>
    </>
  );
}
