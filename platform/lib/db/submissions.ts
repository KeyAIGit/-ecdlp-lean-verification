// DB helpers for the verification queue (Step 3). Submissions are the ONLY user-writable data;
// everything else is a read of the git-backed truth layer. Requires DATABASE_URL (the API
// route and worker guard on it). `verdict` is written only by the worker, never the client.

import { and, desc, eq, isNull } from "drizzle-orm";
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

/** Worker: atomically-ish claim the oldest unrun submission (verdict IS NULL). */
export async function claimNextQueued() {
  const [row] = await db
    .select()
    .from(submissions)
    .where(isNull(submissions.verdict))
    .orderBy(submissions.createdAt)
    .limit(1);
  return row ?? null;
}

/** Worker: write the verdict + log back to a submission. */
export async function writeVerdict(id: string, verdict: string, log: string) {
  await db
    .update(submissions)
    .set({ verdict, log })
    .where(and(eq(submissions.id, id), isNull(submissions.verdict)));
}
