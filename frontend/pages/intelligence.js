import { useEffect, useMemo, useState } from "react";

// Simple fetch helper with legacy→/api fallback.
// Uses ?brands=all to force full competitive set by default.
async function getJSON(path) {
  const norm = path.startsWith("/") ? path : `/${path}`;
  let r = await fetch(norm);
  if (!r.ok && !norm.startsWith("/api/")) r = await fetch(`/api${norm}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} @ ${norm} -> ${await r.text()}`);
  return r.json();
}

export default function Intelligence() {
  const [brandsAll, setBrandsAll] = useState([]);
  const [selected, setSelected] = useState([]);  // UI-selected subset (optional)
  const [metrics, setMetrics] = useState(null);  // { [brand]: { metric: value } }
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);

  // Load full set on mount
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await getJSON("/intelligence/summary?brands=all");
        // Expected shape:
        // { brands_used: string[], metrics: { [brand]: { ...dynamicMetrics } } }
        const used = Array.isArray(data?.brands_used) ? data.brands_used : [];
        setBrandsAll(used);
        setSelected(used); // default to all selected
        setMetrics(data?.metrics || null);
        setErr("");
      } catch (e) {
        setErr(e?.message || String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Infer dynamic metric columns from the first brand present
  const columns = useMemo(() => {
    if (!metrics || !selected.length) return [];
    const firstBrand = selected.find((b) => metrics[b]);
    if (!firstBrand) return [];
    return Object.keys(metrics[firstBrand] || {});
  }, [metrics, selected]);

  // Re-fetch when user changes selection (optional UX: only refetch if you want backend aggregation to change)
  // Here we just filter client-side since backend already returned "all".
  const tableRows = useMemo(() => {
    if (!metrics || !columns.length) return [];
    return selected
      .filter((b) => metrics[b])
      .map((b) => ({
        brand: b,
        cells: columns.map((c) => metrics[b]?.[c]),
      }));
  }, [metrics, columns, selected]);

  const toggleBrand = (b) => {
    setSelected((prev) => (prev.includes(b) ? prev.filter((x) => x !== b) : [...prev, b]));
  };

  const selectAll = () => setSelected(brandsAll);
  const clearAll = () => setSelected([]);

  const generateReport = async () => {
    try {
      setReportLoading(true);
      setErr("");
      // Use POST request for report generation
      const response = await fetch('/intelligence/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      if (!response.ok && !response.url.includes('/api/')) {
        const apiResponse = await fetch('/api/intelligence/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        if (!apiResponse.ok) throw new Error(`${apiResponse.status} ${apiResponse.statusText}`);
        const data = await apiResponse.json();
        setReport(data);
      } else {
        const data = await response.json();
        setReport(data);
      }
    } catch (e) {
      setErr(`Failed to generate report: ${e.message}`);
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "36px auto", padding: "16px" }}>
      <div style={{ marginBottom: 24 }}>
        <a href="/" style={{ color: '#3B82F6', textDecoration: 'none' }}>← Back to Home</a>
      </div>
      
      <h1 style={{ marginBottom: 8 }}>🧠 Revenue Intelligence</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Comparing across <strong>{brandsAll.length}</strong> brand{brandsAll.length === 1 ? "" : "s"}.
      </p>

      {/* Report Generation Section */}
      <div style={{ marginBottom: 32, padding: 20, background: '#F9FAFB', borderRadius: 12, border: '1px solid #E5E7EB' }}>
        <h2 style={{ marginBottom: 16, color: '#1F2937' }}>📊 Generate Intelligence Report</h2>
        <button 
          onClick={generateReport}
          disabled={reportLoading}
          style={{
            padding: '12px 24px',
            background: reportLoading ? '#9CA3AF' : 'linear-gradient(to right, #F97316, #DC2626)',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            fontSize: 16,
            fontWeight: 'bold',
            cursor: reportLoading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          {reportLoading ? 'Generating...' : 'Generate Unified Intelligence Report'}
        </button>
      </div>

      {/* Report Display */}
      {report && (
        <div style={{ marginBottom: 32, padding: 24, background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 12 }}>
          <h2 style={{ color: '#166534', marginBottom: 20 }}>📈 Intelligence Report Generated</h2>
          
          {report.performance_metrics && (
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ color: '#374151', marginBottom: 12 }}>Performance Metrics</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                <div style={{ padding: 12, background: 'white', borderRadius: 6 }}>
                  <strong>Engagement Rate:</strong> {report.performance_metrics.engagement_rate}
                </div>
                <div style={{ padding: 12, background: 'white', borderRadius: 6 }}>
                  <strong>Reach Growth:</strong> {report.performance_metrics.reach_growth}
                </div>
                <div style={{ padding: 12, background: 'white', borderRadius: 6 }}>
                  <strong>Brand Mentions:</strong> {report.performance_metrics.brand_mentions}
                </div>
              </div>
            </div>
          )}

          {report.strategic_recommendations && (
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ color: '#374151', marginBottom: 12 }}>🎯 Strategic Recommendations</h3>
              <div style={{ display: 'grid', gap: 12 }}>
                {report.strategic_recommendations.map((rec, index) => (
                  <div key={index} style={{ padding: 16, background: 'white', borderRadius: 8 }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#1F2937' }}>{rec.title}</h4>
                    <p style={{ margin: 0, color: '#6B7280' }}>{rec.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.trending_topics && (
            <div>
              <h3 style={{ color: '#374151', marginBottom: 12 }}>🔥 Trending Topics</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {report.trending_topics.map((topic, index) => (
                  <span key={index} style={{ 
                    padding: '6px 12px', 
                    background: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: 16,
                    fontSize: 14
                  }}>
                    {topic.topic} ({topic.score})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Controls */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center", margin: "12px 0 16px" }}>
        <button onClick={selectAll}>Select All</button>
        <button onClick={clearAll}>Clear</button>
        <span style={{ opacity: 0.8 }}>Selected: {selected.length}</span>
      </div>

      {/* Brand pills */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
        {brandsAll.map((b) => {
          const active = selected.includes(b);
          return (
            <button
              key={b}
              onClick={() => toggleBrand(b)}
              style={{
                padding: "6px 10px",
                borderRadius: 16,
                border: "1px solid #ccc",
                background: active ? "#111" : "#fff",
                color: active ? "#fff" : "#111",
                cursor: "pointer",
              }}
              title={active ? "Click to remove" : "Click to add"}
            >
              {b}
            </button>
          );
        })}
      </div>

      {/* Status */}
      {loading && <p>Loading…</p>}
      {err && (
        <pre style={{ background: "#2a0000", color: "#ffb3b3", padding: 12, borderRadius: 8, whiteSpace: "pre-wrap" }}>
          {err}
        </pre>
      )}

      {/* Dynamic table */}
      {!loading && !err && metrics && columns.length > 0 ? (
        <div style={{ overflowX: "auto", border: "1px solid #eee", borderRadius: 8 }}>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th style={thStyle}>Brand</th>
                {columns.map((c) => (
                  <th key={c} style={thStyle}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row) => (
                <tr key={row.brand}>
                  <td style={tdStyleBold}>{row.brand}</td>
                  {row.cells.map((v, i) => (
                    <td key={i} style={tdStyle}>
                      {formatCell(v)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {/* Fallback raw JSON for debugging (collapsible) */}
      {!loading && metrics && (
        <details style={{ marginTop: 16 }}>
          <summary>Raw response</summary>
          <pre style={{ background: "#111", color: "#eee", padding: 12, borderRadius: 8 }}>
            {JSON.stringify({ brands_used: brandsAll, metrics }, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}

const thStyle = {
  textAlign: "left",
  padding: "10px 12px",
  borderBottom: "1px solid #eee",
  position: "sticky",
  top: 0,
  background: "#fafafa",
  fontWeight: 600,
  whiteSpace: "nowrap",
};

const tdStyle = {
  padding: "10px 12px",
  borderBottom: "1px solid #f2f2f2",
  whiteSpace: "nowrap",
};

const tdStyleBold = { ...tdStyle, fontWeight: 600 };

function formatCell(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") {
    // Heuristic: treat 0–1 as rate, larger numbers as counts
    if (v > 0 && v <= 1) return `${(v * 100).toFixed(1)}%`;
    if (Number.isInteger(v)) return v.toLocaleString();
    return v.toFixed(2);
  }
  return String(v);
}
