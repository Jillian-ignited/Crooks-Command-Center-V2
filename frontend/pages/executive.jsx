import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function Executive() {
  const [kpis, setKpis] = useState(null);
  const [overview, setOverview] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setErr("");
    setLoading(true);
    try {
      const ov = await apiGet("/executive/overview?days=30");
      setOverview(ov);
    } catch(e){ setErr((p)=> (p?p+" | ":"") + `Overview: ${e.message}`); }
    try {
      const ks = await apiGet("/executive/kpis?days=30");
      setKpis(ks);
    } catch(e){ setErr((p)=> (p?p+" | ":"") + `KPIs: ${e.message}`); }
    setLoading(false);
  }

  useEffect(()=>{ load(); },[]);

  return (
    <main style={{maxWidth: 1100, margin:"40px auto", padding:20}}>
      <h1 style={{marginBottom: 12}}>Executive Dashboard</h1>

      {err && <div style={{background:"#fee", border:"1px solid #f99", padding:10, borderRadius:8, marginBottom:16}}>{err}</div>}

      <section style={row}>
        <MetricCard title="Revenue (30d)" value={kpis?.revenue_30d} hint={kpis?.revenue_delta} />
        <MetricCard title="Orders (30d)"  value={kpis?.orders_30d}  hint={kpis?.orders_delta} />
        <MetricCard title="AOV"           value={kpis?.aov}         hint={kpis?.aov_delta} />
        <MetricCard title="Engagement"    value={kpis?.engagement}  hint={kpis?.engagement_delta} />
      </section>

      <section style={card}>
        <h2 style={{marginTop:0}}>Signals</h2>
        {loading ? <p>Loading…</p> : (
          overview?.signals?.length ? (
            <ul style={{margin:0, paddingLeft:18}}>
              {overview.signals.map((s,i)=> <li key={i}>{s}</li>)}
            </ul>
          ) : <p>No signals.</p>
        )}
      </section>

      <section style={card}>
        <h2 style={{marginTop:0}}>Recommendations</h2>
        {loading ? <p>Loading…</p> : (
          overview?.recommendations?.length ? (
            <ol style={{margin:0, paddingLeft:18}}>
              {overview.recommendations.map((s,i)=> <li key={i}>{s}</li>)}
            </ol>
          ) : <p>No recommendations.</p>
        )}
      </section>
    </main>
  );
}

function MetricCard({ title, value, hint }) {
  return (
    <div style={metric}>
      <div style={{fontSize:12, color:"#666"}}>{title}</div>
      <div style={{fontSize:24, fontWeight:700}}>{value==null ? "—" : Number(value).toLocaleString()}</div>
      <div style={{fontSize:12, color:(hint??0)>=0?"#0a0":"#a00"}}>
        {hint==null ? "" : ((hint>=0?"+":"") + Number(hint).toFixed(1) + "%")}
      </div>
    </div>
  );
}

const row = { display:"grid", gridTemplateColumns:"repeat(4, 1fr)", gap:12, marginBottom:16 };
const metric = { background:"#fff", border:"1px solid #eee", borderRadius:12, padding:14, boxShadow:"0 1px 2px rgba(0,0,0,0.03)" };
const card = { background:"#fff", border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16, boxShadow:"0 1px 2px rgba(0,0,0,0.03)" };
