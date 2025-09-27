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

  return (
    <div style={{ maxWidth: 1100, margin: "36px auto", padding: "16px" }}>
      <h1 style={{ marginBottom: 8 }}>Competitive Intelligence</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Comparing across <strong>{brandsAll.length}</strong> brand{brandsAll.length === 1 ? "" : "s"}.
      </p>

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
