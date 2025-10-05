import { useState, useEffect } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Competitive() {
  const [analysis, setAnalysis] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("analysis");

  const loadAnalysisData = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/competitive/analysis`);
      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
      } else {
        console.error("Failed to load competitive analysis data");
      }
    } catch (err) {
      console.error("Failed to load analysis data:", err);
    }
  };

  const loadComparisonData = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/competitive-analysis/comparison`);
      if (res.ok) {
        const data = await res.json();
        setComparison(data);
      } else {
        console.error("Failed to load brand comparison data");
      }
    } catch (err) {
      console.error("Failed to load comparison data:", err);
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([loadAnalysisData(), loadComparisonData()]);
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
        <h1>Competitive Intelligence</h1>
        <p>Loading competitive intelligence...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Competitive Intelligence</h1>
        <div style={{ background: "#fee2e2", border: "1px solid #fecaca", borderRadius: "8px", padding: "1rem", color: "#dc2626" }}>
          <p><strong>Error:</strong> {error}</p>
          <button onClick={loadData} style={{ marginTop: "1rem", padding: "8px 16px", cursor: "pointer" }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const hasAnalysisData = analysis?.data_status !== "awaiting_upload" && analysis?.intelligence_score > 0;
  const hasComparisonData = comparison?.crooks_and_castles?.data_status !== "awaiting_upload";

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Competitive Intelligence</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      {/* Tab Navigation */}
      <div style={{ marginBottom: "2rem", borderBottom: "1px solid #e5e7eb" }}>
        <div style={{ display: "flex", gap: "2rem" }}>
          <button 
            onClick={() => setActiveTab("analysis")}
            style={{ 
              padding: "1rem 0", 
              border: "none", 
              background: "none", 
              borderBottom: activeTab === "analysis" ? "2px solid #3b82f6" : "none",
              color: activeTab === "analysis" ? "#3b82f6" : "#6b7280",
              fontWeight: activeTab === "analysis" ? "bold" : "normal",
              cursor: "pointer"
            }}
          >
            Competitive Analysis
          </button>
          <button 
            onClick={() => setActiveTab("comparison")}
            style={{ 
              padding: "1rem 0", 
              border: "none", 
              background: "none", 
              borderBottom: activeTab === "comparison" ? "2px solid #3b82f6" : "none",
              color: activeTab === "comparison" ? "#3b82f6" : "#6b7280",
              fontWeight: activeTab === "comparison" ? "bold" : "normal",
              cursor: "pointer"
            }}
          >
            Brand Comparison
          </button>
        </div>
      </div>

      {/* Competitive Analysis Tab */}
      {activeTab === "analysis" && (
        <>
          {!hasAnalysisData && (
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
              {hasAnalysisData ? (
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
          </div>
        </>
      )}

      {/* Brand Comparison Tab */}
      {activeTab === "comparison" && (
        <>
          {!hasComparisonData && (
            <div style={{ background: "#fef3c7", border: "1px solid #fcd34d", borderRadius: "8px", padding: "1.5rem", marginBottom: "2rem" }}>
              <h2 style={{ color: "#92400e", marginTop: 0 }}>Brand Comparison Setup</h2>
              <p style={{ color: "#92400e" }}>Connect social media accounts and upload competitor data to see brand comparison metrics.</p>
              <div style={{ marginTop: "1rem" }}>
                <h3 style={{ color: "#92400e" }}>Next Steps:</h3>
                <ul style={{ color: "#92400e" }}>
                  {(comparison?.next_steps || []).map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "2rem" }}>
            {/* Crooks & Castles Performance */}
            <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
              <h2>Crooks & Castles Performance</h2>
              <div style={{ marginBottom: "1rem" }}>
                <p><strong>Brand Mentions:</strong> {comparison?.crooks_and_castles?.brand_mentions || 0}</p>
                <p><strong>Engagement Rate:</strong> {comparison?.crooks_and_castles?.engagement_rate || 0}%</p>
                <p><strong>Follower Growth:</strong> {comparison?.crooks_and_castles?.follower_growth || 0}</p>
                <p><strong>Sentiment:</strong> {comparison?.crooks_and_castles?.sentiment || "No data"}</p>
              </div>
            </div>

            {/* Competitors */}
            <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
              <h2>Competitors</h2>
              {comparison?.competitors?.length > 0 ? (
                comparison.competitors.map((competitor, i) => (
                  <div key={i} style={{ marginBottom: "1rem", padding: "1rem", background: "#f9fafb", borderRadius: "4px" }}>
                    <h3>{competitor.name}</h3>
                    <p><strong>Engagement:</strong> {competitor.engagement_rate || 0}%</p>
                    <p><strong>Growth:</strong> {competitor.follower_growth || 0}</p>
                  </div>
                ))
              ) : (
                <p style={{ color: "#6b7280", fontStyle: "italic" }}>
                  No competitor data available. Upload competitor information to see comparisons.
                </p>
              )}
            </div>

            {/* Content Suggestions */}
            <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
              <h2>Content Suggestions</h2>
              <ul>
                {(comparison?.content_suggestions || []).map((suggestion, i) => (
                  <li key={i} style={{ marginBottom: "0.5rem" }}>{suggestion}</li>
                ))}
              </ul>
            </div>

            {/* Data Sources */}
            <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
              <h2>Data Sources</h2>
              <div style={{ marginBottom: "1rem" }}>
                <h3>Connected:</h3>
                {comparison?.data_sources?.connected?.length > 0 ? (
                  <ul>
                    {comparison.data_sources.connected.map((source, i) => (
                      <li key={i} style={{ color: "#10b981" }}>{source}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: "#6b7280", fontStyle: "italic" }}>No sources connected</p>
                )}
              </div>
              <div>
                <h3>Available:</h3>
                <ul>
                  {(comparison?.data_sources?.available || []).map((source, i) => (
                    <li key={i} style={{ color: "#6b7280" }}>{source}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
