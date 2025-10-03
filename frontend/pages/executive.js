// frontend/pages/executive.js
import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

// Real trend calculation function - no more fake percentages
function calculateTrend(current, previous) {
  if (!current || !previous || previous === 0) return 0;
  return ((current - previous) / previous * 100).toFixed(1);
}

// Format currency properly
function formatCurrency(value) {
  if (!value || value === 0) return "$0";
  return new Intl.toLocaleString("en-US", { 
    style: "currency", 
    currency: "USD", 
    maximumFractionDigits: 0 
  });
}

// Format numbers with commas
function formatNumber(value) {
  if (!value || value === 0) return "0";
  return value.toLocaleString();
}

// Format percentage
function formatPercent(value) {
  if (!value || value === 0) return "0%";
  return `${value.toFixed(1)}%`;
}

export default function Executive() {
  const [overview, setOverview] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load both executive overview and intelligence data
      const [execRes, intelRes] = await Promise.all([
        fetch(`${API_BASE}/api/executive/overview?brand=Crooks & Castles`),
        fetch(`${API_BASE}/api/intelligence/summary`)
      ]);
      
      const execData = await execRes.json();
      const intelData = await intelRes.json();
      
      setOverview(execData);
      setIntelligence(intelData);
    } catch (err) {
      console.error("Failed to load data:", err);
      setError(err.message);
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
          <h1 style={{ margin: 0 }}>Executive Overview</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0 }}>Executive Overview</h1>
        <button 
          onClick={loadData} 
          style={{ padding: "8px 16px", cursor: "pointer" }}
        >
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
            {Array.isArray(intelligence.insights.recommendations) ? 
              intelligence.insights.recommendations.slice(0, 3).map((rec, i) => (
                <div key={i} style={{
                  background: "rgba(255,255,255,0.15)",
                  padding: "1rem",
                  borderRadius: "8px",
                  backdropFilter: "blur(10px)"
                }}>
                  <strong>Action {i + 1}:</strong> {rec}
                </div>
              )) : (
                <div style={{
                  background: "rgba(255,255,255,0.15)",
                  padding: "1rem",
                  borderRadius: "8px"
                }}>
                  <div>No recommendations available - upload data to generate insights</div>
                </div>
              )
            }
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        <MetricCard
          title="Total Sales"
          value={formatCurrency(overview?.sales_metrics?.total_sales || 0)}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.total_sales, overview?.sales_metrics?.previous_sales || 0)}
        />
        <MetricCard
          title="Total Orders"
          value={formatNumber(overview?.sales_metrics?.total_orders || 0)}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.total_orders, overview?.sales_metrics?.previous_orders || 0)}
        />
        <MetricCard
          title="Conversion Rate"
          value={formatPercent(overview?.sales_metrics?.conversion_rate || 0)}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.conversion_rate, overview?.sales_metrics?.previous_conversion || 0)}
        />
        <MetricCard
          title="Average Order Value"
          value={formatCurrency(overview?.sales_metrics?.average_order_value || 0)}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.average_order_value, overview?.sales_metrics?.previous_aov || 0)}
        />
      </div>

      {/* Performance Status */}
      <div style={{ marginBottom: "2rem" }}>
        <h2>Performance Status</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
          <StatusCard
            title="Sales Performance"
            status={overview?.performance_indicators?.sales_status || "no_data"}
            description={getStatusDescription(overview?.performance_indicators?.sales_status)}
          />
          <StatusCard
            title="Order Volume"
            status={overview?.performance_indicators?.order_volume || "no_data"}
            description={getStatusDescription(overview?.performance_indicators?.order_volume)}
          />
          <StatusCard
            title="Overall Health"
            status={overview?.performance_indicators?.overall_health || "no_data"}
            description={getStatusDescription(overview?.performance_indicators?.overall_health)}
          />
        </div>
      </div>

      {/* Recommendations */}
      {overview?.recommendations && overview.recommendations.length > 0 && (
        <div style={{ marginBottom: "2rem" }}>
          <h2>Strategic Recommendations</h2>
          <div style={{ display: "grid", gap: "1rem" }}>
            {overview.recommendations.map((rec, i) => (
              <div key={i} style={{
                background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                padding: "1.5rem",
                borderRadius: "8px",
                color: "white"
              }}>
                <strong>Recommendation {i + 1}:</strong> {rec}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Source Information */}
      <div style={{ fontSize: "0.9rem", marginTop: "1rem", opacity: 0.9 }}>
        Based on {intelligence?.data_sources || 0} analyzed data sources • 
        Last updated: {intelligence?.last_updated ? new Date(intelligence.last_updated).toLocaleString() : 'N/A'}
      </div>
    </div>
  );
}

// MetricCard component with real trend display
function MetricCard({ title, value, suffix, trend }) {
  const trendValue = parseFloat(trend) || 0;
  const trendColor = trendValue > 0 ? "#4ade80" : trendValue < 0 ? "#f87171" : "#94a3b8";
  const trendIcon = trendValue > 0 ? "↗" : trendValue < 0 ? "↘" : "→";
  
  return (
    <div style={{
      background: "#ffffff",
      border: "1px solid #e5e7eb",
      borderRadius: "12px",
      padding: "1.5rem"
    }}>
      <div style={{ fontSize: "0.875rem", color: "#6b7280", marginBottom: "0.5rem" }}>
        {title}
      </div>
      <div style={{ fontSize: "2rem", fontWeight: "bold", marginBottom: "0.5rem" }}>
        {value}{suffix}
      </div>
      <div style={{ display: "flex", alignItems: "center", fontSize: "0.875rem" }}>
        <span style={{ color: trendColor, marginRight: "0.25rem" }}>
          {trendIcon}
        </span>
        <span style={{ color: trendColor }}>
          {trendValue === 0 ? "No change" : `${Math.abs(trendValue)}%`}
        </span>
        <span style={{ color: "#6b7280", marginLeft: "0.25rem" }}>
          {trendValue === 0 ? "" : "since last period"}
        </span>
      </div>
    </div>
  );
}

// StatusCard component
function StatusCard({ title, status, description }) {
  const getStatusColor = (status) => {
    switch (status) {
      case "excellent": return "#10b981";
      case "good": return "#3b82f6";
      case "fair": return "#f59e0b";
      case "poor": return "#ef4444";
      default: return "#6b7280";
    }
  };

  return (
    <div style={{
      background: "#ffffff",
      border: "1px solid #e5e7eb",
      borderRadius: "12px",
      padding: "1.5rem"
    }}>
      <div style={{ fontSize: "0.875rem", color: "#6b7280", marginBottom: "0.5rem" }}>
        {title}
      </div>
      <div style={{
        display: "inline-block",
        background: getStatusColor(status),
        color: "white",
        padding: "0.25rem 0.75rem",
        borderRadius: "9999px",
        fontSize: "0.75rem",
        fontWeight: "500",
        marginBottom: "0.5rem"
      }}>
        {status === "no_data" ? "No Data" : status.charAt(0).toUpperCase() + status.slice(1)}
      </div>
      <div style={{ fontSize: "0.875rem", color: "#6b7280" }}>
        {description}
      </div>
    </div>
  );
}

// Helper function for status descriptions
function getStatusDescription(status) {
  switch (status) {
    case "excellent": return "Performance exceeds expectations";
    case "good": return "Performance meets targets";
    case "fair": return "Performance needs improvement";
    case "poor": return "Performance requires immediate attention";
    case "no_data": return "Upload Shopify data to see performance metrics";
    default: return "Status unknown - check data sources";
  }
}
