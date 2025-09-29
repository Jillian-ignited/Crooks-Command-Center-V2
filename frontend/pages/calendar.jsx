import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

const VIEWS = [
  { key: "7", label: "7 Days" },
  { key: "30", label: "30 Days" },
  { key: "60", label: "60 Days" },
  { key: "quarter", label: "Quarter (90d)" },
];

export default function CalendarPage() {
  const [status, setStatus] = useState(null);
  const [view, setView] = useState("30"); // default to 30 days
  const [data, setData] = useState(null); // { window, events, culture_recommendations }
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function load(currView = view) {
    setLoading(true);
    setErr("");
    try {
      const s = await apiGet("/calendar/status");
      setStatus(s);
    } catch (e) {
      setErr(prev => (prev ? prev + " | " : "") + `Status: ${e.message}`);
    }

    try {
      const ev = await apiGet("/calendar/events", { query: { view: currView } });
      setData(ev);
    } catch (e) {
      setErr(prev => (prev ? prev + " | " : "") + `Events: ${e.message}`);
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(view); }, []); // initial load

  function onChangeView(e) {
    const v = e.target.value;
    setView(v);
    load(v);
  }

  return (
    <main style={{ maxWidth: 960, margin: "40px auto", padding: "0 16px", fontFamily: "system-ui" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Calendar</h1>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <label htmlFor="view" style={{ fontSize: 14, opacity: 0.8 }}>View</label>
          <select id="view" value={view} onChange={onChangeView} style={{ padding: "6px 8px", borderRadius: 8 }}>
            {VIEWS.map(v => <option key={v.key} value={v.key}>{v.label}</option>)}
          </select>
          <button onClick={() => load(view)} disabled={loading} style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#fff" }}>
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>
      </header>

      {err && <p style={{ color: "crimson", marginTop: 12 }}>{err}</p>}

      {/* Status Card */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Connection</h2>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <span
            style={{
              display: "inline-block",
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: status?.connected ? "seagreen" : "darkorange",
            }}
          />
          <span style={{ fontSize: 14 }}>
            {status?.connected ? "Connected" : "Not connected"}
            {status?.provider ? ` · ${status.provider}` : ""}
          </span>
          {status?.note && <span style={{ fontSize: 12, opacity: 0.8 }}>({status.note})</span>}
        </div>
      </section>

      {/* Window + Events */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
          <h2 style={{ marginTop: 0 }}>Events</h2>
          {data?.window && (
            <div style={{ fontSize: 13, opacity: 0.75 }}>
              {data.window.start} → {data.window.end}
            </div>
          )}
        </div>

        {!data?.events?.length && (
          <p style={{ opacity: 0.7, marginTop: 8 }}>No events in this window.</p>
        )}

        {!!data?.events?.length && (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8, marginTop: 8 }}>
            {data.events.map((ev, i) => (
              <li key={i} style={{ border: "1px solid #eee", borderRadius: 10, padding: 12 }}>
                <div style={{ fontWeight: 600 }}>{ev.title || "Untitled Event"}</div>
                <div style={{ fontSize: 13, opacity: 0.8 }}>
                  {ev.start ? new Date(ev.start).toLocaleString() : "TBD"}
                  {ev.channel ? ` · ${ev.channel}` : ""}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Cultural Recommendations */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Cultural Recommendations</h2>
        {!data?.culture_recommendations?.length && (
          <p style={{ opacity: 0.7 }}>No recommendations for this horizon yet.</p>
        )}
        {!!data?.culture_recommendations?.length && (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
            {data.culture_recommendations.map((r, i) => (
              <li key={i} style={{ border: "1px solid #eee", borderRadius: 10, padding: 12 }}>
                <div style={{ fontWeight: 600 }}>{r.theme}</div>
                <div style={{ fontSize: 13, opacity: 0.85, marginTop: 4 }}>{r.why}</div>
                {r.cta && <div style={{ fontSize: 13, marginTop: 6 }}><strong>CTA:</strong> {r.cta}</div>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
