import { useEffect, useState, useCallback } from "react";
import IntelligencePanel from "../components/IntelligencePanel";

// Same-origin by default (since FastAPI serves the static UI). You can still override with env.
const API = process.env.NEXT_PUBLIC_API_BASE || "";

export default function IntelligencePage() {
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);

  async function refreshFiles() {
    const res = await fetch(`${API}/intelligence/uploads`);
    const json = await res.json();
    setFiles(json.files || []);
  }

  async function run() {
    setBusy(true);
    try {
      const body = { brands: brands.split(",").map(s=>s.trim()).filter(Boolean), lookback_days: Number(days) };
      const res = await fetch(`${API}/intelligence/report`, { method: "POST", headers: { "Content-Type":"application/json" }, body: JSON.stringify(body) });
      setData(await res.json());
    } finally {
      setBusy(false);
    }
  }

  async function upload(selected) {
    if (!selected || selected.length === 0) return;
    setBusy(true);
    try {
      const form = new FormData();
      for (const f of selected) form.append("files", f);
      const res = await fetch(`${API}/intelligence/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error("Upload failed");
      await refreshFiles();
    } finally {
      setBusy(false);
    }
  }

  async function remove(name) {
    setBusy(true);
    try {
      const res = await fetch(`${API}/intelligence/upload/${encodeURIComponent(name)}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      await refreshFiles();
    } finally {
      setBusy(false);
    }
  }

  // Drag & Drop handlers
  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer?.files?.length) {
      upload(e.dataTransfer.files);
    }
  }, []);
  const onDragOver = useCallback((e) => { e.preventDefault(); setDragOver(true); }, []);
  const onDragLeave = useCallback(() => setDragOver(false), []);

  useEffect(() => { refreshFiles(); }, []);

  return (
    <div className="grid">
      <div className="card">
        <h3 className="title">Upload Scraped Files (CSV/JSON)</h3>

        {/* Drag & Drop Zone */}
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          style={{
            border: "2px dashed #333",
            borderRadius: 12,
            padding: 20,
            background: dragOver ? "#0f1320" : "#0f1115",
            textAlign: "center",
            marginBottom: 10,
          }}
        >
          {dragOver ? "Release to upload…" : "Drag & drop files here"}
        </div>

        {/* Classic input as fallback */}
        <input type="file" multiple onChange={(e)=>upload(e.target.files)} />

        <div className="muted" style={{marginTop:8}}>
          Expected columns: brand, platform, date, likes, comments, shares, text, url
        </div>
      </div>

      <div className="card">
        <h3 className="title">Uploaded Files</h3>
        {files.length === 0 ? (
          <div className="muted">No files yet.</div>
        ) : (
          <ul>
            {files.map((f) => (
              <li key={f} className="row" style={{justifyContent:"space-between"}}>
                <span>{f}</span>
                <button className="button" onClick={()=>remove(f)} disabled={busy}>Delete</button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h3 className="title">Run Report</h3>
        <div className="row">
          <input style={{flex:1}} value={brands} onChange={e=>setBrands(e.target.value)} />
          <input type="number" min="1" max="60" value={days} onChange={e=>setDays(e.target.value)} style={{width:100}} />
          <button className="button" onClick={run} disabled={busy}>Run</button>
        </div>
      </div>

      <IntelligencePanel data={data} />
    </div>
  );
}
