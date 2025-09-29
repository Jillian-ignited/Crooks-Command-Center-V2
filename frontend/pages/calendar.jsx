import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function CalendarPage(){
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState(null);
  const [err, setErr] = useState("");

  async function load(){
    setErr("");
    try {
      const s = await apiGet("/calendar/status");
      setStatus(s);
    } catch(e){ setErr(`Status: ${e.message}`); }
    try {
      const ev = await apiGet("/calendar/events");
      setEvents(ev);
    } catch(e){ setErr(prev => (prev ? prev + " | " : "") + `Events: ${e.message}`); }
  }
  useEffect(()=>{ load(); },[]);

  return (
    <main style={{maxWidth:900,margin:"40px auto",padding:"0 16px",fontFamily:"system-ui"}}>
      <h1>Calendar</h1>
      {err && <p style={{color:"crimson"}}>{err}</p>}
      <section style={{margin:"16px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Status</h2>
        <pre style={{whiteSpace:"pre-wrap",background:"#fafafa",padding:12,borderRadius:8}}>
          {JSON.stringify(status,null,2)}
        </pre>
      </section>
      <section style={{margin:"16px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Events (7-day window)</h2>
        <pre style={{whiteSpace:"pre-wrap",background:"#fafafa",padding:12,borderRadius:8}}>
          {JSON.stringify(events,null,2)}
        </pre>
      </section>
    </main>
  );
}
