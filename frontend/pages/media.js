// frontend/pages/media.js
import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Media() {
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  async function load() {
    const res = await fetch(`${API_BASE}/api/media/assets`);
    const j = await res.json();
    setItems(j.assets || j || []); // support either shape
  }

  useEffect(() => { load(); }, []);

  async function onUpload(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    setBusy(true); setMsg("");
    try {
      const fd = new FormData();
      fd.append("file", f);
      const res = await fetch(`${API_BASE}/api/media/upload`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(`Upload failed: HTTP ${res.status}`);
      await load();
      setMsg("Uploaded!");
    } catch (err) {
      setMsg(String(err.message || err));
    } finally { setBusy(false); }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: 24 }}>
      <h1>Media Library</h1>
      <div style={{ margin: "12px 0" }}>
        <input
          type="file"
          onChange={onUpload}
          disabled={busy}
          style={{ background: "#15171a", color: "#e9edf2", border: "1px solid #2a2d31", padding: 8, borderRadius: 8 }}
        />
        <span style={{ marginLeft: 12, color: "#98a4b3" }}>{busy ? "Uploading…" : msg}</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 12 }}>
        {items.map((it, i) => (
          <div key={i} style={{ background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 12 }}>
            <div style={{ fontSize: 13, color: "#98a4b3" }}>{it.filename || it.name || "Asset"}</div>
            {it.url ? (
              <a href={it.url} target="_blank" rel="noreferrer" style={{ color: "#6aa6ff" }}>Open</a>
            ) : (
              <div style={{ color: "#98a4b3" }}>No URL</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
