// frontend/pages/competitive.js
import { useEffect, useMemo, useState } from "react";

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
function pct(v) {
  const n = Number(v || 0);
  if (isNaN(n)) return "-";
  return `${n.toFixed(2)}%`;
}
function Arrow({ pctDelta }) {
  if (pctDelta === undefined || pctDelta === null) return null;
  const up = pctDelta >= 0;
  const color = up ? "#6aff8a" : "#ff6a6a";
  return <span style={{ color, marginLeft: 6, fontWeight: 600 }}>{up ? "▲" : "▼"} {Math.abs(pctDelta).toFixed(1)}%</span>;
}

export default function Competitive() {
  const [days, setDays] = useState(30);
  const [brands, setBrands] = useState([]);
  const [rows, setRows] = useState([]);
  const [primary, setPrimary] = useState("Crooks & Castles");
  const [cmpB, setCmpB] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [sortKey, setSortKey] = useState("net_sales");
  const [sortDir, setSortDir] = useState("desc");

  useEffect(() => {
    async function boot() {
      try {
        const bres = await fetch(`${API_BASE}/api/competitive/brands`);
        if (!bres.ok) throw new Error(`Brands HTTP ${bres.status}`);
        const bj = await bres.json();
        const list = bj.brands || [];
        setBrands(list);
        if (list.length && !list.find((x) => x.name === primary)) {
          setPrimary(list[0].name);
        }
      } catch (e) {
        setErr(String(e.message || e));
      }
    }
    boot();
  }, []);

  useEffect(() => {
    async function load() {
      setLoading(true); setErr("");
      try {
        const res = await fetch(`${API_BASE}/api/competitive/board?days=${days}&limit=30&primary=${encodeURIComponent(primary)}`);
        if (!res.ok) throw new Error(`Board HTTP ${res.status}`);
        const j = await res.json();
        setRows(j.rows || []);
        // pick default B brand
        const other = (j.rows || []).find((r) => r.brand !== j.primary);
        setCmpB(other?.brand || "");
      } catch (e) {
        setErr(String(e.message || e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [days, primary]);

  const sorted = useMemo(() => {
    const copy = [...rows];
    copy.sort((a, b) => {
      const va = a[sortKey] ?? 0;
      const vb = b[sortKey] ?? 0;
      return sortDir === "asc" ? va - vb : vb - va;
    });
    return copy;
  }, [rows, sortKey, sortDir]);

  const a = rows.find((r) => r.brand === primary);
  const b = rows.find((r) => r.brand === cmpB);

  function header(k, label) {
    const active = sortKey === k;
    return (
      <th
        onClick={() => {
          if (active) setSortDir(sortDir === "asc" ? "desc" : "asc");
          else { setSortKey(k); setSortDir("desc"); }
        }}
        style={{ cursor: "pointer", whiteSpace: "nowrap", padding: "10px 12px", borderBottom: "1px solid #2a2d31", textAlign: "right" }}
      >
        {label} {active ? (sortDir === "asc" ? "▲" : "▼") : ""}
      </th>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: 24 }}>
      <header style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <h1 style={{ margin: 0 }}>Competitive Intelligence</h1>

        <select
          value={primary}
          onChange={(e) => setPrimary(e.target.value)}
          style={{ background: "#15171a", color: "#e9edf2", border: "1px solid #2a2d31", padding: "8px 10px", borderRadius: 8 }}
        >
          {brands.map((b) => <option key={`a-${b.id || b.name}`} value={b.name}>{b.name}</option>)}
        </select>

        <span>vs</span>

        <select
          value={cmpB}
          onChange={(e) => setCmpB(e.target.value)}
          style={{ background: "#15171a", color: "#e9edf2", border: "1px solid #2a2d31", padding: "8px 10px", borderRadius: 8 }}
        >
          {brands.map((b) => <option key={`b-${b.id || b.name}`} value={b.name}>{b.name}</option>)}
        </select>

        <div style={{ marginLeft: "auto", display: "flex", gap: 8, background: "#15171a", border: "1px solid #2a2d31", borderRadius: 999, padding: 4 }}>
          <button onClick={() => setDays(7)}  style={pill(days === 7)}>7d</button>
          <button onClick={() => setDays(30)} style={pill(days === 30)}>30d</button>
        </div>
      </header>

      {err && <div style={{ marginTop: 12, padding: 12, borderRadius: 8, background: "#2a0f12", border: "1px solid #a33" }}>{err}</div>}

      {/* A vs B cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 12, marginTop: 12 }}>
        <CompareCard label={`Orders (${days}d)`} a={a?.orders} b={b?.orders} fmt={num} wowA={a?.wow?.orders?.pct} wowB={b?.wow?.orders?.pct} />
        <CompareCard label={`Net Sales (${days}d)`} a={a?.net_sales} b={b?.net_sales} fmt={dollars} wowA={a?.wow?.net_sales?.pct} wowB={b?.wow?.net_sales?.pct} />
        <CompareCard label={`AOV (${days}d)`} a={a?.aov} b={b?.aov} fmt={dollars} wowA={a?.wow?.aov?.pct} wowB={b?.wow?.aov?.pct} />
        <CompareCard label={`Conversion (${days}d)`} a={a?.conversion_pct} b={b?.conversion_pct} fmt={pct} wowA={a?.wow?.conversion_pct?.pct} wowB={b?.wow?.conversion_pct?.pct} />
        <CompareCard label={`Sessions (${days}d)`} a={a?.sessions} b={b?.sessions} fmt={num} wowA={a?.wow?.sessions?.pct} wowB={b?.wow?.sessions?.pct} />
        <CompareCard label={`Social Plays (${days}d)`} a={a?.plays} b={b?.plays} fmt={num} wowA={a?.wow?.plays?.pct} wowB={b?.wow?.plays?.pct} />
        <CompareCard label={`Social Likes (${days}d)`} a={a?.likes} b={b?.likes} fmt={num} wowA={a?.wow?.likes?.pct} wowB={b?.wow?.likes?.pct} />
        <CompareCard label={`Social Comments (${days}d)`} a={a?.comments} b={b?.comments} fmt={num} wowA={a?.wow?.comments?.pct} wowB={b?.wow?.comments?.pct} />
      </div>

      {/* Leaderboard */}
      <div style={{ marginTop: 18, background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead style={{ background: "#15171a" }}>
            <tr>
              <th style={{ textAlign: "left", padding: "10px 12px", borderBottom: "1px solid #2a2d31" }}>Brand</th>
              {header("orders", "Orders")}
              {header("net_sales", "Net Sales")}
              {header("aov", "AOV")}
              {header("conversion_pct", "Conversion")}
              {header("sessions", "Sessions")}
              {header("plays", "Plays")}
              {header("likes", "Likes")}
              {header("comments", "Comments")}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={9} style={{ padding: 16, color: "#98a4b3" }}>Loading…</td></tr>
            ) : (
              sorted.map((r) => (
                <tr key={r.brand} style={{ borderBottom: "1px solid #2a2d31" }}>
                  <td style={{ padding: "8px 12px" }}>{r.brand}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.orders)}<Arrow pctDelta={r?.wow?.orders?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{dollars(r.net_sales)}<Arrow pctDelta={r?.wow?.net_sales?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{dollars(r.aov)}<Arrow pctDelta={r?.wow?.aov?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{pct(r.conversion_pct)}<Arrow pctDelta={r?.wow?.conversion_pct?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.sessions)}<Arrow pctDelta={r?.wow?.sessions?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.plays)}<Arrow pctDelta={r?.wow?.plays?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.likes)}<Arrow pctDelta={r?.wow?.likes?.pct} /></td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.comments)}<Arrow pctDelta={r?.wow?.comments?.pct} /></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  function header(k, label) {
    const active = sortKey === k;
    return (
      <th
        onClick={() => {
          if (active) setSortDir(sortDir === "asc" ? "desc" : "asc");
          else { setSortKey(k); setSortDir("desc"); }
        }}
        style={{ cursor: "pointer", whiteSpace: "nowrap", padding: "10px 12px", borderBottom: "1px solid #2a2d31", textAlign: "right" }}
      >
        {label} {active ? (sortDir === "asc" ? "▲" : "▼") : ""}
      </th>
    );
  }
}

function pill(active) {
  return {
    padding: "6px 10px",
    borderRadius: 999,
    border: "none",
    background: active ? "#6aa6ff" : "transparent",
    color: active ? "#0a0b0d" : "#e9edf2",
    cursor: "pointer",
  };
}

function CompareCard({ label, a, b, fmt, wowA, wowB }) {
  const av = Number(a || 0), bv = Number(b || 0);
  const delta = av - bv;
  const dir = delta === 0 ? "eq" : delta > 0 ? "up" : "down";
  const color = dir === "eq" ? "#98a4b3" : dir === "up" ? "#6aff8a" : "#ff6a6a";
  return (
    <div style={{ background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 13, color: "#98a4b3" }}>{label}</div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, marginTop: 6 }}>
        <div><strong>Us:</strong> {fmt(av)}<Arrow pctDelta={wowA} /></div>
        <div><strong>Them:</strong> {fmt(bv)}<Arrow pctDelta={wowB} /></div>
        <div style={{ color }}>{delta === 0 ? "—" : (delta > 0 ? "▲ " : "▼ ") + fmt(Math.abs(delta))}</div>
      </div>
    </div>
  );
}
