import { useState, useEffect } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function Dashboard() {
  const [shopifyData, setShopifyData] = useState(null);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      
      // Load REAL Shopify data + recent intelligence
      const [shopifyRes, overviewRes] = await Promise.all([
        fetch(`${API_BASE_URL}/shopify/dashboard?period=30d`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE_URL}/executive/overview`).then(r => r.json()).catch(() => null)
      ]);
      
      setShopifyData(shopifyRes);
      setOverview(overviewRes);
    } catch (err) {
      console.error("Failed to load dashboard:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: "2rem" }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        {/* Header */}
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem", color: "#e9edf2" }}>Crooks Command Center</h1>
          <p style={{ color: "#888" }}>Intelligence-driven brand management for Crooks & Castles</p>
        </div>

        {/* Key Metrics - REAL DATA */}
        {shopifyData ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
            {/* Revenue */}
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                <div style={{ color: "#888", fontSize: "0.9rem" }}>💰 Revenue (30d)</div>
                {shopifyData.revenue.growth !== 0 && (
                  <span style={{ 
                    fontSize: "0.85rem", 
                    color: shopifyData.revenue.growth > 0 ? "#4ade80" : "#ff6b6b",
                    background: shopifyData.revenue.growth > 0 ? "#1a2a1a" : "#2a1a1a",
                    padding: "2px 8px",
                    borderRadius: "12px"
                  }}>
                    {shopifyData.revenue.growth > 0 ? "↑" : "↓"} {Math.abs(shopifyData.revenue.growth)}%
                  </span>
                )}
              </div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                ${shopifyData.revenue.current.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
                vs ${shopifyData.revenue.previous.toLocaleString()} prev period
              </div>
            </div>

            {/* Orders */}
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                <div style={{ color: "#888", fontSize: "0.9rem" }}>📦 Orders</div>
                {shopifyData.orders.growth !== 0 && (
                  <span style={{ 
                    fontSize: "0.85rem", 
                    color: shopifyData.orders.growth > 0 ? "#4ade80" : "#ff6b6b",
                    background: shopifyData.orders.growth > 0 ? "#1a2a1a" : "#2a1a1a",
                    padding: "2px 8px",
                    borderRadius: "12px"
                  }}>
                    {shopifyData.orders.growth > 0 ? "↑" : "↓"} {Math.abs(shopifyData.orders.growth)}%
                  </span>
                )}
              </div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                {shopifyData.orders.current.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
                vs {shopifyData.orders.previous.toLocaleString()} prev period
              </div>
            </div>

            {/* AOV */}
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                <div style={{ color: "#888", fontSize: "0.9rem" }}>💵 Avg Order Value</div>
                {shopifyData.avg_order_value.growth !== 0 && (
                  <span style={{ 
                    fontSize: "0.85rem", 
                    color: shopifyData.avg_order_value.growth > 0 ? "#4ade80" : "#ff6b6b",
                    background: shopifyData.avg_order_value.growth > 0 ? "#1a2a1a" : "#2a1a1a",
                    padding: "2px 8px",
                    borderRadius: "12px"
                  }}>
                    {shopifyData.avg_order_value.growth > 0 ? "↑" : "↓"} {Math.abs(shopifyData.avg_order_value.growth)}%
                  </span>
                )}
              </div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                ${shopifyData.avg_order_value.current.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
                vs ${shopifyData.avg_order_value.previous.toLocaleString()} prev period
              </div>
            </div>

            {/* Customers */}
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                <div style={{ color: "#888", fontSize: "0.9rem" }}>👥 Customers</div>
                {shopifyData.customers.growth !== 0 && (
                  <span style={{ 
                    fontSize: "0.85rem", 
                    color: shopifyData.customers.growth > 0 ? "#4ade80" : "#ff6b6b",
                    background: shopifyData.customers.growth > 0 ? "#1a2a1a" : "#2a1a1a",
                    padding: "2px 8px",
                    borderRadius: "12px"
                  }}>
                    {shopifyData.customers.growth > 0 ? "↑" : "↓"} {Math.abs(shopifyData.customers.growth)}%
                  </span>
                )}
              </div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                {shopifyData.customers.current.toLocaleString()}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
                vs {shopifyData.customers.previous.toLocaleString()} prev period
              </div>
            </div>

            {/* Conversion Rate */}
            {shopifyData.conversion_rate && (
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem" }}>📈 Conversion Rate</div>
                  {shopifyData.conversion_rate.growth !== 0 && (
                    <span style={{ 
                      fontSize: "0.85rem", 
                      color: shopifyData.conversion_rate.growth > 0 ? "#4ade80" : "#ff6b6b",
                      background: shopifyData.conversion_rate.growth > 0 ? "#1a2a1a" : "#2a1a1a",
                      padding: "2px 8px",
                      borderRadius: "12px"
                    }}>
                      {shopifyData.conversion_rate.growth > 0 ? "↑" : "↓"} {Math.abs(shopifyData.conversion_rate.growth)}%
                    </span>
                  )}
                </div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                  {shopifyData.conversion_rate.current}%
                </div>
                <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
                  vs {shopifyData.conversion_rate.previous}% prev period
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", marginBottom: "2rem", textAlign: "center", border: "1px solid #2a2a2a" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📊</div>
            <h3 style={{ color: "#e9edf2", marginBottom: "0.5rem" }}>No Shopify Data Yet</h3>
            <p style={{ color: "#888", marginBottom: "1.5rem" }}>Upload your Shopify orders CSV to see real metrics</p>
            <a href="/docs" target="_blank" style={{ padding: "10px 20px", background: "#6aa6ff", color: "#fff", borderRadius: "6px", textDecoration: "none", display: "inline-block" }}>
              Upload via API Docs
            </a>
          </div>
        )}

        {/* Two Column Layout */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
          {/* Recent Intelligence */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <h2 style={{ marginBottom: "1rem", color: "#e9edf2", fontSize: "1.25rem" }}>📊 Recent Intelligence</h2>
            {overview && overview.recent_files && overview.recent_files.length > 0 ? (
              overview.recent_files.map(f => (
                <div key={f.id} style={{ padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginBottom: "0.5rem" }}>
                  <div style={{ fontWeight: "600", color: "#e9edf2" }}>{f.filename}</div>
                  <div style={{ fontSize: "0.85rem", color: "#888" }}>{f.source}</div>
                </div>
              ))
            ) : (
              <p style={{ color: "#888" }}>No intelligence files uploaded yet</p>
            )}
          </div>

          {/* Quick Actions */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <h2 style={{ marginBottom: "1rem", color: "#e9edf2", fontSize: "1.25rem" }}>⚡ Quick Actions</h2>
            <a href="/upload" style={{ display: "block", padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginBottom: "0.5rem", textDecoration: "none", color: "#e9edf2", transition: "all 0.2s" }} onMouseEnter={e => e.currentTarget.style.background = "#1a1a2a"} onMouseLeave={e => e.currentTarget.style.background = "#0a0b0d"}>
              <div>📤 Upload Intelligence</div>
            </a>
            <a href="/intelligence" style={{ display: "block", padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginBottom: "0.5rem", textDecoration: "none", color: "#e9edf2", transition: "all 0.2s" }} onMouseEnter={e => e.currentTarget.style.background = "#1a1a2a"} onMouseLeave={e => e.currentTarget.style.background = "#0a0b0d"}>
              <div>📊 View Files</div>
            </a>
            <a href="/campaigns" style={{ display: "block", padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginBottom: "0.5rem", textDecoration: "none", color: "#e9edf2", transition: "all 0.2s" }} onMouseEnter={e => e.currentTarget.style.background = "#1a1a2a"} onMouseLeave={e => e.currentTarget.style.background = "#0a0b0d"}>
              <div>🎯 Campaigns</div>
            </a>
            <a href="/deliverables" style={{ display: "block", padding: "1rem", background: "#0a0b0d", borderRadius: "6px", textDecoration: "none", color: "#e9edf2", transition: "all 0.2s" }} onMouseEnter={e => e.currentTarget.style.background = "#1a1a2a"} onMouseLeave={e => e.currentTarget.style.background = "#0a0b0d"}>
              <div>📋 Deliverables</div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
