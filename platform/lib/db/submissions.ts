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

export interface ClaimOpts {
  /** How long a `running` claim is trusted before it is considered crashed and re-claimable. */
  leaseMs?: number;
  /** Give up (mark `failed`) after this many attempts. */
  maxAttempts?: number;
}

/**
 * Worker: **atomically** claim the next runnable submission, stamping it with this worker's
 * `workerId` (the claim token). One statement flips exactly one eligible row to `running`, so two
 * workers can never hold the same submission (the loser's `SKIP LOCKED` skips it). A row is
 * eligible if it is `queued`, OR `running` with a **stale lease** (its worker crashed) — the latter
 * gives automatic recovery of stuck jobs. `attempt_count` is incremented and bounded by
 * `maxAttempts`; rows past the bound are left for {@link failExhausted}. Returns the row or null.
 */
export async function claimNextQueued(workerId: string, opts: ClaimOpts = {}) {
  const leaseSec = Math.ceil((opts.leaseMs ?? 300_000) / 1000);
  const maxAttempts = opts.maxAttempts ?? 3;
  const result = await db.execute(sql`
    UPDATE ${submissions} AS s
    SET status = 'running',
        worker_id = ${workerId},
        claimed_at = now(),
        attempt_count = s.attempt_count + 1
    WHERE s.id = (
      SELECT id FROM ${submissions}
      WHERE attempt_count < ${maxAttempts}
        AND (
          status = 'queued'
          OR (status = 'running' AND claimed_at < now() - make_interval(secs => ${leaseSec}::int))
        )
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
 * `status = 'running'` **and** `worker_id = workerId`, so only the worker that currently holds the
 * claim can finalize it — a worker whose lease already expired (and whose job was re-claimed by
 * someone else) cannot clobber the new result. A verdict is never overwritten.
 */
export async function writeVerdict(id: string, workerId: string, verdict: string, log: string) {
  await db
    .update(submissions)
    .set({ verdict, log, status: "done" })
    .where(
      and(
        eq(submissions.id, id),
        eq(submissions.status, "running"),
        eq(submissions.workerId, workerId),
      ),
    );
}

/**
 * Sweeper: mark as `failed` any `running` row whose lease is stale AND whose retries are
 * exhausted, so exhausted jobs reach a terminal state instead of being re-claimed forever.
 */
export async function failExhausted(opts: ClaimOpts = {}) {
  const leaseSec = Math.ceil((opts.leaseMs ?? 300_000) / 1000);
  const maxAttempts = opts.maxAttempts ?? 3;
  await db.execute(sql`
    UPDATE ${submissions}
    SET status = 'failed'
    WHERE status = 'running'
      AND attempt_count >= ${maxAttempts}
      AND claimed_at < now() - make_interval(secs => ${leaseSec}::int);
  `);
}
