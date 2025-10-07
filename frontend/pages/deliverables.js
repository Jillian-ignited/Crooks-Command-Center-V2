import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function DeliverablesPage() {
  const [deliverables, setDeliverables] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [selectedPhase, setSelectedPhase] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [selectedPhase, selectedStatus]);

  async function loadData() {
    try {
      setLoading(true);
      
      // Build query params
      const params = new URLSearchParams();
      if (selectedPhase !== "all") params.append("phase", selectedPhase);
      if (selectedStatus !== "all") params.append("status", selectedStatus);
      
      const [deliverablesRes, dashboardRes] = await Promise.all([
        fetch(`${API_BASE_URL}/deliverables/?${params}`).then(r => r.json()),
        fetch(`${API_BASE_URL}/deliverables/dashboard`).then(r => r.json())
      ]);
      
      setDeliverables(deliverablesRes.deliverables || []);
      setDashboard(dashboardRes);
    } catch (err) {
      console.error("Failed to load:", err);
    } finally {
      setLoading(false);
    }
  }

  async function updateStatus(deliverableId, newStatus) {
    try {
      const response = await fetch(`${API_BASE_URL}/deliverables/${deliverableId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ status: newStatus })
      });
      
      if (response.ok) {
        loadData(); // Reload data
      }
    } catch (err) {
      console.error("Failed to update:", err);
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading deliverables...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      {/* Header */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem" }}>📋 Deliverables</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Track High Voltage Digital tasks and asset requirements</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        {/* Dashboard Stats */}
        {dashboard && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Total Tasks</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{dashboard.total_deliverables}</div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Complete</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80" }}>{dashboard.by_status.complete}</div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Upcoming</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#6aa6ff" }}>{dashboard.upcoming_count}</div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Overdue</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ff6b6b" }}>{dashboard.overdue_count}</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", padding: "1rem", background: "#1a1a1a", borderRadius: "8px" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontSize: "0.9rem", color: "#888" }}>Phase</label>
            <select value={selectedPhase} onChange={(e) => setSelectedPhase(e.target.value)} style={{ width: "100%", padding: "8px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2" }}>
              <option value="all">All Phases</option>
              <option value="Phase 1">Phase 1 - Foundation</option>
              <option value="Phase 2">Phase 2 - Growth</option>
              <option value="Phase 3">Phase 3 - Full Retainer</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontSize: "0.9rem", color: "#888" }}>Status</label>
            <select value={selectedStatus} onChange={(e) => setSelectedStatus(e.target.value)} style={{ width: "100%", padding: "8px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2" }}>
              <option value="all">All Statuses</option>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="complete">Complete</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
        </div>

        {/* Deliverables List */}
        {deliverables.length === 0 ? (
          <div style={{ textAlign: "center", padding: "4rem 2rem", background: "#1a1a1a", borderRadius: "12px" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📋</div>
            <h2 style={{ marginBottom: "1rem" }}>No deliverables found</h2>
            <p style={{ color: "#888" }}>Try changing your filters or import your CSV</p>
          </div>
        ) : (
          <div style={{ display: "grid", gap: "1rem" }}>
            {deliverables.map(d => (
              <div key={d.id} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "0.5rem" }}>
                      <span style={{ padding: "2px 8px", background: "#0a0b0d", borderRadius: "4px", fontSize: "0.75rem", color: "#6aa6ff" }}>
                        {d.phase}
                      </span>
                      <span style={{ padding: "2px 8px", background: "#0a0b0d", borderRadius: "4px", fontSize: "0.75rem" }}>
                        {d.category}
                      </span>
                    </div>
                    <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>{d.task}</h3>
                    {d.due_date && (
                      <div style={{ fontSize: "0.9rem", color: "#888" }}>
                        📅 Due: {new Date(d.due_date).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <select 
                    value={d.status} 
                    onChange={(e) => updateStatus(d.id, e.target.value)}
                    style={{ 
                      padding: "6px 12px", 
                      background: d.status === "complete" ? "#1a2a1a" : d.status === "in_progress" ? "#1a1a2a" : d.status === "blocked" ? "#2a1a1a" : "#0a0b0d",
                      color: d.status === "complete" ? "#4ade80" : d.status === "in_progress" ? "#6aa6ff" : d.status === "blocked" ? "#ff6b6b" : "#888",
                      border: "1px solid #2a2a2a",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "0.9rem"
                    }}
                  >
                    <option value="not_started">Not Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="complete">Complete</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>

                {d.asset_requirements && (
                  <div style={{ padding: "1rem", background: "#0a0b0d", borderRadius: "6px", marginTop: "1rem" }}>
                    <div style={{ fontSize: "0.85rem", color: "#888", marginBottom: "0.5rem" }}>📦 Asset Requirements:</div>
                    <div style={{ fontSize: "0.9rem", lineHeight: "1.6" }}>{d.asset_requirements}</div>
                  </div>
                )}

                {d.owner && (
                  <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "1rem" }}>
                    👤 Owner: {d.owner}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
