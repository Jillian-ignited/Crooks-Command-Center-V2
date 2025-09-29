import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

const RANGES = [
  {label:"7d", v:7},
  {label:"30d", v:30},
  {label:"60d", v:60},
  {label:"Qtr", v:90},
];

export default function CalendarPage(){
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [range, setRange] = useState(7);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function load(){
    setErr("");
    setLoading(true);
    try {
      const s = await apiGet("/calendar/status");
      setStatus(s);
    } catch(e){ setErr((p)=> (p?p+" | ":"") + `Status: ${e.message}`); }
    try {
      const ev = await apiGet(`/calendar/events?days=${range}`);
      setEvents(Array.isArray(ev)? ev : []);
    } catch(e){ setErr((p)=> (p?p+" | ":"") + `Events: ${e.message}`); }
    setLoading(false);
  }
  useEffect(()=>{ load(); /* eslint-disable-next-line */ },[range]);

  return (
    <main style={{maxWidth: 1000, margin:"40px auto", padding:20}}>
      <h1 style={{marginBottom: 12}}>Calendar</h1>

      {err && <div style={{background:"#fee", border:"1px solid #f99", padding:10, borderRadius:8, marginBottom:16}}>{err}</div>}

      <section style={card}>
        <div style={{display:"flex", gap:8, alignItems:"center", marginBottom:8}}>
          <strong>View:</strong>
          {RANGES.map(r => (
            <button key={r.v}
              onClick={()=>setRange(r.v)}
              style={{ ...chip, ...(range===r.v?chipActive:{}) }}
            >{r.label}</button>
          ))}
          <span style={{marginLeft:"auto", fontSize:12, color:"#666"}}>
            {status?.connected ? "Google connected" : "Google not connected"}
          </span>
        </div>

        {loading ? <p>Loading…</p> : (
          events.length ? (
            <ul style={{listStyle:"none", padding:0, margin:0}}>
              {events.map((e,i)=> (
                <li key={i} style={row}>
                  <div style={{width:160, color:"#555"}}>
                    {fmtDate(e.start)} – {fmtDate(e.end)}
                  </div>
                  <div style={{fontWeight:600}}>{e.title || "Untitled"}</div>
                  {e.location && <div style={{marginLeft:"auto", color:"#777"}}>{e.location}</div>}
                </li>
              ))}
            </ul>
          ) : <p>No events in range.</p>
        )}
      </section>

      <section style={card}>
        <h2 style={{marginTop:0}}>Culturally Relevant Drops & Moments</h2>
        <ul style={{margin:0, paddingLeft:18}}>
          <li>Streetwear collab calendar (Tentpole)</li>
          <li>Music festival dates (Audience overlap)</li>
          <li>Sneaker release windows (Traffic spikes)</li>
          <li>Creator content hooks (TikTok trends)</li>
        </ul>
        <p style={{color:"#666", fontSize:12, marginTop:8}}>
          (We’ll enrich this from your ingested datasets once available.)
        </p>
      </section>
    </main>
  );
}

function fmtDate(x){
  if(!x) return "—";
  const d = new Date(x);
  return d.toLocaleString();
}

const chip = { border:"1px solid #ddd", padding:"6px 10px", borderRadius:999, background:"#fff", cursor:"pointer" };
const chipActive = { borderColor:"#111", background:"#111", color:"#fff" };
const card = { background:"#fff", border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16, boxShadow:"0 1px 2px rgba(0,0,0,0.03)" };
const row = { display:"flex", gap:12, alignItems:"center", padding:"10px 0", borderBottom:"1px solid #f3f3f3" };
