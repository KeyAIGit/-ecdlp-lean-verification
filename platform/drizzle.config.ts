import type { Config } from "drizzle-kit";

// `npx drizzle-kit push` (or `generate` + `migrate`) applies lib/db/schema.ts to the database
// pointed at by DATABASE_URL. See db/schema.sql for the plain-SQL equivalent.
export default {
  schema: "./lib/db/schema.ts",
  out: "./db/migrations",
  dialect: "postgresql",
  dbCredentials: { url: process.env.DATABASE_URL ?? "" },
} satisfies Config;
