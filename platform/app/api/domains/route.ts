import { NextResponse } from "next/server";
import { getDataSource } from "../../../lib/data";

// GET /api/domains          — the domain portfolio (DB when configured, else the static site).
// GET /api/domains?id=<id>  — that domain's claims.
export async function GET(req: Request) {
  const ds = await getDataSource();
  const id = new URL(req.url).searchParams.get("id");
  if (id) {
    return NextResponse.json(await ds.getClaims(id));
  }
  return NextResponse.json(await ds.getDomains());
}
