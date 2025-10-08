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
  const [activeTab, setActiveTab] = useState("dashboard");
  const [viewType, setViewType] = useState("both");
  const [phaseData, setPhaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasData, setHasData] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [dashboardRes, allRes] = await Promise.all([
        fetch(`${API_BASE_URL}/deliverables/dashboard`).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${API_BASE_URL}/deliverables/`).then(r => r.ok ? r.json() : { deliverables: [] }).catch(() => ({ deliverables: [] }))
      ]);
      
      setDashboard(dashboardRes);
      setDeliverables(allRes.deliverables || []);
      setHasData(allRes.deliverables && allRes.deliverables.length > 0);
    } catch (err) {
      console.error("Failed to load deliverables:", err);
      setHasData(false);
    } finally {
      setLoading(false);
    }
  }

  async function loadPhaseData(phase) {
    try {
      const phaseNum = phase.replace('phase', '');
      const res = await fetch(`${API_BASE_URL}/deliverables/by-phase/Phase ${phaseNum}`);
      if (res.ok) {
        const data = await res.json();
        setPhaseData(data);
      }
    } catch (err) {
      console.error("Failed to load phase data:", err);
    }
  }

  async function importAgencyCSV() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch(`${API_BASE_URL}/deliverables/import-agency-csv`, {
          method: 'POST',
          body: formData
        });
        
        if (!res.ok) {
          const errorText = await res.text();
          console.error('Import error response:', errorText);
          alert(`❌ Import failed: ${res.status} ${res.statusText}`);
          return;
        }
        
        const data = await res.json();
        
        if (data.success) {
          alert(`✅ Success! ${data.message || `Imported ${data.created} deliverables`}`);
          loadData();
        } else {
          alert(`❌ Error: ${data.message || 'Import failed'}`);
        }
      } catch (err) {
        console.error('Import error:', err);
        alert(`❌ Import failed: ${err.message || 'Network error - check console'}`);
      }
    };
    input.click();
  }

  async function generateBrandInputs() {
    if (!confirm('Generate brand input deliverables? This will create ~30 items.')) return;

    try {
      const res = await fetch(`${API_BASE_URL}/deliverables/generate-brand-inputs`, {
        method: 'POST'
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        console.error('Generate error response:', errorText);
        alert(`❌ Generation failed: ${res.status} ${res.statusText}`);
        return;
      }
      
      const data = await res.json();
      alert(data.message || 'Brand inputs generated!');
      loadData();
    } catch (err) {
      console.error('Generate error:', err);
      alert(`❌ Generation failed: ${err.message || 'Network error'}`);
    }
  }

  async function updateStatus(id, newStatus) {
    try {
      await fetch(`${API_BASE_URL}/deliverables/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      loadData();
      if (phaseData) {
        const phase = activeTab.replace('phase', '');
        loadPhaseData(`phase${phase}`);
      }
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  }

  useEffect(() => {
    if (activeTab.startsWith('phase')) {
      loadPhaseData(activeTab);
    }
  }, [activeTab]);

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

  const StatusBadge = ({ status }) => {
    if (!status) return <span style={{ color: "#888", fontSize: "0.75rem" }}>—</span>;
    
    const colors = {
      not_started: { bg: "#2a1a1a", color: "#ff6b6b" },
      in_progress: { bg: "#2a2310", color: "#f59e0b" },
      completed: { bg: "#1a2a1a", color: "#4ade80" },
      blocked: { bg: "#2a1a2a", color: "#a78bfa" },
      ready: { bg: "#1a2a2a", color: "#6aa6ff" }
    };
    const style = colors[status] || colors.not_started;
    return (
      <span style={{ 
        padding: "4px 12px", 
        borderRadius: "6px", 
        fontSize: "0.75rem", 
        fontWeight: "600",
        background: style.bg,
        color: style.color,
        textTransform: "uppercase"
      }}>
        {(status || '').replace(/_/g, ' ')}
      </span>
    );
  };

  const PriorityBadge = ({ priority }) => {
    if (!priority) return null;
    
    const colors = {
      high: "#ff6b6b",
      medium: "#f59e0b",
      low: "#6aa6ff"
    };
    return (
      <span style={{ color: colors[priority] || colors.medium, fontSize: "0.85rem", fontWeight: "600" }}>
        {priority === 'high' ? '🔥' : priority === 'medium' ? '⚡' : '📌'} {(priority || '').toUpperCase()}
      </span>
    );
  };

  const DeliverableCard = ({ d, showType = true }) => {
    if (!d || !d.title) return null;
    
    return (
      <div style={{ 
        background: "#1a1a1a", 
        padding: "1.5rem", 
        borderRadius: "12px", 
        border: "1px solid #2a2a2a",
        borderLeft: `3px solid ${d.deliverable_type === 'brand_input' ? '#6aa6ff' : '#4ade80'}`
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
          <div style={{ flex: 1 }}>
            {showType && d.deliverable_type && (
              <div style={{ 
                fontSize: "0.75rem", 
                color: d.deliverable_type === 'brand_input' ? '#6aa6ff' : '#4ade80',
                fontWeight: "600",
                marginBottom: "0.5rem",
                textTransform: "uppercase"
              }}>
                {d.deliverable_type === 'brand_input' ? '📤 You Deliver' : '📥 HVA Delivers'}
              </div>
            )}
            <div style={{ fontSize: "1.1rem", fontWeight: "600", color: "#e9edf2", marginBottom: "0.5rem" }}>
              {d.title}
            </div>
            {d.description && (
              <div style={{ fontSize: "0.9rem", color: "#888", marginBottom: "0.5rem" }}>
                {d.description}
              </div>
            )}
            <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
              {d.due_date && (
                <div style={{ fontSize: "0.85rem", color: "#666" }}>
                  📅 Due: {new Date(d.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </div>
              )}
              {d.priority && <PriorityBadge priority={d.priority} />}
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", alignItems: "flex-end" }}>
            <StatusBadge status={d.status} />
            <select 
              value={d.status || 'not_started'} 
              onChange={(e) => updateStatus(d.id, e.target.value)}
              style={{ 
                padding: "4px 8px", 
                background: "#0a0b0d", 
                color: "#e9edf2", 
                border: "1px solid #2a2a2a", 
                borderRadius: "6px",
                fontSize: "0.75rem",
                cursor: "pointer"
              }}
            >
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="blocked">Blocked</option>
              <option value="ready">Ready</option>
            </select>
          </div>
        </div>
        {d.blocks && Array.isArray(d.blocks) && d.blocks.length > 0 && (
          <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "0.5rem", paddingTop: "0.5rem", borderTop: "1px solid #2a2a2a" }}>
            <strong style={{ color: "#6aa6ff" }}>🔓 Unlocks:</strong> {d.blocks.join(', ')}
          </div>
        )}
        {d.assigned_to && (
          <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "0.5rem" }}>
            <strong>Assigned:</strong> {d.assigned_to}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      {/* Header */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem", color: "#e9edf2" }}>📋 Deliverables Tracker</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Two-way deliverable management: Track what you owe HVA and what they owe you</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        {/* Setup Section */}
        {!hasData && (
          <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", marginBottom: "2rem", border: "1px solid #2a2a2a" }}>
            <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>🚀 Setup Your Deliverables</h2>
            <p style={{ color: "#888", marginBottom: "1.5rem" }}>Import your agency deliverables and generate brand input requirements</p>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
              <button 
                onClick={importAgencyCSV}
                style={{ 
                  padding: "12px 24px", 
                  background: "#6aa6ff", 
                  color: "#fff", 
                  border: "none", 
                  borderRadius: "8px", 
                  cursor: "pointer",
                  fontWeight: "600"
                }}
              >
                📥 Import Agency CSV
              </button>
              <button 
                onClick={generateBrandInputs}
                style={{ 
                  padding: "12px 24px", 
                  background: "#4ade80", 
                  color: "#000", 
                  border: "none", 
                  borderRadius: "8px", 
                  cursor: "pointer",
                  fontWeight: "600"
                }}
              >
                📤 Generate Brand Inputs
              </button>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", borderBottom: "1px solid #2a2a2a", flexWrap: "wrap" }}>
          <button onClick={() => setActiveTab("dashboard")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "dashboard" ? "#6aa6ff" : "#888", borderBottom: activeTab === "dashboard" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📊 Dashboard
          </button>
          <button onClick={() => setActiveTab("phase1")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "phase1" ? "#6aa6ff" : "#888", borderBottom: activeTab === "phase1" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            Phase 1: Foundation
          </button>
          <button onClick={() => setActiveTab("phase2")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "phase2" ? "#6aa6ff" : "#888", borderBottom: activeTab === "phase2" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            Phase 2: Q4 Push
          </button>
          <button onClick={() => setActiveTab("phase3")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "phase3" ? "#6aa6ff" : "#888", borderBottom: activeTab === "phase3" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            Phase 3: Full Retainer
          </button>
          <button onClick={() => setActiveTab("all")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "all" ? "#6aa6ff" : "#888", borderBottom: activeTab === "all" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            All Deliverables
          </button>
        </div>

        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && dashboard && dashboard.stats && (
          <>
            {/* Stats Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>Total Deliverables</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{dashboard.stats.total || 0}</div>
              </div>
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #6aa6ff20", borderLeft: "3px solid #6aa6ff" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>📤 You Deliver</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#6aa6ff" }}>{dashboard.stats.brand_inputs || 0}</div>
              </div>
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #4ade8020", borderLeft: "3px solid #4ade80" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>📥 HVA Delivers</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80" }}>{dashboard.stats.agency_outputs || 0}</div>
              </div>
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #f59e0b20", borderLeft: "3px solid #f59e0b" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>In Progress</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#f59e0b" }}>{dashboard.stats.in_progress || 0}</div>
              </div>
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #4ade8020", borderLeft: "3px solid #4ade80" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>✅ Completed</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80" }}>{dashboard.stats.completed || 0}</div>
              </div>
              <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #ff6b6b20", borderLeft: "3px solid #ff6b6b" }}>
                <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>🔥 Overdue</div>
                <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#ff6b6b" }}>{dashboard.stats.overdue_count || 0}</div>
              </div>
            </div>

            {/* Overdue Items */}
            {dashboard.overdue && dashboard.overdue.length > 0 && (
              <div style={{ marginBottom: "2rem" }}>
                <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#ff6b6b" }}>🔥 OVERDUE - Immediate Action Required</h3>
                <div style={{ display: "grid", gap: "1rem" }}>
                  {dashboard.overdue.map(d => (
                    <DeliverableCard key={d.id} d={d} />
                  ))}
                </div>
              </div>
            )}

            {/* Upcoming Items */}
            {dashboard.upcoming && dashboard.upcoming.length > 0 && (
              <div>
                <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#f59e0b" }}>⏰ Coming Up (Next 7 Days)</h3>
                <div style={{ display: "grid", gap: "1rem" }}>
                  {dashboard.upcoming.map(d => (
                    <DeliverableCard key={d.id} d={d} />
                  ))}
                </div>
              </div>
            )}

            {/* Phase Progress */}
            {dashboard.phases && Object.keys(dashboard.phases).length > 0 && (
              <div style={{ marginTop: "2rem" }}>
                <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>📊 Phase Progress</h3>
                <div style={{ display: "grid", gap: "1rem" }}>
                  {Object.entries(dashboard.phases).map(([phase, stats]) => {
                    const progress = stats.total > 0 ? (stats.completed / stats.total) * 100 : 0;
                    return (
                      <div key={phase} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                          <div style={{ fontWeight: "600" }}>{phase}</div>
                          <div style={{ color: "#888" }}>{stats.completed} / {stats.total} complete</div>
                        </div>
                        <div style={{ background: "#0a0b0d", height: "8px", borderRadius: "4px", overflow: "hidden" }}>
                          <div style={{ background: "#4ade80", height: "100%", width: `${progress}%`, transition: "width 0.3s" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty Dashboard */}
        {activeTab === "dashboard" && (!dashboard || !dashboard.stats) && (
          <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📋</div>
            <h3 style={{ marginBottom: "0.5rem", color: "#e9edf2" }}>No Deliverables Yet</h3>
            <p style={{ color: "#888" }}>Import your CSV or generate brand inputs to get started</p>
          </div>
        )}

        {/* PHASE TABS */}
        {activeTab.startsWith("phase") && phaseData && (
          <>
            <div style={{ marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{phaseData.phase}</h2>
              <p style={{ color: "#888" }}>Total: {phaseData.total || 0} deliverables ({(phaseData.brand_inputs || []).length} brand inputs, {(phaseData.agency_outputs || []).length} agency outputs)</p>
            </div>

            {/* View Type Filter */}
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "2rem", background: "#1a1a1a", padding: "0.5rem", borderRadius: "8px", width: "fit-content" }}>
              <button onClick={() => setViewType("both")} style={{ padding: "0.5rem 1rem", background: viewType === "both" ? "#6aa6ff" : "transparent", color: viewType === "both" ? "#fff" : "#888", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: viewType === "both" ? "600" : "400" }}>
                Both
              </button>
              <button onClick={() => setViewType("brand_input")} style={{ padding: "0.5rem 1rem", background: viewType === "brand_input" ? "#6aa6ff" : "transparent", color: viewType === "brand_input" ? "#fff" : "#888", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: viewType === "brand_input" ? "600" : "400" }}>
                📤 Brand Inputs
              </button>
              <button onClick={() => setViewType("agency_output")} style={{ padding: "0.5rem 1rem", background: viewType === "agency_output" ? "#4ade80" : "transparent", color: viewType === "agency_output" ? "#000" : "#888", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: viewType === "agency_output" ? "600" : "400" }}>
                📥 Agency Outputs
              </button>
            </div>

            {/* Brand Inputs Section */}
            {(viewType === "both" || viewType === "brand_input") && phaseData.brand_inputs && phaseData.brand_inputs.length > 0 && (
              <div style={{ marginBottom: "2rem" }}>
                <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#6aa6ff" }}>📤 What You Need to Deliver to HVA</h3>
                <div style={{ display: "grid", gap: "1rem" }}>
                  {phaseData.brand_inputs.map(d => (
                    <DeliverableCard key={d.id} d={d} showType={false} />
                  ))}
                </div>
              </div>
            )}

            {/* Agency Outputs Section */}
            {(viewType === "both" || viewType === "agency_output") && phaseData.agency_outputs && phaseData.agency_outputs.length > 0 && (
              <div>
                <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#4ade80" }}>📥 What HVA Delivers to You</h3>
                <div style={{ display: "grid", gap: "1rem" }}>
                  {phaseData.agency_outputs.map(d => (
                    <DeliverableCard key={d.id} d={d} showType={false} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* ALL DELIVERABLES TAB */}
        {activeTab === "all" && (
          <div>
            <div style={{ marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>All Deliverables</h2>
              <p style={{ color: "#888" }}>Complete list of all deliverables across all phases</p>
            </div>

            {deliverables.length > 0 ? (
              <div style={{ display: "grid", gap: "1rem" }}>
                {deliverables.map(d => (
                  <DeliverableCard key={d.id} d={d} />
                ))}
              </div>
            ) : (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📋</div>
                <h3 style={{ marginBottom: "0.5rem", color: "#e9edf2" }}>No Deliverables Yet</h3>
                <p style={{ color: "#888" }}>Import your CSV or generate brand inputs to get started</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
