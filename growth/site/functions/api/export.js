// GET /api/export — admin-only CSV/JSON export of signups (x-admin-token must
// equal the ADMIN_TOKEN secret). This is the "hand-over to delivery" door:
// export → run the enrichment engine → deliver sample batches.
export async function onRequestGet(ctx) {
  const { env, request } = ctx;
  const tok = request.headers.get("x-admin-token") || "";
  if (!env.ADMIN_TOKEN || tok !== env.ADMIN_TOKEN)
    return new Response(JSON.stringify({ error: "forbidden" }), { status: 403,
      headers: { "Content-Type": "application/json" } });

  const recs = [];
  let cursor;
  do {
    const page = await env.SIGNUPS.list({ prefix: "signup:", cursor, limit: 1000 });
    for (const k of page.keys) {
      try { recs.push(JSON.parse(await env.SIGNUPS.get(k.name))); } catch { /* skip */ }
    }
    cursor = page.cursor;
  } while (cursor);
  recs.sort((a, b) => (a.at || "").localeCompare(b.at || ""));

  const fmt = new URL(request.url).searchParams.get("format");
  if (fmt === "csv") {
    const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const csv = ["email,company,product,icp,note,at",
      ...recs.map(r => [r.email, r.company, r.product, r.icp, r.note, r.at].map(esc).join(","))].join("\n");
    return new Response(csv, { headers: { "Content-Type": "text/csv",
      "Content-Disposition": 'attachment; filename="cogops-growth-signups.csv"' } });
  }
  return new Response(JSON.stringify({ count: recs.length, signups: recs }, null, 1),
    { headers: { "Content-Type": "application/json" } });
}
