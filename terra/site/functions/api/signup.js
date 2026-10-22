// POST /api/signup — the evidence machine: waitlist signups land in KV with
// per-record validation, dedupe, honeypot and per-IP hourly rate limit.
// Optional NOTIFY_URL (e.g. an ntfy.sh topic) gets a push per signup so the
// founder's phone knows before the inbox does.
const json = (o, s = 200) => new Response(JSON.stringify(o),
  { status: s, headers: { "Content-Type": "application/json" } });

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const DISPOSABLE = ["mailinator.com","guerrillamail.com","tempmail.com","yopmail.com","10minutemail.com","trashmail.com"];

export async function onRequestPost(ctx) {
  const { env, request, waitUntil } = ctx;
  let b; try { b = await request.json(); } catch { return json({ error: "invalid_json" }, 400); }
  const email = String(b.email || "").trim().toLowerCase();
  const company = String(b.company || "").trim();
  const product = String(b.product || "").trim();

  // honeypot: bots fill it, humans never see it — accept & discard silently
  if (String(b.website || "").trim() !== "") return json({ ok: true, position: "—" });

  if (!EMAIL_RE.test(email)) return json({ error: "valid_work_email_required" }, 400);
  const dom = email.split("@")[1];
  if (DISPOSABLE.some(d => dom === d || dom.endsWith("." + d)))
    return json({ error: "disposable_email_not_accepted" }, 400);
  if (!company || !product) return json({ error: "company_and_product_required" }, 400);

  // per-IP hourly rate limit (5/h) — cheap abuse defense
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const hour = Math.floor(Date.now() / 3600000);
  const rlKey = `rl:${ip}:${hour}`;
  const n = parseInt(await env.SIGNUPS.get(rlKey) || "0", 10);
  if (n >= 5) return json({ error: "rate_limited_try_later" }, 429);
  await env.SIGNUPS.put(rlKey, String(n + 1), { expirationTtl: 3700 });  // awaited: no race under bursts

  // dedupe
  const key = `signup:${email}`;
  if (await env.SIGNUPS.get(key)) return json({ error: "duplicate" }, 409);

  const rec = { email, company, product,
    icp: String(b.icp || "").slice(0, 300), note: String(b.note || "").slice(0, 1000),
    at: new Date().toISOString(), ip_hash: await sha(ip) };
  await env.SIGNUPS.put(key, JSON.stringify(rec));

  // position = current count
  let count = 0, cursor;
  do {
    const page = await env.SIGNUPS.list({ prefix: "signup:", cursor, limit: 1000 });
    count += page.keys.length; cursor = page.cursor;
  } while (cursor);

  if (env.NOTIFY_URL) {
    waitUntil(fetch(env.NOTIFY_URL, { method: "POST",
      body: `🌱 CogOps Growth signup #${count}: ${company} <${email}> — ${product}${rec.icp ? " | ICP: " + rec.icp : ""}`
    }).catch(() => {}));
  }
  return json({ ok: true, position: count, company, product });
}

async function sha(s) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map(x => x.toString(16).padStart(2, "0")).join("").slice(0, 12);
}
