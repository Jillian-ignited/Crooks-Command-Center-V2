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

export default function Competitive() {
  const [brands, setBrands] = useState([]);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cmpA, setCmpA] = useState("Crooks & Castles");
  const [cmpB, setCmpB] = useState("");
  const [sortKey, setSortKey] = useState("net_sales");
  const [sortDir, setSortDir] = useState("desc");
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const base = await fetch(`${API_BASE}/api/executive/overview`);
        const baseJson = await base.json();
        if (!base.ok || !baseJson.ok) throw new Error("Failed to load brands");
        const list = baseJson.brands || [];
        setBrands(list);

        // limit to ~30 brands for speed
        const sample = list.slice(0, 30);

        // pull 30d recaps for each brand
        const recaps = await Promise.all(
          sample.map(async (b) => {
            const res = await fetch(`${API_BASE}/api/executive/overview?brand=${encodeURIComponent(b.name)}`);
            const j = await res.json();
            const r30 = j?.recaps?.["30d"] || {};
            const s30 = j?.recaps?.social?.["30d"] || {};
            return {
              brand: b.name,
              orders: Number(r30.orders || 0),
              net_sales: Number(r30.net_sales || 0),
              aov: Number(r30.aov || 0),
              conversion_pct: Number(r30.conversion_pct || 0),
              sessions: Number(r30.sessions || 0),
              plays: Number(s30.plays || 0),
              likes: Number(s30.likes || 0),
              comments: Number(s30.comments || 0),
              refreshed_at: r30.refreshed_at || j?.snapshot?.last_import || null,
            };
          })
        );

        setRows(recaps);
        // pick a default competitor (first non-Crooks)
        const firstOther = recaps.find((r) => r.brand !== "Crooks & Castles");
        setCmpB(firstOther?.brand || recaps[0]?.brand || "");
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const sorted = useMemo(() => {
    const copy = [...rows];
    copy.sort((a, b) => {
      const va = a[sortKey] ?? 0;
      const vb = b[sortKey] ?? 0;
      return sortDir === "asc" ? va - vb : vb - va;
    });
    return copy;
  }, [rows, sortKey, sortDir]);

  const a = rows.find((r) => r.brand === cmpA);
  const b = rows.find((r) => r.brand === cmpB);

  function header(k, label) {
    const active = sortKey === k;
    return (
      <th
        onClick={() => {
          if (active) setSortDir(sortDir === "asc" ? "desc" : "asc");
          else {
            setSortKey(k);
            setSortDir("desc");
          }
        }}
        style={{ cursor: "pointer", whiteSpace: "nowrap", padding: "10px 12px", borderBottom: "1px solid #2a2d31", textAlign: "right" }}
      >
        {label} {active ? (sortDir === "asc" ? "▲" : "▼") : ""}
      </th>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: 24 }}>
      <h1 style={{ marginTop: 0 }}>Competitive Intelligence</h1>
      <p style={{ color: "#98a4b3", marginTop: -6 }}>30-day rollup across orders, sales, AOV, conversion, and social.</p>

      {error && (
        <div style={{ margin: "12px 0", padding: 12, borderRadius: 8, background: "#2a0f12", border: "1px solid #a33" }}>
          {error}
        </div>
      )}

      {/* Compare block */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center", marginTop: 8, padding: 12, background: "#121418", border: "1px solid #2a2d31", borderRadius: 12 }}>
        <strong>Compare</strong>
        <select
          value={cmpA}
          onChange={(e) => setCmpA(e.target.value)}
          style={{ background: "#15171a", color: "#e9edf2", border: "1px solid #2a2d31", padding: "8px 10px", borderRadius: 8, minWidth: 200 }}
        >
          {brands.map((b) => (
            <option key={`a-${b.id || b.name}`} value={b.name}>{b.name}</option>
          ))}
        </select>
        <span>vs</span>
        <select
          value={cmpB}
          onChange={(e) => setCmpB(e.target.value)}
          style={{ background: "#15171a", color: "#e9edf2", border: "1px solid #2a2d31", padding: "8px 10px", borderRadius: 8, minWidth: 200 }}
        >
          {brands.map((b) => (
            <option key={`b-${b.id || b.name}`} value={b.name}>{b.name}</option>
          ))}
        </select>

        <div style={{ marginLeft: "auto", color: "#98a4b3", fontSize: 13 }}>
          {a?.refreshed_at ? `Refreshed: ${a.refreshed_at}` : ""}
        </div>
      </div>

      {/* A vs B cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12, marginTop: 12 }}>
        <CompareCard label="Orders (30d)" a={a?.orders} b={b?.orders} fmt={num} />
        <CompareCard label="Net Sales (30d)" a={a?.net_sales} b={b?.net_sales} fmt={dollars} />
        <CompareCard label="AOV (30d)" a={a?.aov} b={b?.aov} fmt={dollars} />
        <CompareCard label="Conversion (30d)" a={a?.conversion_pct} b={b?.conversion_pct} fmt={pct} />
        <CompareCard label="Sessions (30d)" a={a?.sessions} b={b?.sessions} fmt={num} />
        <CompareCard label="Social Plays (30d)" a={a?.plays} b={b?.plays} fmt={num} />
        <CompareCard label="Social Likes (30d)" a={a?.likes} b={b?.likes} fmt={num} />
        <CompareCard label="Social Comments (30d)" a={a?.comments} b={b?.comments} fmt={num} />
      </div>

      {/* Leaderboard table */}
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
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.orders)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{dollars(r.net_sales)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{dollars(r.aov)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{pct(r.conversion_pct)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.sessions)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.plays)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.likes)}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>{num(r.comments)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CompareCard({ label, a, b, fmt }) {
  const av = Number(a || 0);
  const bv = Number(b || 0);
  const delta = av - bv;
  const dir = delta === 0 ? "eq" : delta > 0 ? "up" : "down";
  const color = dir === "eq" ? "#98a4b3" : dir === "up" ? "#6aff8a" : "#ff6a6a";
  return (
    <div style={{ background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 13, color: "#98a4b3" }}>{label}</div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, marginTop: 6 }}>
        <div><strong>Us:</strong> {fmt(av)}</div>
        <div><strong>Them:</strong> {fmt(bv)}</div>
        <div style={{ color }}>{delta === 0 ? "—" : (delta > 0 ? "▲ " : "▼ ") + fmt(Math.abs(delta))}</div>
      </div>
    </div>
  );
}
