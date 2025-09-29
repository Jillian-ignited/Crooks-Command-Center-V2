import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function ExecutivePage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  async function load(d = days) {
    setErr("");
    try {
      const res = await apiGet("/executive/overview", { query: { days: d } });
      setData(res);
    } catch (e) {
      setErr(e.message);
      setData(null);
    }
  }

  useEffect(() => { load(days); }, []); // on mount

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: "0 16px", fontFamily: "system-ui" }}>
      <h1>Executive Overview</h1>

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
