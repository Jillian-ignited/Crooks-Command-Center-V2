import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function SummaryPage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  async function load(d = days) {
    setErr("");
    try {
      // backend/routers/summary.py exposes both /summary and /overview
      const res = await apiGet("/summary/overview", { query: { days: d } });
      setData(res);
    } catch (e) {
      setErr(e.message);
      setData(null);
    }
  }

  useEffect(() => { load(days); }, []);

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: "0 16px", fontFamily: "system-ui" }}>
      <h1>Summary</h1>

      <form onSubmit={(e)=>{e.preventDefault(); load(days);}} style={{display:"flex",gap:8,alignItems:"center",margin:"12px 0"}}>
        <label>Days</label>
        <input type="number" min="1" max="365" value={days} onChange={e=>setDays(Number(e.target.value||30))}/>
        <button type="submit">Refresh</button>
      </form>

      {err && <p style={{ color: "crimson" }}>{err}</p>}
      <pre style={{ whiteSpace: "pre-wrap", background: "#fafafa", padding: 12, borderRadius: 8 }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </main>
  );
}
