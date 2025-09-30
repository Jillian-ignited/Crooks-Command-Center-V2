// frontend/pages/summary.js
import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

function dollars(v) {
  const n = Number(v || 0);
  if (isNaN(n)) return "-";
  return n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}
function num(v) {
  const n = Number(v || 0);
  if (isNaN(n)) return "-";
  return n.toLocaleString();
}

export default function Summary() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/summary/overview`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const j = await res.json();
        setData(j);
      } catch (e) { setErr(String(e.message || e)); }
    })();
  }, []);

  const kpis = data?.kpis || data?.summary || {};
  const notes = data?.notes || [];

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: 24 }}>
      <h1 style={{ marginTop: 0 }}>Summary</h1>
      {err && <div style={{ margin: "12px 0", padding: 12, borderRadius: 8, background: "#2a0f12", border: "1px solid #a33" }}>{err}</div>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
        <Card label="Revenue" value={dollars(kpis.revenue)} />
        <Card label="Orders" value={num(kpis.orders)} />
        <Card label="AOV" value={dollars(kpis.aov)} />
        <Card label="Sessions" value={num(kpis.sessions)} />
      </div>
      <div style={{ marginTop: 18, background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 16 }}>
        <h3 style={{ marginTop: 0 }}>Highlights</h3>
        <ul style={{ margin: 0, paddingLeft: 16, lineHeight: 1.5 }}>
          {(notes.length ? notes : ["No highlights yet."]).map((n, i) => <li key={i}>{String(n)}</li>)}
        </ul>
      </div>
    </div>
  );
}

function Card({ label, value }) {
  return (
    <div style={{ background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 13, color: "#98a4b3" }}>{label}</div>
      <div style={{ fontSize: 24, marginTop: 6 }}>{value ?? "—"}</div>
    </div>
  );
}
