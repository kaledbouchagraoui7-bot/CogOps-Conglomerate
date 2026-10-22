// CogOps Vault gate — Pages advanced mode (_worker.js).
// Everything except /login and /api/* requires the vault_session cookie,
// whose value is HMAC-SHA256(VAULT_COOKIE_KEY, "vault-ok").
async function hmacHex(key, msg) {
  const k = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(key),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(msg));
  return [...new Uint8Array(s)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
async function sha256Hex(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/api/login") {
      if (request.method !== "POST") return new Response("method not allowed", { status: 405 });
      const form = await request.formData();
      const pw = String(form.get("password") || "");
      const hash = await sha256Hex(pw);
      if (!env.VAULT_PASS_HASH || hash !== env.VAULT_PASS_HASH) {
        return new Response("denied", { status: 401 });
      }
      const sig = await hmacHex(env.VAULT_COOKIE_KEY || "unset-key", "vault-ok");
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-store",
          "Set-Cookie": `vault_session=${sig}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=2592000`,
        },
      });
    }

    if (url.pathname === "/login") {
      const r = await env.ASSETS.fetch(request);
      return r;
    }

    const sig = await hmacHex(env.VAULT_COOKIE_KEY || "unset-key", "vault-ok");
    const m = (request.headers.get("Cookie") || "").match(/vault_session=([a-f0-9]+)/);
    if (m && m[1] === sig) {
      const r = await env.ASSETS.fetch(request);
      return r;
    }
    return Response.redirect(url.origin + "/login", 302);
  },
};
