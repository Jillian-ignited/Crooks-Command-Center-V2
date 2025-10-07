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
          <div>Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: "2rem" }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        <h1>Command Center</h1>
        <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", marginBottom: "2rem" }}>
          <h2>🎯 Priorities</h2>
          {priorities.map((p, i) => (
            <div key={p.id} style={{ background: "#0a0b0d", padding: "1rem", borderRadius: "8px", marginBottom: "1rem" }}>
              <h3>{i + 1}. {p.title}</h3>
              <p style={{ color: "#888" }}>{p.description}</p>
              <a href={p.link} style={{ color: "#6aa6ff" }}>{p.action}</a>
            </div>
          ))}
        </div>
        {quickStats && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
              <div>💰 Revenue</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>${quickStats.revenue.current.toLocaleString()}</div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
              <div>👥 Customers</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{quickStats.customers.current.toLocaleString()}</div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
              <div>📦 Orders</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{quickStats.orders.current.toLocaleString()}</div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
              <div>💵 AOV</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>${quickStats.avg_order_value.current}</div>
            </div>
          </div>
        )}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
            <h2>📊 Recent Intelligence</h2>
            {overview && overview.recent_files && overview.recent_files.length > 0 ? (
              overview.recent_files.map(f => (
                <div key={f.id} style={{ padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginBottom: "0.5rem" }}>
                  <div style={{ fontWeight: "600" }}>{f.filename}</div>
                  <div style={{ fontSize: "0.85rem", color: "#888" }}>{f.source}</div>
                </div>
              ))
            ) : (
              <p style={{ color: "#888" }}>No files yet</p>
            )}
          </div>
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
            <h2>⚡ Quick Actions</h2>
            <a href="/upload" style={{ display: "block", padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginBottom: "0.5rem", textDecoration: "none", color: "inherit" }}>
              <div>📤 Upload Intelligence</div>
            </a>
            <a href="/intelligence" style={{ display: "block", padding: "1rem", background: "#0a0b0d", borderRadius: "6px", textDecoration: "none", color: "inherit" }}>
              <div>📊 View Files</div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
