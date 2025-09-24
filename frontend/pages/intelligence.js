import { useState } from "react";
import IntelligencePanel from "../components/IntelligencePanel";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function IntelligencePage() {
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);

  async function run() {
    const body = { brands: brands.split(",").map(s=>s.trim()).filter(Boolean), lookback_days: Number(days) };
    const res = await fetch(`${API}/intelligence/report`, { method: "POST", headers: { "Content-Type":"application/json" }, body: JSON.stringify(body) });
    setData(await res.json());
  }

  async function upload(files) {
    const form = new FormData();
    for (const f of files) form.append("files", f);
    const res = await fetch(`${API}/intelligence/upload`, { method: "POST", body: form });
    const ack = await res.json();
    alert("Uploaded: " + ack.saved_files.join(", "));
  }

  return (
    <div className="grid">
      <div className="card">
        <h3 className="title">Upload Scraped Files (CSV/JSON)</h3>
        <input type="file" multiple onChange={e=>upload(e.target.files)} />
        <div className="muted" style={{marginTop:8}}>Expected columns: brand, platform, date, likes, comments, shares, text, url</div>
      </div>

      <div className="card">
        <h3 className="title">Run Report</h3>
        <div className="row">
          <input style={{flex:1}} value={brands} onChange={e=>setBrands(e.target.value)} />
          <input type="number" min="1" max="60" value={days} onChange={e=>setDays(e.target.value)} style={{width:100}} />
          <button className="button" onClick={run}>Run</button>
        </div>
      </div>

      <IntelligencePanel data={data} />
    </div>
  );
}
