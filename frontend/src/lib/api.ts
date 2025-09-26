// Central API helper that supports JSON and FormData without breaking uploads.
// Import path options:
//   import { apiGet, apiPost } from "@/lib/api";   // if tsconfig has "@" path alias
//   // or
//   import { apiGet, apiPost } from "../lib/api";  // relative import
//
const BASE = process.env.NEXT_PUBLIC_API_BASE;

function buildUrl(path: string) {
  if (!BASE) throw new Error("Missing NEXT_PUBLIC_API_BASE");
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${normalized}`;
}

export async function api(path: string, init?: RequestInit) {
  const url = buildUrl(path);
  const isFormData = init?.body instanceof FormData;

  const headers: Record<string, string> = {};
  if (!isFormData) headers["Content-Type"] = "application/json";

  const res = await fetch(url, { ...init, headers: { ...headers, ...(init?.headers || {}) } });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status} ${res.statusText} @ ${url}\n${body}`);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export const apiGet = (path: string, init?: RequestInit) =>
  api(path, { method: "GET", ...(init || {}) });

export const apiPost = (path: string, body?: any, init?: RequestInit) =>
  api(path, {
    method: "POST",
    body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    ...(init || {}),
  });

export const apiPut = (path: string, body?: any, init?: RequestInit) =>
  api(path, {
    method: "PUT",
    body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    ...(init || {}),
  });

export const apiDelete = (path: string, init?: RequestInit) =>
  api(path, { method: "DELETE", ...(init || {}) });
