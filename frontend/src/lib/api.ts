// Centralized API helper for the frontend (Next.js/React)
// Usage:
//   import { apiGet, apiPost } from "@/lib/api";
//   const data = await apiGet("/health");

const BASE = process.env.NEXT_PUBLIC_API_BASE;

function buildUrl(path: string) {
  if (!BASE) {
    throw new Error("Missing NEXT_PUBLIC_API_BASE. Set it in your env.");
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${normalized}`;
}

export async function api(path: string, init?: RequestInit) {
  const url = buildUrl(path);
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.text();
    // Surface meaningful errors for quick diagnosis
    throw new Error(`API ${res.status} ${res.statusText} @ ${url}\n${body}`);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

export async function apiGet(path: string, init?: RequestInit) {
  return api(path, { method: "GET", ...(init || {}) });
}

export async function apiPost(path: string, body?: unknown, init?: RequestInit) {
  return api(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
    ...(init || {}),
  });
}

export async function apiPut(path: string, body?: unknown, init?: RequestInit) {
  return api(path, {
    method: "PUT",
    body: body === undefined ? undefined : JSON.stringify(body),
    ...(init || {}),
  });
}

export async function apiDelete(path: string, init?: RequestInit) {
  return api(path, { method: "DELETE", ...(init || {}) });
}
