export async function onRequestGet(ctx) {
  const env = ctx.env;
  const cap = parseInt(env.SAMPLE_CAP || "5", 10);
  const wk = (() => { const d = new Date(); const day = (d.getUTCDay() + 6) % 7;
    d.setUTCDate(d.getUTCDate() - day); return d.toISOString().slice(0, 10); })();
  let count = 0, weekUsed = 0, cursor;
  try {
    do {
      const page = await env.SIGNUPS.list({ prefix: "signup:", cursor, limit: 1000 });
      for (const k of page.keys) {
        count++;
        try {
          const v = await env.SIGNUPS.get(k.name);
          if (v && JSON.parse(v).at && String(JSON.parse(v).at).slice(0, 10) >= wk) weekUsed++;
        } catch (e) {}
      }
      cursor = page.cursor;
    } while (cursor);
  } catch (e) {}
  return new Response(JSON.stringify({
    count, week_used: weekUsed, slots_left: Math.max(0, cap - weekUsed), week: wk,
  }), { headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
