import { useState } from "react";
import ExecutiveSummaryCard from "../components/ExecutiveSummaryCard";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function SummaryPage() {
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);
  const [report, setReport] = useState(null);

  async function run() {
    const body = { brands: brands.split(",").map(s=>s.trim()).filter(Boolean), lookback_days: Number(days) };
    const res = await fetch(`${API}/summary`, { method: "POST", headers: { "Content-Type":"application/json" }, body: JSON.stringify(body) });
    setReport(await res.json());
  }

  return (
    <div className="grid">
      <div className="card">
        <h3 className="title">Generate Executive Summary</h3>
        <div className="row">
          <input style={{flex:1}} value={brands} onChange={e=>setBrands(e.target.value)} />
          <input type="number" min="1" max="60" value={days} onChange={e=>setDays(e.target.value)} style={{width:100}} />
          <button className="button" onClick={run}>Run</button>
        </div>
      </div>
      <ExecutiveSummaryCard report={report} />
    </div>
  );
}
