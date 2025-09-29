import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../lib/api";

export default function IntelligencePage() {
  const [brands, setBrands] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const b = await apiGet("/intelligence/brands");   // GET /api/intelligence/brands
      setBrands(Array.isArray(b) ? b : []);
    } catch (e) {
      setErr((prev) => (prev ? prev + " | " : "") + `Brands: ${e.message}`);
    }
    try {
      const s = await apiGet("/intelligence/summary");  // GET /api/intelligence/summary
      setSummary(s);
    } catch (e) {
      setErr((prev) => (prev ? prev + " | " : "") + `Summary: ${e.message}`);
    }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  return (
    <main style={{maxWidth: 1000, margin: "40px auto", padding: 20}}>
      <h1 style={{marginBottom: 12}}>Competitive Intelligence</h1>

      {err && <div style={{background:"#fee", border:"1px solid #f99", padding:10, borderRadius:8, marginBottom:16}}>{err}</div>}

      <section style={cardStyle}>
        <h2 style={h2}>Tracked Brands</h2>
        {loading ? <p>Loading…</p> : (
          <div style={{display:"flex", flexWrap:"wrap", gap:8}}>
            {brands.map((b) => (
              <span key={b} style={pill}>{b}</span>
            ))}
            {brands.length === 0 && <p>No brands configured.</p>}
          </div>
        )}
      </section>

      <section style={cardStyle}>
        <h2 style={h2}>Cross-Brand Snapshot</h2>
        {loading ? <p>Loading…</p> : (
          summary && summary.metrics?.length ? (
            <table style={table}>
              <thead>
                <tr>
                  <th style={th}>Brand</th>
                  <th style={th}>Posts</th>
                  <th style={th}>Engagement</th>
                  <th style={th}>Growth (30d)</th>
                </tr>
              </thead>
              <tbody>
                {summary.metrics.map(row => (
                  <tr key={row.brand}>
                    <td style={td}>{row.brand}</td>
                    <td style={td}>{fmt0(row.posts)}</td>
                    <td style={td}>{fmt0(row.engagement)}</td>
                    <td style={td}>{fmtPct(row.growth_30d)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p>No data yet. Try uploading a dataset on the Upload page and refresh.</p>
        )}
      </section>

      <section style={cardStyle}>
        <h2 style={h2}>Generate Report</h2>
        <button
          onClick={async () => {
            try {
              const r = await apiPost("/intelligence/report", { range: "30d" }); // if implemented
              alert("Report queued.");
            } catch (e) {
              alert(`Failed: ${e.message}`);
            }
          }}
          style={btn}
        >Run 30-day Report</button>
      </section>
    </main>
  );
}

const cardStyle = { background:"#fff", border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16, boxShadow:"0 1px 2px rgba(0,0,0,0.03)" };
const h2 = { margin:"0 0 8px 0" };
const pill = { background:"#f5f5f5", border:"1px solid #ddd", padding:"6px 10px", borderRadius:999 };
const table = { width:"100%", borderCollapse:"collapse" };
const th = { textAlign:"left", padding:"10px 8px", borderBottom:"1px solid #eee", background:"#fafafa" };
const td = { padding:"10px 8px", borderBottom:"1px solid #f3f3f3" };
const btn = { border:"1px solid #111", background:"#111", color:"#fff", padding:"10px 14px", borderRadius:10, cursor:"pointer" };

function fmt0(n){ return n==null ? "—" : Number(n).toLocaleString(); }
function fmtPct(n){ return n==null ? "—" : `${(Number(n)).toFixed(1)}%`; }
