// frontend/lib/api.js
const API_BASE = "/api";
const collapse = (p) => ("/" + String(p || "").replace(/^\/+/, "")).replace(/\/{2,}/g, "/");

async function request(path, { method="GET", body, headers={} } = {}) {
  const url = API_BASE + collapse(path);
  const isFD = typeof FormData !== "undefined" && body instanceof FormData;
  const isBlob = typeof Blob !== "undefined" && body instanceof Blob;

  const hdrs = { ...headers };
  let payload = body;
  if (payload != null && !isFD && !isBlob && typeof payload !== "string") {
    hdrs["Content-Type"] = hdrs["Content-Type"] || "application/json";
    payload = JSON.stringify(payload);
  }

  const res = await fetch(url, { method, headers: isFD || isBlob ? undefined : hdrs, body: payload });
  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    const msg = typeof data === "string" ? data : JSON.stringify(data);
    throw new Error(`HTTP ${res.status} @ ${url}\n${msg}`);
  }
  return data;
}

export const apiGet  = (p, o) => request(p, { method: "GET", ...(o||{}) });
export const apiPost = (p, b, o) => request(p, { method: "POST", body: b, ...(o||{}) });
export const apiPut  = (p, b, o) => request(p, { method: "PUT",  body: b, ...(o||{}) });
export const apiDel  = (p, o) => request(p, { method: "DELETE", ...(o||{}) });
export default { apiGet, apiPost, apiPut, apiDel };
