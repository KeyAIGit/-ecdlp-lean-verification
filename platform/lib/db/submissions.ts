// DB helpers for the verification queue (Step 3). Submissions are the ONLY user-writable data;
// everything else is a read of the git-backed truth layer. Requires DATABASE_URL (the API
// route and worker guard on it). `verdict` is written only by the worker, never the client.

import { and, desc, eq, isNull, sql } from "drizzle-orm";
import { db } from "./client";
import { users, submissions } from "./schema";

/** Upsert the signed-in Clerk user into `users`, returning our internal user id. */
export async function ensureUser(clerkId: string, email?: string): Promise<string> {
  const [row] = await db
    .insert(users)
    .values({ clerkId, email: email ?? null })
    .onConflictDoUpdate({ target: users.clerkId, set: { email: email ?? null } })
    .returning({ id: users.id });
  return row.id;
}

export async function createSubmission(input: {
  userId: string;
  domainId?: string;
  statement: string;
  leanSource: string;
}) {
  const [row] = await db
    .insert(submissions)
    .values({
      userId: input.userId,
      domainId: input.domainId ?? null,
      statement: input.statement,
      leanSource: input.leanSource,
    })
    .returning();
  return row;
}

export async function listByUser(userId: string) {
  return db
    .select()
    .from(submissions)
    .where(eq(submissions.userId, userId))
    .orderBy(desc(submissions.createdAt));
}

/**
 * Worker: **atomically** claim the oldest queued submission. A single
 * `UPDATE … WHERE id = (SELECT … FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *`
 * flips exactly one `queued` row to `running` in one statement, so two concurrent
 * workers can never claim the same submission (the loser's SKIP LOCKED skips the
 * locked row and picks the next, or gets nothing). Returns the claimed row or null.
 */
export async function claimNextQueued() {
  const result = await db.execute(sql`
    UPDATE ${submissions} AS s
    SET status = 'running', claimed_at = now()
    WHERE s.id = (
      SELECT id FROM ${submissions}
      WHERE status = 'queued'
      ORDER BY created_at
      FOR UPDATE SKIP LOCKED
      LIMIT 1
    )
    RETURNING s.*;
  `);
  const rows = (result as unknown as { rows?: unknown[] }).rows ?? (result as unknown as unknown[]);
  return (Array.isArray(rows) ? rows[0] : undefined) ?? null;
}

/**
 * Worker: write the verdict + log and mark the submission `done`. Guarded on
 * `status = 'running'` so only the worker that claimed it can finalize it, and a
 * verdict is never overwritten.
 */
export async function writeVerdict(id: string, verdict: string, log: string) {
  await db
    .update(submissions)
    .set({ verdict, log, status: "done" })
    .where(and(eq(submissions.id, id), eq(submissions.status, "running")));
}
