import { useState, useEffect } from "react";
import Head from 'next/head';

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function HomePage() {
  const [systemHealth, setSystemHealth] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Load system status and health information
  const loadSystemStatus = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load health check
      const healthRes = await fetch(`${API}/health`);
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setSystemHealth(healthData);
      }

      // Load API status
      const statusRes = await fetch(`${API}/api/status`);
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setApiStatus(statusData);
      }

      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to load system status:', err);
      setError('Unable to connect to backend services');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSystemStatus();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Calculate system health score
  const getHealthScore = () => {
    if (!systemHealth || !systemHealth.modules) return 0;
    
    const modules = Object.values(systemHealth.modules);
    const operational = modules.filter(status => 
      status === 'operational' || status.includes('operational')
    ).length;
    
    return Math.round((operational / modules.length) * 100);
  };

  // Get status color based on health
  const getStatusColor = (status) => {
    if (status === 'operational' || status.includes('operational')) return 'var(--ok)';
    if (status.includes('enhanced') || status.includes('new')) return 'var(--brand)';
    return 'var(--warn)';
  };

  return (
    <div>
      <Head>
        <title>Crooks & Castles Command Center V2</title>
        <meta name="description" content="Competitive intelligence and revenue analytics platform" />
      </Head>

      <div className="grid">
        {/* Header Section */}
        <div className="card" style={{ 
          background: 'linear-gradient(135deg, rgba(106, 166, 255, 0.1), rgba(142, 123, 255, 0.1))',
          border: '1px solid var(--brand)'
        }}>
          <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ 
                fontSize: 28, 
                fontWeight: 'bold', 
                margin: '0 0 8px 0',
                background: 'linear-gradient(135deg, var(--brand), var(--brand-2))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                🏴‍☠️ Crooks & Castles Command Center
              </h1>
              <div className="muted">
                Competitive Intelligence & Revenue Analytics Platform v2.1.0
              </div>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: getHealthScore() > 70 ? 'var(--ok)' : 'var(--warn)' }}>
                {loading ? '--' : `${getHealthScore()}%`}
              </div>
              <div className="muted" style={{ fontSize: 12 }}>System Health</div>
              {lastUpdate && (
                <div className="muted" style={{ fontSize: 10 }}>
                  Updated: {lastUpdate}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* System Status Overview */}
        <div className="card">
          <div className="row" style={{ justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 className="title" style={{ margin: 0 }}>System Status</h3>
            <button 
              className="button" 
              onClick={loadSystemStatus}
              disabled={loading}
              style={{ minWidth: 'auto', padding: '6px 12px' }}
            >
              {loading ? 'Checking...' : 'Refresh'}
            </button>
          </div>

          {error && (
            <div style={{ 
              padding: 12, 
              background: 'rgba(239, 68, 68, 0.1)', 
              border: '1px solid var(--danger)',
              borderRadius: 8,
              marginBottom: 16
            }}>
              <div style={{ color: 'var(--danger)', fontWeight: 'bold' }}>Connection Error</div>
              <div className="muted">{error}</div>
            </div>
          )}

          {systemHealth && (
            <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {Object.entries(systemHealth.modules).map(([module, status]) => (
                <div key={module} style={{
                  padding: 12,
                  background: 'rgba(255,255,255,0.02)',
                  border: `1px solid ${getStatusColor(status)}`,
                  borderRadius: 8
                }}>
                  <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                        {module.replace('_', ' ')}
                      </div>
                      <div style={{ 
                        fontSize: 12, 
                        color: getStatusColor(status),
                        textTransform: 'capitalize'
                      }}>
                        {status}
                      </div>
                    </div>
                    <div style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: getStatusColor(status)
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="title">Quick Actions</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
            <div style={{ 
              padding: 16, 
              background: 'rgba(106, 166, 255, 0.05)',
              border: '1px solid var(--brand)',
              borderRadius: 12,
              cursor: 'pointer'
            }} 
            onClick={() => window.location.href = '/intelligence'}>
              <h4 style={{ margin: '0 0 8px 0', color: 'var(--brand)' }}>
                📊 Intelligence Analysis
              </h4>
              <div className="muted" style={{ fontSize: 13 }}>
                Upload social media data and generate competitive intelligence reports
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--brand)' }}>
                Click to start →
              </div>
            </div>

            <div style={{ 
              padding: 16, 
              background: 'rgba(52, 211, 153, 0.05)',
              border: '1px solid var(--ok)',
              borderRadius: 12,
              cursor: 'pointer'
            }}
            onClick={() => window.location.href = '/summary'}>
              <h4 style={{ margin: '0 0 8px 0', color: 'var(--ok)' }}>
                📋 Executive Summary
              </h4>
              <div className="muted" style={{ fontSize: 13 }}>
                Generate high-level strategic insights and competitive analysis
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--ok)' }}>
                Click to generate →
              </div>
            </div>

            <div style={{ 
              padding: 16, 
              background: 'rgba(245, 158, 11, 0.05)',
              border: '1px solid var(--warn)',
              borderRadius: 12,
              cursor: 'pointer'
            }}
            onClick={() => window.location.href = '/calendar'}>
              <h4 style={{ margin: '0 0 8px 0', color: 'var(--warn)' }}>
                📅 Cultural Calendar
              </h4>
              <div className="muted" style={{ fontSize: 13 }}>
                Track important dates and cultural events for content planning
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--warn)' }}>
                Click to view →
              </div>
            </div>

            <div style={{ 
              padding: 16, 
              background: 'rgba(142, 123, 255, 0.05)',
              border: '1px solid var(--brand-2)',
              borderRadius: 12,
              cursor: 'pointer'
            }}
            onClick={() => window.location.href = '/agency'}>
              <h4 style={{ margin: '0 0 8px 0', color: 'var(--brand-2)' }}>
                🏢 Agency Dashboard
              </h4>
              <div className="muted" style={{ fontSize: 13 }}>
                Track projects, deliverables, and team performance
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--brand-2)' }}>
                Click to manage →
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Dashboard */}
        <div className="card">
          <h3 className="title">Key Metrics</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: 'var(--brand)' }}>
                {systemHealth ? Object.keys(systemHealth.modules).length : '--'}
              </div>
              <div className="muted">Active Modules</div>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: 'var(--ok)' }}>
                {apiStatus ? apiStatus.endpoints_available?.length || 0 : '--'}
              </div>
              <div className="muted">API Endpoints</div>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: 'var(--warn)' }}>
                24/7
              </div>
              <div className="muted">Monitoring</div>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 'bold', color: 'var(--brand-2)' }}>
                v2.1
              </div>
              <div className="muted">Platform Version</div>
            </div>
          </div>
        </div>

        {/* Recent Features */}
        {systemHealth && systemHealth.new_features && (
          <div className="card">
            <h3 className="title">Latest Features</h3>
            <div className="grid" style={{ gap: 8 }}>
              {systemHealth.new_features.map((feature, index) => (
                <div key={index} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 8,
                  padding: 8,
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: 6
                }}>
                  <div style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    background: 'var(--ok)',
                    flexShrink: 0
                  }} />
                  <span style={{ fontSize: 14 }}>{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Information */}
        <div className="card">
          <h3 className="title">System Information</h3>
          <div style={{ fontSize: 13, lineHeight: 1.6, color: 'var(--muted)' }}>
            <div className="row" style={{ marginBottom: 8 }}>
              <strong>Service:</strong> 
              <span style={{ marginLeft: 8 }}>
                {systemHealth?.service || 'Crooks & Castles Command Center V2'}
              </span>
            </div>
            <div className="row" style={{ marginBottom: 8 }}>
              <strong>Version:</strong> 
              <span style={{ marginLeft: 8 }}>
                {systemHealth?.version || '2.1.0'}
              </span>
            </div>
            <div className="row" style={{ marginBottom: 8 }}>
              <strong>Status:</strong> 
              <span style={{ 
                marginLeft: 8, 
                color: systemHealth?.status === 'healthy' ? 'var(--ok)' : 'var(--warn)' 
              }}>
                {systemHealth?.status || 'Unknown'}
              </span>
            </div>
            <div className="row">
              <strong>Last Check:</strong> 
              <span style={{ marginLeft: 8 }}>
                {systemHealth?.timestamp ? 
                  new Date(systemHealth.timestamp).toLocaleString() : 
                  'Never'
                }
              </span>
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="card">
          <h3 className="title">Getting Started</h3>
          <div style={{ marginBottom: 16 }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: 16, color: 'var(--brand)' }}>
              New to the Command Center?
            </h4>
            <div className="muted" style={{ marginBottom: 12 }}>
              Follow these steps to get up and running:
            </div>
            <ol style={{ paddingLeft: 20, color: 'var(--muted)', fontSize: 13 }}>
              <li style={{ marginBottom: 6 }}>
                Visit <strong>Intelligence Analysis</strong> to upload your social media data files
              </li>
              <li style={{ marginBottom: 6 }}>
                Generate competitive intelligence reports to understand market positioning
              </li>
              <li style={{ marginBottom: 6 }}>
                Use <strong>Executive Summary</strong> to create high-level strategic insights
              </li>
              <li style={{ marginBottom: 6 }}>
                Check the <strong>Cultural Calendar</strong> for content planning opportunities
              </li>
              <li>
                Monitor ongoing projects via the <strong>Agency Dashboard</strong>
              </li>
            </ol>
          </div>
          
          {(!systemHealth || getHealthScore() < 50) && (
            <div style={{ 
              padding: 12, 
              background: 'rgba(245, 158, 11, 0.1)',
              border: '1px solid var(--warn)',
              borderRadius: 8
            }}>
              <div style={{ color: 'var(--warn)', fontWeight: 'bold', marginBottom: 4 }}>
                Setup Required
              </div>
              <div className="muted" style={{ fontSize: 12 }}>
                Some system components aren't fully operational. Contact your administrator 
                or check the backend server configuration.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
