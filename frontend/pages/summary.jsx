import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Summary() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/summary/overview`);
      if (res.ok) {
        const data = await res.json();
        setOverview(data);
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
        <h1>Performance Summary</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Performance Summary</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <MetricCard
          title="Content Pieces"
          value={overview?.content_pieces || 0}
          subtitle="Published this period"
        />
        <MetricCard
          title="Total Reach"
          value={formatNumber(overview?.total_reach || 0)}
          subtitle="Across all platforms"
        />
        <MetricCard
          title="Engagement Rate"
          value={`${overview?.engagement_rate || 0}%`}
          subtitle="Average engagement"
        />
        <MetricCard
          title="Cultural Score"
          value={`${overview?.cultural_score || 0}/10`}
          subtitle="Authenticity score"
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "2rem" }}>
        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Street Culture Performance</h2>
          <div style={{ marginBottom: "1rem" }}>
            <h3>Reach × Awareness</h3>
            <p>Impressions: {formatNumber(overview?.impressions || 0)}</p>
            <p>Follower Growth: +{overview?.follower_growth || 0}</p>
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <h3>Engagement × Resonance</h3>
            <p>Likes: {formatNumber(overview?.likes || 0)}</p>
            <p>Comments: {formatNumber(overview?.comments || 0)}</p>
          </div>
          <div>
            <h3>Conversion × Value</h3>
            <p>Revenue per Post: ${overview?.revenue_per_post || 0}</p>
            <p>ROI: {overview?.roi || 0}%</p>
          </div>
        </div>

        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1.5rem" }}>
          <h2>Performance Highlights</h2>
          {overview?.content_pieces === 0 ? (
            <div>
              <p>No content created yet - opportunity for growth and engagement</p>
              <p>Focus on authentic street culture positioning for maximum resonance</p>
            </div>
          ) : (
            <div>
              <p>{overview.content_pieces} pieces published with {overview.engagement_rate}% engagement</p>
              <p>Maintain authentic street culture positioning</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, subtitle }) {
  return (
    <div style={{
      background: "white",
      border: "1px solid #e5e7eb",
      borderRadius: "8px",
      padding: "1.5rem"
    }}>
      <div style={{ fontSize: "0.875rem", color: "#6b7280", marginBottom: "0.5rem" }}>
        {title}
      </div>
      <div style={{ fontSize: "2rem", fontWeight: "bold", marginBottom: "0.25rem" }}>
        {value}
      </div>
      <div style={{ fontSize: "0.75rem", color: "#6b7280" }}>
        {subtitle}
      </div>
    </div>
  );
}

function formatNumber(num) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}
