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
function Arrow({ deltaPct }) {
  if (deltaPct === undefined || deltaPct === null) return null;
  const up = deltaPct >= 0;
  const color = up ? "#6aff8a" : "#ff6a6a";
  const label = `${up ? "▲" : "▼"} ${Math.abs(deltaPct).toFixed(1)}%`;
  return <span style={{ marginLeft: 8, color, fontWeight: 600 }}>{label}</span>;
}

export default function Executive() {
  const [data, setData] = useState(null);
  const [brand, setBrand] = useState("Crooks & Castles");
  const [windowDays, setWindowDays] = useState(7);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function fetchOverview(b) {
    setError("");
    setLoading(true);
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

  useEffect(() => { fetchOverview(brand); /* eslint-disable-next-line */ }, []);

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

  // Rec rules (for tooltips)
  const REC_RULES = [
    { id: "low_conv", check: (r) => (r?.conversion_pct ?? 0) < 1.2, why: "Conversion < 1.2%. Benchmarks for streetwear DTC often 1.5–3%." },
    { id: "low_aov", check: (r) => (r?.aov ?? 0) < 100, why: "AOV < $100. Bundles / threshold promos can lift AOV quickly." },
    { id: "weak_eng", check: (_, s) => {
        const plays = Number(s?.plays || 0);
        const eng = plays ? (Number(s?.comments || 0) + Number(s?.saves || 0)) / plays : 0;
        return plays > 0 && eng < 0.02;
      }, why: "Engagement per view < 2%. First-3s hooks and creator-led variants can increase retention." },
    { id: "no_signals", check: (r) => (Number(r?.orders||0) === 0 && Number(r?.net_sales||0) === 0), why: "No orders/sales in the window. Data might be stale or mapping incomplete." },
  ];

  const recommendations = useMemo(() => {
    if (!recap || !socialRecap) return [];
    const out = [];
    for (const rule of REC_RULES) {
      if (rule.check(recap, socialRecap)) {
        if (rule.id === "low_conv") out.push({ text: "Tighten paid targeting and add PDP/cart urgency (free-shipping banner, low-stock badges).", why: rule.why });
        if (rule.id === "low_aov") out.push({ text: "Launch bundles or tiered discount (e.g., “2 for $X”, “Spend $150 get a gift”).", why: rule.why });
        if (rule.id === "weak_eng") out.push({ text: "Iterate first-3s hooks on Reels/TikTok; test creator-led cuts & stronger CTAs.", why: rule.why });
        if (rule.id === "no_signals") out.push({ text: "Verify current Shopify exports and ensure Orders/Sales mapping is flowing.", why: rule.why });
      }
    }
    if (!out.length) out.push({ text: "KPIs are healthy — scale top creatives and refresh offer angles.", why: "No rules flagged. Continue momentum." });
    return out;
  }, [recap, socialRecap]);

  const hashtags = socialRecap?.top_hashtags || { combined: [], tiktok: [], instagram: [] };

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
            {data?.brands?.length
              ? data.brands.map((b) => <option key={b.id || b.name} value={b.name}>{b.name}</option>)
              : <option>Crooks & Castles</option>}
          </select>

          <div style={{ background: "#15171a", border: "1px solid #2a2d31", borderRadius: 999, padding: 4, display: "flex", gap: 4 }}>
            <button onClick={() => setWindowDays(7)}  style={pill(windowDays === 7)}>7d</button>
            <button onClick={() => setWindowDays(30)} style={pill(windowDays === 30)}>30d</button>
          </div>

          <button
            onClick={onRefresh}
            disabled={refreshing}
            style={{
              background: refreshing ? "#2a2d31" : "#6aa6ff",
              color: refreshing ? "#8b96a3" : "#0a0b0d",
              border: "none", padding: "8px 12px", borderRadius: 8, cursor: refreshing ? "default" : "pointer",
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
        {/* KPI Cards with WoW */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
          <KpiCard label={`Orders (${windowDays}d)`} value={num(recap?.orders)} wow={recap?.wow?.orders?.pct} />
          <KpiCard label={`Net Sales (${windowDays}d)`} value={dollars(recap?.net_sales)} wow={recap?.wow?.net_sales?.pct} />
          <KpiCard label={`AOV (${windowDays}d)`} value={dollars(recap?.aov)} wow={recap?.wow?.aov?.pct} />
          <KpiCard label={`Conversion (${windowDays}d)`} value={pct(recap?.conversion_pct)} wow={recap?.wow?.conversion_pct?.pct} />
          <KpiCard label={`Sessions (${windowDays}d)`} value={num(recap?.sessions)} wow={recap?.wow?.sessions?.pct} />
          <KpiCard label={`Social Plays (${windowDays}d)`} value={num(socialRecap?.plays)} wow={socialRecap?.wow?.plays?.pct} />
          <KpiCard label={`Social Likes (${windowDays}d)`} value={num(socialRecap?.likes)} wow={socialRecap?.wow?.likes?.pct} />
          <KpiCard label={`Social Comments (${windowDays}d)`} value={num(socialRecap?.comments)} wow={socialRecap?.wow?.comments?.pct} />
        </div>

        {/* Snapshot */}
        <div style={{ marginTop: 10, fontSize: 13, color: "#98a4b3" }}>
          <span>Last data date: {recap?.last_date || "—"}</span>
          <span style={{ marginLeft: 12 }}>Refreshed: {recap?.refreshed_at || data?.snapshot?.last_import || "—"}</span>
          <span style={{ marginLeft: 12 }}>Current: {recap?.current ? "Yes" : "—"}</span>
        </div>

        {/* Recommendations with “Why?” tooltips */}
        <div style={{ marginTop: 18, padding: 16, borderRadius: 12, background: "#121418", border: "1px solid #2a2d31" }}>
          <h3 style={{ marginTop: 0, marginBottom: 8 }}>Priorities & Recommendations</h3>
          <ul style={{ margin: 0, paddingLeft: 16, lineHeight: 1.5 }}>
            {recommendations.map((t, i) => (
              <li key={i} title={t.why} style={{ cursor: "help" }}>{t.text}</li>
            ))}
          </ul>
          <div style={{ color: "#98a4b3", fontSize: 12, marginTop: 8 }}>Hover to see “Why?”.</div>
        </div>

        {/* Top Hashtags (7d/30d) */}
        <div style={{ marginTop: 18, padding: 16, borderRadius: 12, background: "#121418", border: "1px solid #2a2d31" }}>
          <h3 style={{ margin: 0, marginBottom: 8 }}>Top Hashtags ({windowDays}d)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 12 }}>
            <HashtagBoard title="Combined" items={hashtags.combined} showWow />
            <HashtagBoard title="TikTok"   items={hashtags.tiktok} />
            <HashtagBoard title="Instagram" items={hashtags.instagram} />
          </div>
        </div>

        {/* Competitive intel teaser */}
        <div style={{ marginTop: 18, padding: 16, borderRadius: 12, background: "#121418", border: "1px solid #2a2d31" }}>
          <h3 style={{ marginTop: 0, marginBottom: 8 }}>Competitive Intelligence</h3>
          <p style={{ marginTop: 0 }}>
            Compare Crooks & Castles vs. tracked brands at{" "}
            <a href="/competitive" style={{ color: "#6aa6ff", textDecoration: "underline" }}>/competitive</a>.
          </p>
          <MiniBrands brands={data?.brands || []} />
        </div>
      </section>
    </div>
  );
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

function KpiCard({ label, value, wow }) {
  return (
    <div style={{ background: "#121418", border: "1px solid #2a2d31", borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 13, color: "#98a4b3" }}>{label}</div>
      <div style={{ fontSize: 24, marginTop: 6, display: "flex", alignItems: "baseline" }}>
        <span>{value ?? "—"}</span>
        {typeof wow === "number" ? <Arrow deltaPct={wow} /> : null}
      </div>
      <div style={{ fontSize: 12, color: "#98a4b3", marginTop: 4 }}>WoW change</div>
    </div>
  );
}

function HashtagBoard({ title, items, showWow = false }) {
  if (!items || !items.length) {
    return (
      <div style={{ background: "#0f1115", border: "1px solid #2a2d31", borderRadius: 12, padding: 12 }}>
        <div style={{ color: "#98a4b3", marginBottom: 6 }}>{title}</div>
        <div style={{ color: "#98a4b3" }}>No hashtag data yet.</div>
      </div>
    );
  }
  return (
    <div style={{ background: "#0f1115", border: "1px solid #2a2d31", borderRadius: 12, padding: 12 }}>
      <div style={{ color: "#98a4b3", marginBottom: 6 }}>{title}</div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto auto", gap: 6 }}>
        <div style={{ fontSize: 12, color: "#98a4b3" }}>Tag</div>
        <div style={{ fontSize: 12, color: "#98a4b3", textAlign: "right" }}>Count</div>
        <div style={{ fontSize: 12, color: "#98a4b3", textAlign: "right" }}>{showWow ? "WoW" : ""}</div>
        {items.map((h, i) => (
          <FragmentRow key={h.tag + i} tag={h.tag} count={h.count} wow={showWow ? h?.wow?.pct : undefined} />
        ))}
      </div>
    </div>
  );
}

function FragmentRow({ tag, count, wow }) {
  const up = (wow ?? 0) >= 0;
  return (
    <>
      <div style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{tag}</div>
      <div style={{ textAlign: "right" }}>{num(count)}</div>
      <div style={{ textAlign: "right", color: wow === undefined ? "#98a4b3" : up ? "#6aff8a" : "#ff6a6a" }}>
        {wow === undefined ? "—" : `${up ? "▲" : "▼"} ${Math.abs(wow).toFixed(1)}%`}
      </div>
    </>
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
