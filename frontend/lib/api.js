// Minimal, resilient client for same-origin APIs.
// - Tries the path you pass first; if 404, retries with `/api` prefix.
// - Never sets Content-Type for FormData (lets browser set multipart boundary).
// - JSON-safe parse, good error messages, and a hard timeout.
//
// Usage:
//   import { api } from "../lib/api";
//   const data = await api.get("/intelligence/summary?brands=all");
//   const fd = new FormData(); fd.append("file", file); await api.post("/intelligence/upload", fd);

const DEFAULT_TIMEOUT_MS = 20000; // 20s

function withTimeout(ms = DEFAULT_TIMEOUT_MS) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort("Request timeout"), ms);
  return { signal: c.signal, clear: () => clearTimeout(t) };
}

async function parseResponse(res) {
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    try { return await res.json(); } catch { /* fallthrough */ }
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

  // Decide headers: JSON for plain objects/strings, none for FormData/Blob
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const isBlob = type
