// GET /api/count — public signup count (the live counter on the landing page:
// evidence made visible, OS §9 "users pay the metric" applied to the funnel).
export async function onRequestGet(ctx) {
  let count = 0, cursor;
  do {
    const page = await ctx.env.SIGNUPS.list({ prefix: "signup:", cursor, limit: 1000 });
    count += page.keys.length; cursor = page.cursor;
  } while (cursor);
  return new Response(JSON.stringify({ count }),
    { headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=60" } });
}
