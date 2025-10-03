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
            {(Array.isArray(intelligence.insights.recommendations) ? 
              intelligence.insights.recommendations.slice(0, 3).map((rec, i) => (
                <div key={i} style={{
                  background: "rgba(255,255,255,0.15)",
                  padding: "0.75rem 1rem",
                  borderRadius: "8px",
                  backdropFilter: "blur(10px)"
                }}>
                  <strong>Action {i + 1}:</strong> {rec}
                </div>
              )) : (
                <div>No recommendations available - upload data to generate insights</div>
              )
            )}
          </div>
        </div>
      )}

      <div style={{ fontSize: "0.9rem", marginTop: "1rem", opacity: 0.9 }}>
        Based on {intelligence?.data_sources || 0} analyzed data sources •
        Last updated: {intelligence?.last_updated ? new Date(intelligence.last_updated).toLocaleDateString() : 'N/A'}
      </div>

      {/* Metrics Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        <MetricCard
          title="Total Sales"
          value={formatCurrency(overview?.sales_metrics?.total_sales || 0)}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.total_sales, 0)}
        />
        <MetricCard
          title="Total Orders"
          value={overview?.sales_metrics?.total_orders || 0}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.total_orders, 0)}
        />
        <MetricCard
          title="Conversion Rate"
          value={overview?.sales_metrics?.conversion_rate || 0}
          suffix="%"
          trend={calculateTrend(overview?.sales_metrics?.conversion_rate, 0)}
        />
        <MetricCard
          title="Average Order Value"
          value={formatCurrency(overview?.sales_metrics?.average_order_value || 0)}
          suffix=""
          trend={calculateTrend(overview?.sales_metrics?.average_order_value, 0)}
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
                padding: "1rem",
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
      <div style={{ marginTop: "2rem", padding: "1rem", background: "#f8f9fa", borderRadius: "8px" }}>
        <h3>Data Sources</h3>
        <p><strong>Executive Data:</strong> {overview?.data_source || "Unknown"}</p>
        <p><strong>Intelligence Data:</strong> {intelligence?.data_source || "Unknown"}</p>
        <p><strong>Last Updated:</strong> {overview?.generated_at ? new Date(overview.generated_at).toLocaleString() : "Unknown"}</p>
      </div>
    </div>
  );
}

// Helper Components
function MetricCard({ title, value, suffix, trend }) {
  const trendColor = trend > 0 ? "#10b981" : trend < 0 ? "#ef4444" : "#6b7280";
  const trendSymbol = trend > 0 ? "↗" : trend < 0 ? "↘" : "→";
  
  return (
    <div style={{
      background: "white",
      padding: "1.5rem",
      borderRadius: "12px",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
      border: "1px solid #e5e7eb"
    }}>
      <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", color: "#6b7280" }}>{title}</h3>
      <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#1f2937" }}>
        {value}{suffix}
      </div>
      <div style={{ fontSize: "0.8rem", color: trendColor, marginTop: "0.5rem" }}>
        {trendSymbol} {trend === 0 ? "No change" : `${Math.abs(trend).toFixed(1)}%`}
      </div>
    </div>
  );
}

function StatusCard({ title, status, description }) {
  const statusColors = {
    "good": "#10b981",
    "healthy": "#10b981",
    "moderate": "#f59e0b",
    "needs_improvement": "#ef4444",
    "needs_data": "#6b7280",
    "no_data": "#6b7280"
  };

  return (
    <div style={{
      background: "white",
      padding: "1.5rem",
      borderRadius: "12px",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
      border: "1px solid #e5e7eb"
    }}>
      <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1rem" }}>{title}</h3>
      <div style={{
        display: "inline-block",
        padding: "0.25rem 0.75rem",
        borderRadius: "20px",
        fontSize: "0.8rem",
        fontWeight: "bold",
        color: "white",
        background: statusColors[status] || "#6b7280"
      }}>
        {status.replace(/_/g, ' ').toUpperCase()}
      </div>
      <p style={{ margin: "0.5rem 0 0 0", fontSize: "0.9rem", color: "#6b7280" }}>
        {description}
      </p>
    </div>
  );
}

// Helper Functions
function formatCurrency(amount) {
  if (amount === 0) return "$0";
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

function calculateTrend(current, previous) {
  // For now, return 0 since we don't have historical data
  // In a real implementation, this would compare current vs previous period
  if (current === 0 && previous === 0) return 0;
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / previous) * 100;
}

function getStatusDescription(status) {
  const descriptions = {
    "good": "Performance is meeting expectations",
    "healthy": "All systems operating normally",
    "moderate": "Some areas need attention",
    "needs_improvement": "Immediate action required",
    "needs_data": "Upload data to see performance insights",
    "no_data": "No data available - upload Shopify reports to track performance"
  };
  return descriptions[status] || "Status unknown";
}
