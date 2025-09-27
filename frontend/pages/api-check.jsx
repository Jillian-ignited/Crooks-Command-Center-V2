import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function ApiCheck() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [routes, setRoutes] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        
        // Check health endpoint
        const healthRes = await apiGet("/health");
        setHealthStatus(healthRes);
        
        // Get available routes
        const routesRes = await apiGet("/routes");
        setRoutes(routesRes);
        
      } catch (e) {
        setErr(e?.message || String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const testEndpoint = async (path) => {
    try {
      const response = await fetch(path);
      const data = await response.json();
      alert(`✅ ${path}\nStatus: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`);
    } catch (e) {
      alert(`❌ ${path}\nError: ${e.message}`);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", padding: 16, fontFamily: 'system-ui' }}>
      <div style={{ marginBottom: 24 }}>
        <a href="/" style={{ color: '#3B82F6', textDecoration: 'none' }}>← Back to Home</a>
      </div>
      
      <h1 style={{ color: '#1F2937', marginBottom: 24 }}>🔧 API Health Check & Testing</h1>
      
      {loading && <div style={{ padding: 20, textAlign: 'center' }}>Loading...</div>}
      
      {err && (
        <div style={{ padding: 16, background: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 8, marginBottom: 24 }}>
          <h3 style={{ color: '#DC2626', margin: '0 0 8px 0' }}>❌ Error</h3>
          <pre style={{ color: '#DC2626', margin: 0, whiteSpace: 'pre-wrap' }}>{err}</pre>
        </div>
      )}

      {healthStatus && (
        <div style={{ padding: 16, background: '#D1FAE5', border: '1px solid #A7F3D0', borderRadius: 8, marginBottom: 24 }}>
          <h3 style={{ color: '#065F46', margin: '0 0 8px 0' }}>✅ Health Status</h3>
          <pre style={{ color: '#065F46', margin: 0 }}>{JSON.stringify(healthStatus, null, 2)}</pre>
        </div>
      )}

      {routes && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ color: '#1F2937', marginBottom: 16 }}>🛣️ Available API Routes</h3>
          <div style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: 8, padding: 16 }}>
            <div style={{ marginBottom: 16 }}>
              <strong>Total Routes: {routes.routes?.length || 0}</strong>
            </div>
            
            <div style={{ display: 'grid', gap: 8 }}>
              {routes.routes?.map((route, index) => (
                <div key={index} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 12px',
                  background: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: 4
                }}>
                  <div>
                    <code style={{ color: '#1F2937', fontWeight: 'bold' }}>{route.path}</code>
                    <span style={{ color: '#6B7280', marginLeft: 8 }}>
                      [{route.methods?.join(', ') || 'N/A'}]
                    </span>
                  </div>
                  {route.methods?.includes('GET') && (
                    <button 
                      onClick={() => testEndpoint(route.path)}
                      style={{
                        padding: '4px 8px',
                        background: '#3B82F6',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        cursor: 'pointer',
                        fontSize: 12
                      }}
                    >
                      Test
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div style={{ padding: 16, background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: 8 }}>
        <h3 style={{ color: '#92400E', margin: '0 0 12px 0' }}>🧪 Quick Tests</h3>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button onClick={() => testEndpoint('/api/health')} style={{ padding: '8px 12px', background: '#10B981', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Test Health
          </button>
          <button onClick={() => testEndpoint('/intelligence/summary')} style={{ padding: '8px 12px', background: '#8B5CF6', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Test Intelligence
          </button>
          <button onClick={() => testEndpoint('/agency/dashboard')} style={{ padding: '8px 12px', background: '#F59E0B', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Test Agency
          </button>
          <button onClick={() => testEndpoint('/content/dashboard')} style={{ padding: '8px 12px', background: '#EF4444', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Test Content
          </button>
        </div>
      </div>
    </div>
  );
}
