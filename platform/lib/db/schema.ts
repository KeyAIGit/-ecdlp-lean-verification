// Drizzle schema for the platform database (Step 2). Mirrors the data model in
// ../../PHASE2_PLAN.md. `domains` / `claims` are seeded from the repo's registry + corpus so
// the DB starts as a faithful copy of the git truth layer; `users` / `submissions` are the
// platform's own mutable state.

import {
  pgTable,
  pgEnum,
  uuid,
  text,
  timestamp,
} from "drizzle-orm/pg-core";

export const domainStatus = pgEnum("domain_status", [
  "live",
  "planned",
  "exploratory",
]);

export const claimStatus = pgEnum("claim_status", ["verified", "planned"]);

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
  // verdict is written by the Step-3 verification worker; null while queued/unrun.
  verdict: text("verdict"),
  log: text("log"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
