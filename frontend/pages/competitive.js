import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Competitive() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/competitive/analysis`);
      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
      }
    } catch (err) {
      console.error("Failed to load data:", err);
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
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Competitive Analysis</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "2rem" }}>
        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Brand Positioning</h2>
          <p><strong>Market Position:</strong> {analysis?.market_position || "Strong"}</p>
          <p><strong>Brand Identity:</strong> {analysis?.brand_identity || "Authentic streetwear pioneer"}</p>
          <div>
            <strong>Differentiation:</strong>
            <ul>
              {(analysis?.differentiation || ["Heritage", "Streetwear authenticity", "Urban culture"]).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Competitive Threats</h2>
          <div style={{ marginBottom: "1rem" }}>
            <h3 style={{ color: "#ef4444" }}>High Threat</h3>
            <ul>
              <li>Hellstar - Gen Z hype, rap co-signs</li>
              <li>Memory Lane - Y2K nostalgia</li>
              <li>Amiri - Luxury LA streetwear</li>
            </ul>
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <h3 style={{ color: "#f59e0b" }}>Medium Threat</h3>
            <ul>
              <li>Supreme - Global recognition</li>
              <li>Kith - Collab-driven</li>
              <li>ALD - Boutique culture</li>
            </ul>
          </div>
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Strategic Opportunities</h2>
          <ul>
            {(analysis?.opportunities || ["Digital engagement", "Collaborations", "International expansion"]).map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Intelligence Score</h2>
          <div style={{ fontSize: "3rem", fontWeight: "bold", color: "#10b981", textAlign: "center" }}>
            {analysis?.intelligence_score || 85}/100
          </div>
          <p style={{ textAlign: "center", color: "#6b7280" }}>
            Coverage: {analysis?.coverage_level || "Excellent"}
          </p>
        </div>
      </div>
    </div>
  );
}
