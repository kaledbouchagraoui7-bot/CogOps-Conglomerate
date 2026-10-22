// Vault gate: everything except /login and /api/* requires the session cookie.
// Cookie value = HMAC-SHA256(VAULT_COOKIE_KEY, "vault-ok") — computed identically in api/login.ts.
export const onRequest: PagesFunction = async (ctx) => {
  const url = new URL(ctx.request.url);
  if (url.pathname === "/login" || url.pathname.startsWith("/api/")) {
    return ctx.next();
  }
  const env: any = ctx.env;
  const key = env.VAULT_COOKIE_KEY || "unset-key";
  const sig = await hmacHex(key, "vault-ok");
  const m = (ctx.request.headers.get("Cookie") || "").match(/vault_session=([a-f0-9]+)/);
  if (m && m[1] === sig) return ctx.next();
  return Response.redirect(url.origin + "/login", 302);
};

async function hmacHex(key: string, msg: string): Promise<string> {
  const k = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(key),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(msg));
  return [...new Uint8Array(s)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
