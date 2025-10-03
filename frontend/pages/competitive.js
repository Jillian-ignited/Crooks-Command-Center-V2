import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Competitive() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/competitive/analysis`);
      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
      } else {
        setError("Failed to load competitive analysis data");
      }
    } catch (err) {
      console.error("Failed to load data:", err);
      setError("Network error - please check your connection");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Competitive Analysis</h1>
        <p>Loading competitive intelligence...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Competitive Analysis</h1>
        <div style={{ background: "#fee2e2", border: "1px solid #fecaca", borderRadius: "8px", padding: "1rem", color: "#dc2626" }}>
          <p><strong>Error:</strong> {error}</p>
          <button onClick={loadData} style={{ marginTop: "1rem", padding: "8px 16px", cursor: "pointer" }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const hasData = analysis?.data_status !== "awaiting_upload" && analysis?.intelligence_score > 0;

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Competitive Analysis</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      {!hasData && (
        <div style={{ background: "#fef3c7", border: "1px solid #fcd34d", borderRadius: "8px", padding: "1.5rem", marginBottom: "2rem" }}>
          <h2 style={{ color: "#92400e", marginTop: 0 }}>Setup Required</h2>
          <p style={{ color: "#92400e" }}>Upload competitive intelligence data to see analysis and insights.</p>
          <div style={{ marginTop: "1rem" }}>
            <h3 style={{ color: "#92400e" }}>Recommended Setup:</h3>
            <ul style={{ color: "#92400e" }}>
              {(analysis?.recommendations || []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "2rem" }}>
        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Brand Positioning</h2>
          <p><strong>Market Position:</strong> {analysis?.market_position || "N/A"}</p>
          <p><strong>Brand Identity:</strong> {analysis?.brand_identity || "N/A"}</p>
          <div>
            <strong>Differentiation:</strong>
            <ul>
              {(analysis?.differentiation || []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Competitive Threats</h2>
          {hasData ? (
            <>
              <div style={{ marginBottom: "1rem" }}>
                <h3 style={{ color: "#ef4444" }}>High Threat</h3>
                <ul>
                  {(analysis?.competitive_threats?.high || []).map((item, i) => (
                    <li key={i}><strong>{item.brand}</strong> - {item.reason}</li>
                  ))}
                </ul>
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <h3 style={{ color: "#f59e0b" }}>Medium Threat</h3>
                <ul>
                  {(analysis?.competitive_threats?.medium || []).map((item, i) => (
                    <li key={i}><strong>{item.brand}</strong> - {item.reason}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p style={{ color: "#6b7280", fontStyle: "italic" }}>
              Upload competitor data to see threat analysis
            </p>
          )}
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Strategic Opportunities</h2>
          <ul>
            {(analysis?.opportunities || []).map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Intelligence Score</h2>
          <div style={{ 
            fontSize: "3rem", 
            fontWeight: "bold", 
            color: hasData ? "#10b981" : "#6b7280", 
            textAlign: "center" 
          }}>
            {analysis?.intelligence_score || 0}/100
          </div>
          <p style={{ textAlign: "center", color: "#6b7280" }}>
            Coverage: {analysis?.coverage_level || "No data"}
          </p>
          {!hasData && (
            <p style={{ textAlign: "center", color: "#6b7280", fontSize: "0.875rem", marginTop: "1rem" }}>
              Score will increase as you upload competitive data
            </p>
          )}
        </div>
      </div>

      {analysis?.last_updated && (
        <div style={{ marginTop: "2rem", textAlign: "center", color: "#6b7280", fontSize: "0.875rem" }}>
          Last updated: {new Date(analysis.last_updated).toLocaleString()}
        </div>
      )}
    </div>
  );
}
