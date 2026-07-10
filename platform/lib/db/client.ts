// Drizzle client over a Neon serverless Postgres connection (works on Vercel/edge and Node).
// Any Postgres works — swap the driver if you host elsewhere. Only imported when
// DATABASE_URL is set (see ../data.ts), so the pg driver is never bundled for Step 1.

import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "./schema";

const url = process.env.DATABASE_URL;
if (!url) {
  throw new Error("DATABASE_URL is not set (the db backend requires it).");
}

export const db = drizzle(neon(url), { schema });
