import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Agency() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/agency/dashboard`);
      if (res.ok) {
        const data = await res.json();
        setDashboard(data);
      }
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/api/agency/upload`, {
        method: "POST",
        body: formData
      });

      if (response.ok) {
        await loadData();
      }
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Agency Dashboard</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Agency Partnership Dashboard</h1>
        <button onClick={loadData} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h2>Upload Deliverables</h2>
        <div style={{ border: "2px dashed #ccc", padding: "2rem", textAlign: "center" }}>
          <input
            type="file"
            onChange={handleFileUpload}
            accept=".csv,.xlsx,.xls,.txt"
            disabled={uploading}
          />
          {uploading && <p>Uploading...</p>}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem" }}>
        <MetricCard
          title="Total Deliverables"
          value={dashboard?.total_deliverables || 0}
          subtitle="Active projects"
        />
        <MetricCard
          title="Completion Rate"
          value={`${dashboard?.completion_rate || 0}%`}
          subtitle="On-time delivery"
        />
        <MetricCard
          title="Budget Utilization"
          value={`${dashboard?.budget_utilization || 0}%`}
          subtitle="Current phase"
        />
        <MetricCard
          title="Days to Milestone"
          value={dashboard?.days_to_milestone || 0}
          subtitle="Next deadline"
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
