// frontend/pages/agency.jsx
import { useEffect, useState } from "react";

const API = typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_API_BASE || "") : "";

export default function Agency() {
  const [dashboard, setDashboard] = useState(null);
  const [deliverables, setDeliverables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    if (typeof window === 'undefined') return;
    
    setLoading(true);
    setError(null);

    try {
      const [dashRes, delivRes] = await Promise.all([
        fetch(`${API}/api/agency/dashboard`),
        fetch(`${API}/api/agency/deliverables`)
      ]);
      
      if (dashRes.ok) {
        const dashData = await dashRes.json();
        setDashboard(dashData);
      }
      
      if (delivRes.ok) {
        const delivData = await delivRes.json();
        setDeliverables(delivData.deliverables || []);
      }
    } catch (err) {
      console.error('Failed to load agency data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      loadData();
    }
  }, []);

  if (loading && typeof window !== 'undefined') {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Agency Dashboard</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Agency Dashboard</h1>

      {error && (
        <div style={{ background: '#fee', border: '1px solid #f99', padding: '1rem', borderRadius: 8, marginBottom: '1rem' }}>
          Error: {error}
        </div>
      )}

      {dashboard && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
            <div style={{ fontSize: "0.85rem", color: "#888" }}>Active Projects</div>
            <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{dashboard.active_projects || 0}</div>
          </div>
          
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
            <div style={{ fontSize: "0.85rem", color: "#888" }}>Total Deliverables</div>
            <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{dashboard.total_deliverables || 0}</div>
          </div>
          
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
            <div style={{ fontSize: "0.85rem", color: "#888" }}>Completion Rate</div>
            <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{dashboard.completion_rate || 0}%</div>
          </div>
        </div>
      )}

      <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
        <h2>Recent Deliverables</h2>
        {deliverables.length > 0 ? (
          <div style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
            {deliverables.map((item, i) => (
              <div key={i} style={{ padding: "0.75rem", background: "#2a2a2a", borderRadius: "6px" }}>
                <div style={{ fontWeight: "bold" }}>{item.title || item.name}</div>
                <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "0.25rem" }}>
                  Status: {item.status} | Due: {item.due_date || 'TBD'}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: "#666", marginTop: "1rem" }}>No deliverables found</p>
        )}
      </div>
    </div>
  );
}
