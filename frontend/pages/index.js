import { useEffect, useState } from "react";
import ExecutiveSummaryCard from "../components/ExecutiveSummaryCard";
import IntelligencePanel from "../components/IntelligencePanel";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Home() {
  const [summary, setSummary] = useState(null);
  const [intel, setIntel] = useState(null);
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);

  async function runSummary() {
    const body = { brands: brands.split(",").map(s=>s.trim()).filter(Boolean), lookback_days: Number(days) };
    const res = await fetch(`${API}/summary`, { method: "POST", headers: { "Content-Type":"application/json" }, body: JSON.stringify(body) });
    setSummary(await res.json());
  }

  async function runIntel() {
    const body = { brands: brands.split(",").map(s=>s.trim()).filter(Boolean), lookback_days: Number(days) };
    const res = await fetch(`${API}/intelligence/report`, { method: "POST", headers: { "Content-Type":"application/json" }, body: JSON.stringify(body) });
    setIntel(await res.json());
  }

  useEffect(()=>{ /* noop */ },[]);

  return (
    <div className="grid">
      <div className="card">
        <h3 className="title">Controls</h3>
        <div className="row" style={{marginTop:8}}>
          <input style={{flex:1}} value={brands} onChange={e=>setBrands(e.target.value)} />
          <input type="number" min="1" max="60" value={days} onChange={e=>setDays(e.target.value)} style={{width:100}} />
          <button className="button" onClick={runSummary}>Run Summary</button>
          <button className="button" onClick={runIntel}>Run Intelligence</button>
        </div>
      </div>

      <ExecutiveSummaryCard report={summary} />
      <IntelligencePanel data={intel} />
    </div>
  );
}
