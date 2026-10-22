// POST /api/login  body: URLSearchParams {password}
// 200 + Set-Cookie when sha256(password) === VAULT_PASS_HASH, else 401.
export const onRequestPost: PagesFunction = async (ctx) => {
  const env: any = ctx.env;
  const form = await ctx.request.formData();
  const pw = String(form.get("password") || "");
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(pw));
  const hash = [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  if (!env.VAULT_PASS_HASH || hash !== env.VAULT_PASS_HASH) {
    return new Response("denied", { status: 401 });
  }
  const k = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(env.VAULT_COOKIE_KEY || "unset-key"),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sigBuf = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode("vault-ok"));
  const sig = [...new Uint8Array(sigBuf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Set-Cookie": `vault_session=${sig}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=2592000`,
      "Cache-Control": "no-store",
    },
  });
};

export const onRequestGet: PagesFunction = () => new Response("method not allowed", { status: 405 });
