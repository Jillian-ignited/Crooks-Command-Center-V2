import { useEffect, useState } from "react";
import AgencyDeliverables from "../components/AgencyDeliverables";

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function AgencyPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAgencyData = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API}/agency/dashboard`);
      
      if (!res.ok) {
        throw new Error(`Failed to load agency data: HTTP ${res.status}`);
      }
      
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error('Failed to load agency data:', err);
      setError(`Unable to load agency dashboard: ${err.message}`);
      
      // Set fallback data for development/testing
      setData({
        week_of: new Date().toISOString().split('T')[0],
        deliverables: [
          {
            title: "Unable to load deliverables",
            status: "error",
            owner: "System",
            due: "Check backend connection"
          }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgencyData();
  }, []);

  if (loading) {
    return (
      <div className="grid">
        <div className="card">
          <h3 className="title">Agency Dashboard</h3>
          <div className="muted">Loading agency data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid">
      {/* Error Display */}
      {error && (
        <div className="card" style={{ border: '1px solid var(--warn)', background: 'rgba(245, 158, 11, 0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="title" style={{ color: 'var(--warn)', margin: '0 0 8px 0' }}>Connection Issue</h3>
              <div style={{ color: 'var(--warn)' }}>{error}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
                Showing fallback data. Check that the backend server is running.
              </div>
            </div>
            <button 
              className="button" 
              onClick={() => {
                setError(null);
                loadAgencyData();
              }}
              style={{ background: 'var(--warn)', minWidth: 'auto', padding: '6px 12px' }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Control Panel */}
      <div className="card">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <h3 className="title" style={{ margin: 0 }}>Agency Dashboard</h3>
          <button 
            className="button" 
            onClick={loadAgencyData}
            disabled={loading}
            style={{ minWidth: 'auto' }}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        <div className="muted" style={{ marginTop: 8 }}>
          Project deliverables and tracking dashboard
        </div>
      </div>

      {/* Agency Deliverables Component */}
      <AgencyDeliverables data={data} />

      {/* Additional Agency Info */}
      {data && (
        <div className="card">
          <h3 className="title">Quick Stats</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12 }}>
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: 'var(--brand)' }}>
                {data.deliverables?.length || 0}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Total Deliverables</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: 'var(--ok)' }}>
                {data.deliverables?.filter(d => d.status === 'completed').length || 0}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Completed</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: 'var(--warn)' }}>
                {data.deliverables?.filter(d => d.status === 'in-progress').length || 0}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>In Progress</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: 'var(--danger)' }}>
                {data.deliverables?.filter(d => d.status === 'overdue').length || 0}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>Overdue</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
