import { useState, useEffect } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      
      // Load comprehensive summary from new endpoint
      const res = await fetch(`${API_BASE_URL}/summary/dashboard`);
      const data = await res.json();
      
      setSummary(data);
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
          <div>Loading command center...</div>
        </div>
      </div>
    );
  }

  const shopify = summary?.shopify || {};
  const hasShopifyData = shopify.total_orders > 0 || shopify.total_revenue > 0;

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: "2rem" }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        {/* Header */}
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem", color: "#e9edf2" }}>
            Crooks Command Center
          </h1>
          <p style={{ color: "#888" }}>Intelligence-driven brand management for Crooks & Castles</p>
        </div>

        {/* AI Insights Banner */}
        {summary?.insights && summary.insights.length > 0 && (
          <div style={{ marginBottom: "2rem" }}>
            {summary.insights.map((insight, idx) => (
              <div
                key={idx}
                style={{
                  background: insight.type === 'alert' ? '#2a1a1a' : insight.type === 'positive' ? '#1a2a1a' : '#1a1a2a',
                  border: `1px solid ${insight.type === 'alert' ? '#ef4444' : insight.type === 'positive' ? '#4ade80' : '#6aa6ff'}`,
                  padding: "1rem",
                  borderRadius: "12px",
                  marginBottom: "0.5rem"
                }}
              >
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "0.5rem",
                  marginBottom: "0.25rem"
                }}>
                  <span style={{ fontSize: "1.2rem" }}>
                    {insight.type === 'alert' ? '⚠️' : insight.type === 'positive' ? '✅' : 'ℹ️'}
                  </span>
                  <strong style={{ color: "#e9edf2" }}>{insight.title}</strong>
                </div>
                <div style={{ color: "#a1a8b3", fontSize: "0.9rem", marginLeft: "1.7rem" }}>
                  {insight.description}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Key Metrics - Shopify Performance */}
        {hasShopifyData ? (
          <>
            <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#e9edf2" }}>
              📊 Performance ({shopify.period})
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
              {/* Revenue */}
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem" }}>💰 Revenue</div>
                  {shopify.revenue_change_percent !== 0 && (
                    <span style={{ 
                      fontSize: "0.85rem", 
                      color: shopify.revenue_change_percent > 0 ? "#4ade80" : "#ff6b6b",
                      background: shopify.revenue_change_percent > 0 ? "#1a2a1a" : "#2a1a1a",
                      padding: "2px 8px",
                      borderRadius: "12px"
                    }}>
                      {shopify.revenue_change_percent > 0 ? "↑" : "↓"} {Math.abs(shopify.revenue_change_percent)}%
                    </span>
                  )}
                </div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                  ${shopify.total_revenue?.toLocaleString() || 0}
                </div>
              </div>

              {/* Orders */}
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                  <div style={{ color: "#888", fontSize: "0.9rem" }}>📦 Orders</div>
                  {shopify.orders_change_percent !== 0 && (
                    <span style={{ 
                      fontSize: "0.85rem", 
                      color: shopify.orders_change_percent > 0 ? "#4ade80" : "#ff6b6b",
                      background: shopify.orders_change_percent > 0 ? "#1a2a1a" : "#2a1a1a",
                      padding: "2px 8px",
                      borderRadius: "12px"
                    }}>
                      {shopify.orders_change_percent > 0 ? "↑" : "↓"} {Math.abs(shopify.orders_change_percent)}%
                    </span>
                  )}
                </div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                  {shopify.total_orders?.toLocaleString() || 0}
                </div>
              </div>

              {/* AOV */}
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "1rem" }}>💵 Avg Order Value</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                  ${shopify.avg_order_value?.toLocaleString() || 0}
                </div>
              </div>

              {/* Sessions */}
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "1rem" }}>👁️ Sessions</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                  {shopify.total_sessions?.toLocaleString() || 0}
                </div>
              </div>

              {/* Conversion Rate */}
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "1rem" }}>📈 Conversion Rate</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>
                  {shopify.avg_conversion_rate?.toFixed(2) || 0}%
                </div>
              </div>
            </div>
          </>
        ) : (
          <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", marginBottom: "2rem", textAlign: "center", border: "1px solid #2a2a2a" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📊</div>
            <h3 style={{ color: "#e9edf2", marginBottom: "0.5rem" }}>No Shopify Data Yet</h3>
            <p style={{ color: "#888", marginBottom: "1.5rem" }}>Upload your Shopify analytics to see metrics</p>
            <a href="/shopify" style={{ padding: "10px 20px", background: "#6aa6ff", color: "#fff", borderRadius: "6px", textDecoration: "none", display: "inline-block" }}>
              Go to Shopify
            </a>
          </div>
        )}

        {/* Three Column Layout */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1.5rem", marginBottom: "2rem" }}>
          {/* Intelligence Module */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h3 style={{ color: "#e9edf2", fontSize: "1.1rem" }}>📊 Intelligence</h3>
              <span style={{ 
                background: "#2a2a3a", 
                color: "#6aa6ff", 
                padding: "4px 12px", 
                borderRadius: "12px",
                fontSize: "0.9rem",
                fontWeight: "600"
              }}>
                {summary?.intelligence?.total_entries || 0}
              </span>
            </div>
            
            {summary?.intelligence?.by_category && Object.keys(summary.intelligence.by_category).length > 0 ? (
              <div style={{ marginBottom: "1rem" }}>
                {Object.entries(summary.intelligence.by_category).map(([cat, count]) => (
                  <div key={cat} style={{ 
                    display: "flex", 
                    justifyContent: "space-between",
                    padding: "0.5rem 0",
                    borderBottom: "1px solid #2a2a2a"
                  }}>
                    <span style={{ color: "#a1a8b3", textTransform: "capitalize" }}>{cat}</span>
                    <span style={{ color: "#6aa6ff", fontWeight: "600" }}>{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: "#666", fontSize: "0.9rem" }}>No intelligence files yet</p>
            )}
            
            <a href="/intelligence" style={{ 
              display: "block", 
              textAlign: "center",
              padding: "0.75rem", 
              background: "#2a2a3a", 
              color: "#6aa6ff",
              borderRadius: "8px",
              textDecoration: "none",
              marginTop: "1rem",
              fontSize: "0.9rem",
              fontWeight: "600"
            }}>
              View All →
            </a>
          </div>

          {/* Competitive Module */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h3 style={{ color: "#e9edf2", fontSize: "1.1rem" }}>🎯 Competitive</h3>
              <span style={{ 
                background: "#2a2a3a", 
                color: "#6aa6ff", 
                padding: "4px 12px", 
                borderRadius: "12px",
                fontSize: "0.9rem",
                fontWeight: "600"
              }}>
                {summary?.competitive?.total_competitors || 0}
              </span>
            </div>
            
            {summary?.competitive?.total_intel_entries > 0 ? (
              <>
                <div style={{ marginBottom: "1rem" }}>
                  <div style={{ 
                    display: "flex", 
                    justifyContent: "space-between",
                    padding: "0.5rem 0",
                    borderBottom: "1px solid #2a2a2a"
                  }}>
                    <span style={{ color: "#a1a8b3" }}>Total Intel</span>
                    <span style={{ color: "#6aa6ff", fontWeight: "600" }}>
                      {summary.competitive.total_intel_entries}
                    </span>
                  </div>
                  
                  {summary?.competitive?.by_category && Object.entries(summary.competitive.by_category).map(([cat, count]) => (
                    <div key={cat} style={{ 
                      display: "flex", 
                      justifyContent: "space-between",
                      padding: "0.5rem 0",
                      borderBottom: "1px solid #2a2a2a"
                    }}>
                      <span style={{ color: "#a1a8b3", textTransform: "capitalize" }}>{cat}</span>
                      <span style={{ color: "#6aa6ff", fontWeight: "600" }}>{count}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p style={{ color: "#666", fontSize: "0.9rem" }}>No competitive intel yet</p>
            )}
            
            <a href="/competitive" style={{ 
              display: "block", 
              textAlign: "center",
              padding: "0.75rem", 
              background: "#2a2a3a", 
              color: "#6aa6ff",
              borderRadius: "8px",
              textDecoration: "none",
              marginTop: "1rem",
              fontSize: "0.9rem",
              fontWeight: "600"
            }}>
              View Intel →
            </a>
          </div>

          {/* Agency Deliverables */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h3 style={{ color: "#e9edf2", fontSize: "1.1rem" }}>📋 Deliverables</h3>
              {summary?.agency?.overdue > 0 && (
                <span style={{ 
                  background: "#2a1a1a", 
                  color: "#ef4444", 
                  padding: "4px 12px", 
                  borderRadius: "12px",
                  fontSize: "0.9rem",
                  fontWeight: "600"
                }}>
                  {summary.agency.overdue} overdue
                </span>
              )}
            </div>
            
            {summary?.agency?.total_deliverables > 0 ? (
              <div style={{ marginBottom: "1rem" }}>
                {summary?.agency?.by_status && Object.entries(summary.agency.by_status).map(([status, count]) => (
                  <div key={status} style={{ 
                    display: "flex", 
                    justifyContent: "space-between",
                    padding: "0.5rem 0",
                    borderBottom: "1px solid #2a2a2a"
                  }}>
                    <span style={{ color: "#a1a8b3", textTransform: "capitalize" }}>
                      {status.replace('_', ' ')}
                    </span>
                    <span style={{ 
                      color: status === 'completed' ? '#4ade80' : '#6aa6ff', 
                      fontWeight: "600" 
                    }}>
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: "#666", fontSize: "0.9rem" }}>No deliverables tracked yet</p>
            )}
            
            <a href="/deliverables" style={{ 
              display: "block", 
              textAlign: "center",
              padding: "0.75rem", 
              background: "#2a2a3a", 
              color: "#6aa6ff",
              borderRadius: "8px",
              textDecoration: "none",
              marginTop: "1rem",
              fontSize: "0.9rem",
              fontWeight: "600"
            }}>
              Manage →
            </a>
          </div>
        </div>

        {/* Recent Activity */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
          {/* Recent Intelligence */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <h3 style={{ marginBottom: "1rem", color: "#e9edf2", fontSize: "1.1rem" }}>
              📊 Recent Intelligence
            </h3>
            {summary?.intelligence?.recent && summary.intelligence.recent.length > 0 ? (
              summary.intelligence.recent.map(item => (
                <div key={item.id} style={{ 
                  padding: "0.75rem", 
                  background: "#0a0b0d", 
                  borderRadius: "8px", 
                  marginBottom: "0.5rem",
                  border: "1px solid #2a2a2a"
                }}>
                  <div style={{ fontWeight: "600", color: "#e9edf2", marginBottom: "0.25rem" }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#888" }}>
                    {item.category} • {new Date(item.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: "#666" }}>No recent intelligence</p>
            )}
          </div>

          {/* Upcoming Due */}
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <h3 style={{ marginBottom: "1rem", color: "#e9edf2", fontSize: "1.1rem" }}>
              ⏰ Upcoming Deliverables
            </h3>
            {summary?.agency?.upcoming_due && summary.agency.upcoming_due.length > 0 ? (
              summary.agency.upcoming_due.map(item => (
                <div key={item.id} style={{ 
                  padding: "0.75rem", 
                  background: "#0a0b0d", 
                  borderRadius: "8px", 
                  marginBottom: "0.5rem",
                  border: "1px solid #2a2a2a"
                }}>
                  <div style={{ fontWeight: "600", color: "#e9edf2", marginBottom: "0.25rem" }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#888" }}>
                    Due: {new Date(item.due_date).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: "#666" }}>No upcoming deliverables</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
