// frontend/pages/intelligence.js
import { useState } from "react";

export default function Intelligence() {
  const [file, setFile] = useState(null);
  const [brand, setBrand] = useState("");
  const [source, setSource] = useState("shopify"); // default since you're uploading Shopify
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;

    const params = new URLSearchParams();
    params.set("parse", "true");
    if (source) params.set("source", source);
    if (brand) params.set("brand", brand);

    const formData = new FormData();
    formData.append("file", file); // backend expects 'file'

    try {
      setStatus("Uploading…");
      const res = await fetch(`/api/intelligence/upload?${params.toString()}`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok || data?.ok === false) throw new Error(data?.detail || `HTTP ${res.status}`);
      setResult(data);
      setStatus("Upload successful ✅");
    } catch (err) {
      console.error(err);
      setStatus(`Error: ${err.message}`);
      setResult(null);
    }
  }

  const prettySize = (n) => {
    if (!n && n !== 0) return "";
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n/1024).toFixed(1)} KB`;
    return `${(n/1024/1024).toFixed(2)} MB`;
  };
  const prettyDateTime = (s) => {
    if (!s) return "";
    const d = new Date(s);
    if (isNaN(d.getTime())) return s; // avoid "Invalid Date"
    return d.toLocaleString();
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Intelligence Upload</h1>

      <form onSubmit={handleUpload} style={{ display: "grid", gap: 12, maxWidth: 520 }}>
        <label>
          Source
          <select value={source} onChange={(e) => setSource(e.target.value)} style={{ marginLeft: 8 }}>
            <option value="shopify">Shopify</option>
            <option value="auto">Auto-detect</option>
            <option value="">(Generic)</option>
          </select>
        </label>

        <label>
          Brand (for benchmarks)
          <input value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="e.g., Crooks & Castles" />
        </label>

        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button type="submit">Upload</button>
      </form>

      <p style={{ marginTop: 12 }}>{status}</p>

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Result</h3>
          <ul>
            <li>File: {result.filename}</li>
            <li>Size: {prettySize(result.size)}</li> {/* ← uses API value, not local file state */}
            <li>Processed: {prettyDateTime(result?.import?.last_import)}</li>
          </ul>

          <details style={{ marginTop: 12 }}>
            <summary>Full Response</summary>
            <pre style={{ background: "#111", color: "#0f0", padding: 12 }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
