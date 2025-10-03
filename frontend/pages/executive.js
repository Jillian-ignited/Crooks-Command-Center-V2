import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Executive() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/executive/overview`);
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
        <h1>Executive Overview</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Executive Overview</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem" }}>
        <MetricCard
          title="Total Sales"
          value={`$${overview?.total_sales || 0}`}
          subtitle="Current period"
        />
        <MetricCard
          title="Total Orders"
          value={overview?.total_orders || 0}
          subtitle="Orders placed"
        />
        <MetricCard
          title="Conversion Rate"
          value={`${overview?.conversion_rate || 0}%`}
          subtitle="Average conversion"
        />
        <MetricCard
          title="Engagement Rate"
          value={`${overview?.engagement_rate || 0}%`}
          subtitle="Social engagement"
        />
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
