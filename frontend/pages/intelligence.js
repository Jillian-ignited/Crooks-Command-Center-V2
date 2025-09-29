// frontend/pages/intelligence.js
import { useEffect, useMemo, useState } from "react";
import { apiGet } from "../lib/api";

const DEFAULT_DAYS = 30;

export default function IntelligencePage() {
  const [brands, setBrands] = useState([]);        // all available brands from API
  const [selected, setSelected] = useState("all"); // CSV or "all"
  const [days, setDays] = useState(DEFAULT_DAYS);
  const [data, setData] = useState(null);          // summary payload
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadBrands() {
    try {
      const res = await apiGet("/intelligence/brands");
      setBrands(res.brands || []);
    } catch (e) {
      setErr(`Brands: ${e.message}`);
    }
  }

  async function loadSummary({ brandsCSV = selected, windowDays = days } = {}) {
    setLoading(true); setErr("");
    try {
      const res = await apiGet("/intelligence/summary", {
        query: { brands: (brandsCSV || "all"), days: windowDays }
      });
      setData(res);
    } catch (e) {
      setErr(`Summary: ${e.message}`);
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadBrands(); }, []);
  useEffect(() => { loadSummary({}); }, []); // initial

  const tableRows = useMemo(() => {
    if (!data?.metrics) return [];
    const keys = Object.keys(data.metrics);
    return keys.map((b) => ({ brand: b, ...data.metrics[b] }));
  }, [data]);

  function onApply(e) {
    e.preventDefault();
    loadSummary({});
  }

  return (
    <main style={{ maxWidth: 1100, margin: "40px auto", padding: "0 16px", fontFamily: "system-ui" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Competitive Intelligence</h1>
        <button onClick={() => loadSummary({})} disabled={loading} style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff" }}>
          {loading ? "Loading…" : "Refresh"}
        </button>
      </header>

      {err && <p style={{ color: "crimson", marginTop: 12 }}>{err}</p>}

      {/* Controls */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <form onSubmit={onApply} style={{ display: "grid", gridTemplateColumns: "1fr 140px 120px", gap: 12 }}>
          <div>
            <label style={{ display: "block", fontSize: 12, opacity: 0.8, marginBottom: 4 }}>Brands (CSV or “all”)</label>
            <input
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              placeholder='e.g., Crooks & Castles, Hellstar, LRG or "all"'
              style={{ width: "100%", padding: "8px 10px", borderRadius: 8, border: "1px solid #ddd" }}
            />
            {!!brands.length && (
              <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>
                Available: {brands.slice(0, 8).join(", ")}{brands.length > 8 ? "…" : ""}
              </div>
            )}
          </div>

          <div>
            <label style={{ display: "block", fontSize: 12, opacity: 0.8, marginBottom: 4 }}>Days</label>
            <input
              type="number" min="1" max="365" value={days}
              onChange={(e) => setDays(Number(e.target.value || DEFAULT_DAYS))}
              style={{ width: "100%", padding: "8px 10px", borderRadius: 8, border: "1px solid #ddd" }}
            />
          </div>

          <div style={{ display: "flex", alignItems: "end" }}>
            <button type="submit" disabled={loading} style={{ width: "100%", padding: "10px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff" }}>
              Apply
            </button>
          </div>
        </form>
      </section>

      {/* Headline */}
      <section style={{ marginTop: 16 }}>
        <div style={{ fontSize: 13, opacity: 0.75 }}>
          Window: {data?.window_days ?? days}d · Updated: {data?.last_updated ? new Date(data.last_updated).toLocaleString() : "—"}
        </div>
      </section>

      {/* Ranking */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Top 10 by Engagement</h2>
        {!data?.ranking?.length && <p style={{ opacity: 0.7 }}>No data yet.</p>}
        {!!data?.ranking?.length && (
          <ol style={{ margin: 0, paddingLeft: 18 }}>
            {data.ranking.map((r, i) => (
              <li key={i} style={{ margin: "6px 0" }}>
                <strong>{r.brand}</strong> — {r.total_engagement.toLocaleString()} total engagement
              </li>
            ))}
          </ol>
        )}
      </section>

      {/* Table */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Brand Metrics</h2>
        {!tableRows.length && <p style={{ opacity: 0.7 }}>No metrics to display.</p>}
        {!!tableRows.length && (
          <div style={{ overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse", width: "100%" }}>
              <thead>
                <tr style={{ background: "#fafafa" }}>
                  {["Brand","Posts","Avg Likes","Avg Comments","Avg Engagement","Total Engagement","Follower Growth"].map(h => (
                    <th key={h} style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: "8px 6px", fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableRows.map((row) => (
                  <tr key={row.brand}>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px", fontWeight: 600 }}>{row.brand}</td>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px" }}>{row.posts}</td>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px" }}>{row.avg_likes}</td>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px" }}>{row.avg_comments}</td>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px" }}>{row.avg_engagement}</td>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px" }}>{row.total_engagement?.toLocaleString?.() ?? row.total_engagement}</td>
                    <td style={{ borderBottom: "1px solid #f2f2f2", padding: "8px 6px" }}>
                      {(row.follower_growth_rate * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
