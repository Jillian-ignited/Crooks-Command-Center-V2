// Central API helper (JavaScript) for Next.js Pages Router
const BASE = process.env.NEXT_PUBLIC_API_BASE;

function buildUrl(path) {
  if (!BASE) throw new Error("Missing NEXT_PUBLIC_API_BASE");
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${normalized}`;
}

export async function api(path, init) {
  const url = buildUrl(path);
  const isFormData = init && init.body instanceof FormData;

  const headers = {};
  if (!isFormData) headers["Content-Type"] = "application/json";

  const res = await fetch(url, { ...(init || {}), headers: { ...headers, ...(init?.headers || {}) } });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status} ${res.statusText} @ ${url}\n${body}`);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export const apiGet = (path, init) => api(path, { method: "GET", ...(init || {}) });

export const apiPost = (path, body, init) =>
  api(path, {
    method: "POST",
    body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    ...(init || {}),
  });
