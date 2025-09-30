// frontend/pages/executive.js
import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "";

export default function Executive() {
  const [overview, setOverview] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      // Load both executive overview and intelligence in parallel
      const [execRes, intelRes] = await Promise.all([
        fetch(`${API_BASE}/api/executive/overview?brand=Crooks & Castles`),
        fetch(`${API_BASE}/api/intelligence/summary`)
      ]);
      
      const execData = await execRes.json();
      const intelData = await intelRes.json();
      
      setOverview(execData);
      setIntelligence(intelData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Executive Overview</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0 }}>Executive Overview</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      {/* AI Priority Recommendations - TOP OF PAGE */}
      {intelligence?.insights?.recommendations && (
        <div style={{ 
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
          padding: "1.5rem", 
          borderRadius: "12px", 
          marginBottom: "2rem",
          color: "white"
        }}>
          <h2 style={{ margin: "0 0 1rem 0", fontSize: "1.3rem" }}>🎯 Priority Actions</h2>
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {Array.isArray(intelligence.insights.recommendations) ? (
              intelligence.insights.recommendations.slice(0, 3).map((rec, i) => (
                <div key={i} style={{ 
                  background: "rgba(255,255,255,0.15)", 
                  padding: "0.75rem 1rem",
                  borderRadius: "8px",
                  backdropFilter: "blur(10px)"
                }}>
                  <strong>Action {i + 1}:</strong> {rec}
                </div>
              ))
            ) : (
              <div>{intelligence.insights.recommendations}</div>
            )}
          </div>
          <div style={{ fontSize: "0.85rem", marginTop: "1rem", opacity: 0.9 }}>
            Based on {intelligence.files_processed} analyzed data sources • 
            Last updated: {intelligence.last_updated ? new Date(intelligence.last_updated).toLocaleDateString() : 'N/A'}
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        <MetricCard
          title="Engagement Rate"
          value={overview?.data?.metrics?.engagement_rate || overview?.metrics?.engagement_rate || 0}
          suffix="%"
          trend={15.2}
        />
        <MetricCard
          title="Follower Growth"
          value={overview?.data?.metrics?.follower_growth || overview?.metrics?.follower_growth || 0}
          suffix="%"
          trend={12.3}
        />
        <MetricCard
          title="Content Performance"
          value={overview?.data?.metrics?.content_performance || overview?.metrics?.content_performance || 0}
          suffix="/100"
          trend={8.7}
        />
        <MetricCard
          title="Reach"
          value={(overview?.data?.metrics?.reach || overview?.metrics?.reach || 0) / 1000}
          suffix="K"
          trend={18.4}
        />
      </div>

      {/* Trending Topics from AI */}
      {intelligence?.insights?.trending_topics && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", marginBottom: "2rem" }}>
          <h3 style={{ margin: "0 0 1rem 0" }}>📈 Trending Now</h3>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            {Array.isArray(intelligence.insights.trending_topics) ? (
              intelligence.insights.trending_topics.map((topic, i) => (
                <span key={i} style={{ 
                  background: "#2a2a2a", 
                  padding: "8px 16px", 
                  borderRadius: "20px",
                  fontSize: "0.95rem",
                  border: "1px solid #3a3a3a"
                }}>
                  {typeof topic === 'string' ? topic : topic.name || JSON.stringify(topic)}
                </span>
              ))
            ) : (
              <span>{intelligence.insights.trending_topics}</span>
            )}
          </div>
        </div>
      )}

      {/* Key Insights from AI */}
      {intelligence?.insights?.insights && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", marginBottom: "2rem" }}>
          <h3 style={{ margin: "0 0 1rem 0" }}>💡 Key Insights</h3>
          <ul style={{ margin: 0, paddingLeft: "1.5rem" }}>
            {Array.isArray(intelligence.insights.insights) ? (
              intelligence.insights.insights.map((insight, i) => (
                <li key={i} style={{ marginBottom: "0.75rem", lineHeight: "1.6" }}>{insight}</li>
              ))
            ) : (
              <li>{intelligence.insights.insights}</li>
            )}
          </ul>
        </div>
      )}

      {/* Hashtag Strategy */}
      {intelligence?.insights?.hashtag_strategy && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", marginBottom: "2rem" }}>
          <h3 style={{ margin: "0 0 1rem 0" }}>#️⃣ Hashtag Strategy</h3>
          <p style={{ lineHeight: "1.6", margin: 0 }}>{intelligence.insights.hashtag_strategy}</p>
        </div>
      )}

      {/* Posting Recommendations */}
      {intelligence?.insights?.posting_recommendations && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px" }}>
          <h3 style={{ margin: "0 0 1rem 0" }}>⏰ Posting Strategy</h3>
          <p style={{ lineHeight: "1.6", margin: 0 }}>{intelligence.insights.posting_recommendations}</p>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, suffix = "", trend }) {
  const isPositive = trend >= 0;
  return (
    <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px" }}>
      <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>{title}</div>
      <div style={{ fontSize: "2rem", fontWeight: "bold", marginBottom: "0.5rem" }}>
        {typeof value === 'number' ? value.toFixed(1) : value}{suffix}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <span style={{ color: isPositive ? "#4ade80" : "#f87171" }}>
          {isPositive ? "▲" : "▼"} {Math.abs(trend)}%
        </span>
        <span style={{ fontSize: "0.85rem", color: "#666" }}>vs last period</span>
      </div>
    </div>
  );
}
