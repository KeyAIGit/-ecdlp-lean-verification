import { NextResponse } from "next/server";
import { getDataSource } from "../../../lib/data";

// GET /api/stats — the canonical Lean counts (always from the repo's published truth layer).
export const revalidate = 3600;

export async function GET() {
  const ds = await getDataSource();
  return NextResponse.json(await ds.getStats());
}
