// frontend/lib/api.js
const API_BASE = "/api";

const collapse = (p) =>
  ("/" + String(p || "").replace(/^\/+/, "")).replace(/\/{2,}/g, "/");

function withQuery(path, query) {
  if (!query || typeof query !== "object" || Array.isArray(query)) return path;
  const entries = Object.entries(query)
    .filter(([_, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => [k, Array.isArray(v) ? v : [v]])
    .flatMap(([k, arr]) => arr.map((val) => [k, String(val)]));
  if (!entries.length) return path;
  const usp = new URLSearchParams(entries);
  return path + (path.includes("?") ? "&" : "?") + usp.toString();
}

async function request(path, { method = "GET", body, headers = {}, query } = {}) {
  const urlPath = withQuery(API_BASE + collapse(path), query);

  const isFD = typeof FormData !== "undefined" && body instanceof FormData;
  const isBlob = typeof Blob !== "undefined" && body instanceof Blob;

  const hdrs = { ...headers };
  let payload = body;

  if (payload != null && !isFD && !isBlob && typeof payload !== "string") {
    hdrs["Content-Type"] = hdrs["Content-Type"] || "application/json";
    payload = JSON.stringify(payload);
  }

  const res = await fetch(urlPath, {
    method,
    headers: isFD || isBlob ? undefined : hdrs,
    body: payload,
  });

  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : await res.text();

  if (!res.ok) {
    const msg = typeof data === "string" ? data : JSON.stringify(data);
    throw new Error(`HTTP ${res.status} @ ${urlPath}\n${msg}`);
  }
  return data;
}

export const apiGet  = (p, o)      => request(p, { method: "GET", ...(o || {}) });
export const apiPost = (p, body, o)=> request(p, { method: "POST", body, ...(o || {}) });
export const apiPut  = (p, body, o)=> request(p, { method: "PUT",  body, ...(o || {}) });
export const apiDel  = (p, o)      => request(p, { method: "DELETE", ...(o || {}) });

export default { apiGet, apiPost, apiPut, apiDel };
