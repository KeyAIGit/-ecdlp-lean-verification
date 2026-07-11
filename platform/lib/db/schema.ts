// Drizzle schema for the platform database (Step 2). Mirrors the data model in
// ../../PHASE2_PLAN.md. `domains` / `claims` are seeded from the repo's registry + corpus so
// the DB starts as a faithful copy of the git truth layer; `users` / `submissions` are the
// platform's own mutable state.

import {
  pgTable,
  pgEnum,
  uuid,
  text,
  integer,
  timestamp,
} from "drizzle-orm/pg-core";

export const domainStatus = pgEnum("domain_status", [
  "live",
  "planned",
  "exploratory",
]);

export const claimStatus = pgEnum("claim_status", ["verified", "planned"]);

// Submission lifecycle: `queued` (client-created) → `running` (a worker atomically claimed it)
// → `done` (verdict written) | `failed` (retries exhausted). `running` makes the claim atomic
// (no two workers pick the same row); a crashed worker's `running` row is re-claimable once its
// lease (claimed_at) goes stale, up to `attempt_count` = maxAttempts, after which it is `failed`.
export const submissionStatus = pgEnum("submission_status", [
  "queued",
  "running",
  "done",
  "failed",
]);

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  clerkId: text("clerk_id").notNull().unique(),
  email: text("email"),
  role: text("role").notNull().default("member"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const domains = pgTable("domains", {
  id: text("id").primaryKey(), // e.g. "ecdlp-secp256k1"
  title: text("title").notNull(),
  status: domainStatus("status").notNull(),
  oneLiner: text("one_liner"),
  notes: text("notes"),
  corpusRef: text("corpus_ref"),
  ontologyRef: text("ontology_ref"),
  verifier: text("verifier").notNull().default("lean-kernel"),
});

export const claims = pgTable("claims", {
  id: uuid("id").primaryKey().defaultRandom(),
  domainId: text("domain_id")
    .notNull()
    .references(() => domains.id, { onDelete: "cascade" }),
  statement: text("statement").notNull(),
  status: claimStatus("status").notNull(),
  evidenceRef: text("evidence_ref"),
});

export const submissions = pgTable("submissions", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .references(() => users.id, { onDelete: "cascade" }),
  domainId: text("domain_id").references(() => domains.id),
  statement: text("statement").notNull(),
  leanSource: text("lean_source"),
  // lifecycle state; the worker claim flips `queued` → `running` atomically (see submissions.ts).
  status: submissionStatus("status").notNull().default("queued"),
  // `workerId` is the claim token (only the claiming worker may finalize); `claimedAt` is the
  // lease start (a stale lease is re-claimable); `attemptCount` bounds retries.
  workerId: text("worker_id"),
  claimedAt: timestamp("claimed_at"),
  attemptCount: integer("attempt_count").notNull().default(0),
  // verdict is written by the Step-3 verification worker; null while queued/unrun.
  verdict: text("verdict"),
  log: text("log"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
