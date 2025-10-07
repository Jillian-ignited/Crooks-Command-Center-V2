import { useState, useEffect } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [priorities, setPriorities] = useState([]);
  const [quickStats, setQuickStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      
      const [overviewData, prioritiesData, statsData] = await Promise.all([
        fetch(`${API_BASE_URL}/executive/overview`).then(r => r.json()),
        fetch(`${API_BASE_URL}/executive/priorities`).then(r => r.json()),
        fetch(`${API_BASE_URL}/executive/quick-stats`).then(r => r.json())
      ]);
      
      setOverview(overviewData);
      setPriorities(prioritiesData.priorities || []);
      setQuickStats(statsData);
      setError("");
    } catch (err) {
      console.error("Failed to load dashboard:", err);
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ 
        minHeight: "100vh", 
        background: "#0a0b0d", 
        color: "#e9edf2",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading command center...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: "100vh", 
      background: "#0a0b0d", 
      color: "#e9edf2",
      padding: "2rem"
    }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
            Command Center
          </h1>
          <p style={{ color: "#888" }}>
            Crooks & Castles Intelligence Dashboard
          </p>
        </div>

        {error && (
          <div style={{ 
            padding: "1rem", 
            background: "#2a1a1a", 
            borderRadius: "8px", 
            color: "#ff6b6b",
            marginBottom: "2rem"
          }}>
            {error}
          </div>
        )}

        <div style={{ 
          background: "#1a1a1a", 
          padding: "2rem", 
          borderRadius: "12px",
          border: "1px solid #2a2a2a",
          marginBottom: "2rem"
        }}>
          <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
            🎯 Top Priorities This Week
          </h2>
          <div style={{ display: "grid", gap: "1rem" }}>
            {priorities.map((priority, idx) => (
              <div 
                key={priority.id}
                style={{ 
                  background: "#0a0b0d", 
                  padding: "1.5rem", 
                  borderRadius: "8px",
                  border: "1px solid #2a2a2a"
                }}
              >
                <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                  <div style={{ 
                    fontSize: "1.5rem", 
                    fontWeight: "bold",
                    color: "#6aa6ff",
                    minWidth: "2rem"
                  }}>
                    {idx + 1}.
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
                      {priority.title}
                    </h3>
                    <p style={{ color: "#888", marginBottom: "1rem" }}>
                      {priority.description}
                    </p>
                    <a 
                      href={priority.link}
                      style={{ 
                        display: "inline-block",
                        padding: "8px 16px",
                        background: "#2a2a2a",
                        color: "#6aa6ff",
                        borderRadius: "6px",
                        textDecoration: "none",
                        fontSize: "0.9rem",
                        fontWeight: "600"
                      }}
                    >
                      {priority.action} &rarr;
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {quickStats && (
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "1rem",
            marginBottom: "2rem"
          }}>
            <StatCard 
              icon="💰"
              title="Revenue"
              value={`$${quickStats.revenue.current.toLocaleString()}`}
              change={quickStats.revenue.change}
              period={quickStats.revenue.period}
            />
            <StatCard 
              icon="👥"
              title="Customers"
              value={quickStats.customers.current.toLocaleString()}
              change={quickStats.customers.change}
              period={quickStats.customers.period}
            />
            <StatCard 
              icon="📦"
              title="Orders"
              value={quickStats.orders.current.toLocaleString()}
              change={quickStats.orders.change}
              period={quickStats.orders.period}
            />
            <StatCard 
              icon="💵"
              title="Avg Order"
              value={`$${quickStats.avg_order_value.current}`}
              change={quickStats.avg_order_value.change}
              period={quickStats.avg_order_value.period}
            />
          </div>
        )}

        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: "2rem"
        }}>
          <div style={{ 
            background: "#1a1a1a", 
            padding: "1.5rem", 
            borderRadius: "12px",
            border: "1px solid #2a2a2a"
          }}>
            <div style={{ 
              display: "flex", 
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "1.5rem"
            }}>
              <h2 style={{ fontSize: "1.2rem" }}>📊 Recent Intelligence</h2>
              <a href="/intelligence" style={{ color: "#6aa6ff", fontSize: "0.9rem", textDecoration: "none" }}>
                View All &rarr;
              </a>
            </div>
            
            {overview && overview.recent_files && overview.recent_files.length > 0 ? (
              <div style={{ display: "grid", gap: "0.75rem" }}>
                {overview.recent_files.map(file => (
                  <div 
                    key={file.id}
                    style={{ 
                      padding: "1rem",
                      background: "#0a0b0d",
                      borderRadius: "6px",
                      fontSize: "0.9rem"
                    }}
                  >
                    <div style={{ fontWeight: "600", marginBottom: "0.25rem" }}>
                      {file.filename}
                    </div>
                    <div style={{ fontSize: "0.85rem", color: "#888" }}>
                      {file.source} &bull; {new Date(file.uploaded_at).toLocaleDateString()}
                      {file.has_analysis && (
                        <span style={{ color: "#4ade80", marginLeft: "0.5rem" }}>
                          ✓ Analyzed
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "2rem", color: "#888" }}>
                <p style={{ marginBottom: "1rem" }}>No files uploaded yet</p>
                <a href="/upload" style={{ color: "#6aa6ff", textDecoration: "none" }}>
                  Upload your first file &rarr;
                </a>
              </div>
            )}

            {overview && overview.stats && (
              <div style={{ 
                marginTop: "1.5rem",
                paddingTop: "1rem",
                borderTop: "1px solid #2a2a2a",
                fontSize: "0.9rem",
                color: "#888"
              }}>
                {overview.stats.total_files} total files &bull; {overview.stats.this_week} this week
              </div>
            )}
          </div>

          <div style={{ 
            background: "#1a1a1a", 
            padding: "1.5rem", 
            borderRadius: "12px",
            border: "1px solid #2a2a2a"
          }}>
            <h2 style={{ fontSize: "1.2rem", marginBottom: "1.5rem" }}>
              ⚡ Quick Actions
            </h2>
            <div style={{ display: "grid", gap: "0.75rem" }}>
              <ActionButton 
                href="/upload"
                icon="📤"
                title="Upload Intelligence"
                description="Upload Apify, Shopify, or Manus data"
              />
              <ActionButton 
                href="/campaigns"
                icon="📅"
                title="Plan Campaign"
                description="Create new campaign with deliverables"
              />
              <ActionButton 
                href="/competitive"
                icon="🏆"
                title="View Competition"
                description="C&C vs top 30 streetwear brands"
              />
              <ActionButton 
                href="/shopify"
                icon="💰"
                title="Check Performance"
                description="See how campaigns impact sales"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, change, period }) {
  const isPositive = change > 0;
  const isNegative = change < 0;
  
  return (
    <div style={{ 
      background: "#1a1a1a", 
      padding: "1.5rem", 
      borderRadius: "12px",
      border: "1px solid #2a2a2a"
    }}>
      <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{icon}</div>
      <div style={{ fontSize: "0.85rem", color: "#888", marginBottom: "0.5rem" }}>
        {title}
      </div>
      <div style={{ fontSize: "1.8rem", fontWeight: "bold", marginBottom: "0.5rem" }}>
        {value}
      </div>
      <div style={{ fontSize: "0.85rem" }}>
        <span style={{ 
          color: isPositive ? "#4ade80" : isNegative ? "#ff6b6b" : "#888",
          fontWeight: "600"
        }}>
          {isPositive ? "↑" : isNegative ? "↓" : ""} {Math.abs(change)}%
        </span>
        <span style={{ color: "#888", marginLeft: "0.5rem" }}>
          {period}
        </span>
      </div>
    </div>
  );
}

function ActionButton({ href, icon, title, description }) {
  return (
    
      href={href}
      style={{ 
        display: "block",
        padding: "1rem",
        background: "#0a0b0d",
        border: "1px solid transparent",
        borderRadius: "6px",
        textDecoration: "none",
        color: "inherit"
      }}
    >
      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <div style={{ fontSize: "1.5rem" }}>{icon}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: "600", marginBottom: "0.25rem" }}>
            {title}
          </div>
          <div style={{ fontSize: "0.85rem", color: "#888" }}>
            {description}
          </div>
        </div>
        <div style={{ color: "#6aa6ff" }}>&rarr;</div>
      </div>
    </a>
  );
}
