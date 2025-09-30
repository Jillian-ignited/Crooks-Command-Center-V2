// frontend/pages/executive.js
import { useEffect, useMemo, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

function num(n, opts = {}) {
  const v = Number(n || 0);
  if (isNaN(v)) return "-";
  return v.toLocaleString(undefined, { maximumFractionDigits: 2, ...opts });
}

function dollars(v) {
  const n = Number(v || 0);
  if (isNaN(n)) return "-";
  return n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function pct(v) {
  const n = Number(v || 0);
  if (isNaN(n)) return "-";
  return `${n.toFixed(2)}%`;
}

export default function Executive() {
  const [data, setData] = useState(null);
  const [brand, setBrand] = useState("Crooks & Castles");
  const [windowDays, setWindowDays] = useState(7);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function fetchOverview(b) {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/executive/overview?brand=${encodeURIComponent(b || brand)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      if (!json.ok) throw new Error("Bad payload");
      setData(json);
    } catch (e) {
      setError(`Failed to load executive overview: ${e.message}`);
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOverview(brand);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onRefresh() {
    setRefreshing(true);
    await fetchOverview(brand);
    setRefreshing(false);
  }

  const recap = useMemo(() => {
    if (!data) return null;
    return windowDays === 30 ? data.recaps["30d"] : data.recaps["7d"];
  }, [data, windowDays]);

  const socialRecap = useMemo(() => {
    if (!data) return null;
    return windowDays === 30 ? data.recaps.social["30d"] : data.recaps.social["7d"];
  }, [data, windowDays]);

  // Lightweight recommendations based on recaps
  const recommendations = useMemo(() => {
    if (!recap || !socialRecap) return [];
    const r = [];
    if (recap.conversion_pct < 1.2) {
      r.push("Conversion is under 1.2% — consider tightening paid traffic targeting and adding urgency on PDP/cart (low-lift: free-shipping threshold banner, low-stock badges).");
    }
    if (recap.aov < 100) {
      r.push("AOV is below $100 — test bundles or tiered discounts (e.g., ‘2 for $X’ or ‘Spend $150 get a free gift’).");
    }
    if (socialRecap.plays > 0 && (socialRecap.comments + socialRecap.saves) / socialRecap.plays < 0.02) {
      r.push("Social engagement per view is soft — iterate first 3 seconds of Reels/TikTok hooks and test creator-led cuts.");
    }
    if (recap.orders === 0 && recap.net_sales === 0) {
      r.push("No commerce signals in this window — verify Shopify exports are current and mapped (Orders/Sales).");
    }
    if (r.length === 0) r.push("KPIs look healthy — keep scaling top creatives, retest best offers with fresh product angles.");
    return r;
  }, [recap, socialRecap]);

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: 24 }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <h1 style={{ fontSize: 28, margin: 0 }}>Executive Overview</h1>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <select
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            style={{ background: "#15171a", color: "#e9edf2", border: "1px solid #2a2d31", padding: "8px 10px", borderRadius: 8 }}
          >
            {/* Populate from API once loaded */}
            {data?.brands?.length
              ? data.brands.map((b) => (
                  <option key={b.id || b.name} value={b.name}>
                    {b.name}
                  </option>
                ))
              : <option>Crooks & Castles</option>}
          </select>

          <div style={{ background: "#15171a", border: "1px solid #2a2d31", borderRadius: 999, padding: 4, display: "flex", gap: 4 }}>
            <button
              onClick={() => setWindowDays(7)}
              style={{
                padding: "6px 10px",
                borderRadius: 999,
                border: "none",
                background: windowDays === 7 ? "#6aa6ff" : "transparent",
                color: windowDays === 7 ? "#0a0b0d" : "#e9edf2",
                cursor: "pointer",
              }}
            >
              7d
            </button>
            <button
              onClick={() => setWindowDays(30)}
              style={{
                padding: "6px 10px",
                borderRadius: 999,
                border: "none",
                background: windowDays === 30 ? "#6aa6ff" : "transparent",
                color: windowDays === 30 ? "#0a0b0d" : "#e9edf2",
                cursor: "pointer",
              }}
            >
              30d
            </button>
          </div>

          <button
            onClick={async () => { await onRefresh(); }}
            disabled={refreshing}
            style={{
              background: refreshing ? "#2a2d31" : "#6aa6ff",
              color: refreshing ? "#8b96a3" : "#0a0b0d",
              border: "none",
              padding: "8px 12px",
              borderRadius: 8,
              cursor: refreshing ? "default" : "pointer",
            }}
            title="Re-fetch latest overview"
          >
            {refreshing ? "Refreshing…" : "Refresh"}
          </button>
        </div>
      </header>

      {error && (
        <div style={{ marginTop: 16, padding: 12, borderRadius: 8, background: "#2a0f12", border: "1px solid #a33" }}>
          {error}
        </div>
      )}

      <section style={{ marginTop: 16, opacity: loading ? 0.5 : 1, transition: "opacity .2s" }}>
        {/* KPI Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
          <KpiCard label={`Orders (${windowDays}d)`} value={num(recap?.orders)} />
          <KpiCard label={`Net Sales (${windowDays}d)`} value={dollars(recap?.net_sales)} />
          <KpiCard label={`AOV (${windowDays}d)`} value={dollars(recap?.aov)} />
          <KpiCard label={`Conversion (${windowDays}d)`} value={pct(recap?.conversion_pct)} />
          <KpiCard label={`Sessions (${windowDays}d)`} value={num(recap?.sessions)} />
          <KpiCard label={`Social Plays (${windowDays}d)`} value={num(socialRecap?.plays)} />
          <KpiCard label={`Social Likes (${windowDays}d)`} value={num(socialRecap?.likes)} />
          <KpiCard label={`Social Comments (${windowDays}d)`} value={num(socialRecap?.comments)} />
        </div>

        {/* Snapshot / freshness */}
        <div style={{ marginTop: 10, fontSize: 13, color: "#98a4b3" }}>
          <span>Last data date: {recap?.last_date || "—"}</span>
          <span style={{ marginLeft: 12 }}>Refreshed: {recap?.refreshed_at || data?.snapshot?.last_import || "—"}</span>
          <span style={{ marginLeft: 12 }}>Current: {recap?.current ? "Yes" : "—"}</span>
        </div>

        {/* Recommendations */}
        <div style={{ marginTop: 18, padding: 16, borderRadius: 12, background: "#121418", border: "1px solid #2a2d31" }}>
          <h3 style={{ marginTop: 0, marginBottom: 8 }}>Priorities & Recommendations</h3>
          <ul style={{ margin: 0, paddingLeft: 16, lineHeight: 1.5 }}>
            {recommendations.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>

        {/* Competitive intel teaser */}
        <div style={{ marginTop: 18, padding: 16, borderRadius: 12, background: "#121418", border: "1px solid #2a2d31" }}>
          <h3 style={{ marginTop: 0, marginBottom: 8 }}>Competitive Intelligence</h3>
          <p style={{ marginTop: 0 }}>
            Compare Crooks & Castles vs. tracked brands across Orders, Sales, AOV, Conversion, and Social at{" "}
            <a href="/competitive" style={{ color: "#6aa6ff", textDecoration: "underline" }}>
              /competitive
            </a>.
          </p>
          <MiniBrands brands={data?.brands || []} />
        </div>
      </section>
    </div>
  );
}

function KpiCard({ label, value }) {
  return (
    <div style={{ background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 13, color: "#98a4b3" }}>{label}</div>
      <div style={{ fontSize: 24, marginTop: 6 }}>{value ?? "—"}</div>
    </div>
  );
}

function MiniBrands({ brands }) {
  if (!brands?.length) return <div style={{ color: "#98a4b3" }}>No brands yet — upload intelligence or Shopify data.</div>;
  const top = brands.slice(0, 12);
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
      {top.map((b) => (
        <span key={b.id || b.name} style={{ padding: "6px 10px", borderRadius: 999, background: "#15171a", border: "1px solid #2a2d31" }}>
          {b.name}
        </span>
      ))}
    </div>
  );
}
