-- Plain-SQL equivalent of lib/db/schema.ts (Step 2). Apply with `psql "$DATABASE_URL" -f
-- db/schema.sql`, or use Drizzle Kit (`npx drizzle-kit push`). Idempotent-ish: uses IF NOT
-- EXISTS where Postgres allows it.

DO $$ BEGIN
  CREATE TYPE domain_status AS ENUM ('live', 'planned', 'exploratory');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
  CREATE TYPE claim_status AS ENUM ('verified', 'planned');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
  CREATE TYPE submission_status AS ENUM ('queued', 'running', 'done', 'failed');
EXCEPTION WHEN duplicate_object THEN null; END $$;
-- If the type pre-existed without 'failed' (earlier revision), add it. IF NOT EXISTS needs PG 12+.
ALTER TYPE submission_status ADD VALUE IF NOT EXISTS 'failed';

CREATE TABLE IF NOT EXISTS users (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_id    text NOT NULL UNIQUE,
  email       text,
  role        text NOT NULL DEFAULT 'member',
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domains (
  id           text PRIMARY KEY,               -- e.g. 'ecdlp-secp256k1'
  title        text NOT NULL,
  status       domain_status NOT NULL,
  one_liner    text,
  notes        text,
  corpus_ref   text,
  ontology_ref text,
  verifier     text NOT NULL DEFAULT 'lean-kernel'
);

CREATE TABLE IF NOT EXISTS claims (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_id    text NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
  statement    text NOT NULL,
  status       claim_status NOT NULL,
  evidence_ref text
);

CREATE TABLE IF NOT EXISTS submissions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  domain_id   text REFERENCES domains(id),
  statement   text NOT NULL,
  lean_source text,
  status      submission_status NOT NULL DEFAULT 'queued',  -- queued → running → done | failed
  worker_id   text,          -- claim token: only the holding worker may finalize
  claimed_at  timestamptz,   -- lease start; a stale lease is re-claimable
  attempt_count integer NOT NULL DEFAULT 0,
  verdict     text,          -- written by the Step-3 verification worker; null while unrun
  log         text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Migration for an already-existing submissions table (CREATE TABLE IF NOT EXISTS above is a
-- no-op then, so the new queue columns must be added explicitly). Idempotent.
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS status submission_status NOT NULL DEFAULT 'queued';
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS worker_id text;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS claimed_at timestamptz;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS attempt_count integer NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS claims_domain_id_idx ON claims(domain_id);
CREATE INDEX IF NOT EXISTS submissions_user_id_idx ON submissions(user_id);
-- Supports the atomic `FOR UPDATE SKIP LOCKED` queue claim (oldest eligible first).
CREATE INDEX IF NOT EXISTS submissions_queue_idx ON submissions(status, created_at);
