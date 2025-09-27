// Minimal, resilient client for same-origin APIs.
// - Tries the path you pass first; if it fails, retries with `/api` prefix.
// - Never sets Content-Type for FormData (lets browser set multipart boundary).
// - JSON-safe parse, readable errors, and a hard timeout.

const DEFAULT_TIMEOUT_MS = 20000; // 20s

function withTimeout(ms = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort("Request timeout"), ms);
  return { signal: controller.signal, clear: () => clearTimeout(timer) };
}

async function parseResponse(res) {
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    try { return await res.json(); } catch { /* fall back to text */ }
  }
  return await res.text();
}

function normPath(path) {
  return path.startsWith("/") ? path : `/${path}`;
}

async function tryFetchOnce(path, init, timeoutMs) {
  const { signal, clear } = withTimeout(timeoutMs);
  try {
    const res = await fetch(path, { ...init, signal });
    const body = await parseResponse(res);
    return { res, body };
  } finally {
    clear();
  }
}

async function request(path, { method = "GET", body, headers = {}, timeoutMs } = {}) {
  const url = normPath(path);

  // Decide headers: JSON for plain objects/strings; none for FormData/Blob
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const isBlob = typeof Blob !== "undefined" && body instanceof Blob;
  const finalHeaders = { ...headers };
  let finalBody = body;

  if (!isFormData && !isBlob && body !== undefined && body !== null && typeof body !== "string") {
    finalHeaders["Content-Type"] = finalHeaders["Content-Type"] || "application/json";
    finalBody = JSON.stringify(body);
  }
  // For FormData, DO NOT set Content-Type manually.

  // 1) Try as given
  let { res, body: parsed } = await tryFetchOnce(url, { method, body: finalBody, headers: finalHeaders }, timeoutMs);
  if (res.ok) return parsed;

  // 2) If failed and path didn't start with /api, retry with /api prefix
  if (!url.startsWith("/api/")) {
    const prefixed = `/api${url}`;
    ({ res, body: parsed } = await tryFetchOnce(prefixed, { method, body: finalBody, headers: finalHeaders }, timeoutMs));
    if (res.ok) return parsed;
  }

  const text = typeof parsed === "string" ? parsed : JSON.stringify(parsed);
  const err = new Error(`HTTP ${res.status} ${res.statusText} @ ${url}${url.startsWith("/api/") ? "" : " (and /api fallback)"}\n${text}`);
  err.status = res.status;
  err.url = url;
  throw err;
}

// Primary API
export const api = {
  request,
  get: (path, opts) => request(path, { method: "GET", ...(opts || {}) }),
  post: (path, body, opts) => request(path, { method: "POST", body, ...(opts || {}) }),
  put: (path, body, opts) => request(path, { method: "PUT", body, ...(opts || {}) }),
  del: (path, opts) => request(path, { method: "DELETE", ...(opts || {}) }),

  // Health with dual fallback
  health: async () => {
    try { return await request("/api/health"); } catch { return await request("/health"); }
  },
};

// ---- Compatibility named exports (so existing pages keep working) ----
export const apiGet  = (path, opts) => api.get(path, opts);
export const apiPost = (path, body, opts) => api.post(path, body, opts);
export const apiPut  = (path, body, opts) => api.put(path, body, opts);
export const apiDel  = (path, opts) => api.del(path, opts);

export default api;
