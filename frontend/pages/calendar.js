import { useEffect, useState } from "react";
import CalendarView from "../components/CalendarView";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function CalendarPage() {
  const [range, setRange] = useState(60);
  const [data, setData] = useState(null);

  async function load() {
    const res = await fetch(`${API}/calendar?range_days=${range}`);
    setData(await res.json());
  }
  useEffect(()=>{ load(); }, [range]);

  return (
    <div className="grid">
      <div className="card">
        <h3 className="title">Calendar Range</h3>
        <div className="row">
          <input type="number" min="1" max="120" value={range} onChange={e=>setRange(e.target.value)} />
          <button className="button" onClick={()=>load()}>Refresh</button>
        </div>
      </div>
      <CalendarView data={data} />
    </div>
  );
}
