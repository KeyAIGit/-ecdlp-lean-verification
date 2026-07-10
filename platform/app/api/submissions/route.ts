import { NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";

// POST /api/submissions  — enqueue a Lean statement for verification (login required).
// GET  /api/submissions  — list the signed-in user's submissions + verdicts.
//
// Requires DATABASE_URL (Step 2). The client can NEVER set `verdict` — only the worker does,
// after a sandboxed `lake` run. Submissions are untrusted input; see worker/README.md.

function dbUnavailable() {
  return NextResponse.json(
    { error: "verification queue needs a database (set DATABASE_URL — Phase 2 Step 2/3)" },
    { status: 501 },
  );
}

export async function POST(req: Request) {
  const { userId: clerkId } = await auth();
  if (!clerkId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  if (!process.env.DATABASE_URL) return dbUnavailable();

  const body = (await req.json().catch(() => null)) as
    | { statement?: string; leanSource?: string; domainId?: string }
    | null;
  const statement = body?.statement?.trim();
  const leanSource = body?.leanSource?.trim();
  if (!statement || !leanSource) {
    return NextResponse.json({ error: "statement and leanSource are required" }, { status: 400 });
  }
  if (leanSource.length > 20000) {
    return NextResponse.json({ error: "leanSource too large (max 20000 chars)" }, { status: 413 });
  }

  const { ensureUser, createSubmission } = await import("../../../lib/db/submissions");
  const user = await currentUser();
  const email = user?.primaryEmailAddress?.emailAddress;
  const uid = await ensureUser(clerkId, email);
  const row = await createSubmission({ userId: uid, domainId: body?.domainId, statement, leanSource });
  return NextResponse.json({ id: row.id, status: "queued" }, { status: 201 });
}

export async function GET() {
  const { userId: clerkId } = await auth();
  if (!clerkId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  if (!process.env.DATABASE_URL) return dbUnavailable();

  const { ensureUser, listByUser } = await import("../../../lib/db/submissions");
  const uid = await ensureUser(clerkId);
  const rows = await listByUser(uid);
  return NextResponse.json(rows);
}
