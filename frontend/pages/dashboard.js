import { useState, useEffect } from 'react';

// Simple fetch helper with legacy→/api fallback
async function getJSON(path) {
  const norm = path.startsWith("/") ? path : `/${path}`;
  let r = await fetch(norm);
  if (!r.ok && !norm.startsWith("/api/")) r = await fetch(`/api${norm}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} @ ${norm}`);
  return r.json();
}

export default function Dashboard() {
  const [agencyData, setAgencyData] = useState(null);
  const [contentData, setContentData] = useState(null);
  const [ingestData, setIngestData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Load all dashboard data
      const [agency, content, ingest] = await Promise.all([
        getJSON('/agency/dashboard').catch(() => null),
        getJSON('/content/dashboard').catch(() => null),
        getJSON('/ingest/overview').catch(() => null)
      ]);
      
      setAgencyData(agency);
      setContentData(content);
      setIngestData(ingest);
      
    } catch (e) {
      setError(`Failed to load dashboard: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '40px auto', padding: 16, fontFamily: 'system-ui' }}>
      <div style={{ marginBottom: 24 }}>
        <a href="/" style={{ color: '#3B82F6', textDecoration: 'none' }}>← Back to Home</a>
      </div>
      
      <h1 style={{ color: '#1F2937', marginBottom: 24 }}>📊 Executive Dashboard</h1>
      
      {loading && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <p>Loading dashboard data...</p>
        </div>
      )}
      
      {error && (
        <div style={{ padding: 16, background: '#FEE2E2', border: '1px solid #FECACA', borderRadius: 8, marginBottom: 24 }}>
          <p style={{ color: '#DC2626', margin: 0 }}>{error}</p>
        </div>
      )}

      {!loading && (
        <div style={{ display: 'grid', gap: 24 }}>
          
          {/* Agency Overview */}
          {agencyData && (
            <div style={{ padding: 24, background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: 12 }}>
              <h2 style={{ color: '#1F2937', marginBottom: 20 }}>🎯 Agency Performance</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 20 }}>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#3B82F6' }}>{agencyData.metrics?.active_projects || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Active Projects</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#10B981' }}>{agencyData.metrics?.completion_rate || 0}%</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Completion Rate</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#F59E0B' }}>{agencyData.metrics?.overdue_deliverables || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Overdue Items</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#8B5CF6' }}>{agencyData.metrics?.client_satisfaction || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Client Rating</div>
                </div>
              </div>

              {agencyData.current_projects && (
                <div>
                  <h3 style={{ color: '#374151', marginBottom: 12 }}>Current Projects</h3>
                  <div style={{ display: 'grid', gap: 12 }}>
                    {agencyData.current_projects.slice(0, 3).map((project, index) => (
                      <div key={index} style={{ padding: 16, background: 'white', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: 'bold', color: '#1F2937' }}>{project.name}</div>
                          <div style={{ color: '#6B7280', fontSize: 14 }}>{project.client}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ 
                            padding: '4px 8px', 
                            background: project.status === 'In Progress' ? '#FEF3C7' : project.status === 'Review' ? '#E0E7FF' : '#F3F4F6',
                            color: project.status === 'In Progress' ? '#92400E' : project.status === 'Review' ? '#3730A3' : '#374151',
                            borderRadius: 12, 
                            fontSize: 12,
                            marginBottom: 4
                          }}>
                            {project.status}
                          </div>
                          <div style={{ color: '#6B7280', fontSize: 12 }}>{project.completion || 0}% complete</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Content Performance */}
          {contentData && (
            <div style={{ padding: 24, background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 12 }}>
              <h2 style={{ color: '#166534', marginBottom: 20 }}>✨ Content Performance</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 20 }}>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#DC2626' }}>{contentData.content_performance?.total_content || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Total Content</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#7C3AED' }}>{contentData.content_metrics?.avg_engagement_rate || 0}%</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Engagement Rate</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#059669' }}>{contentData.content_metrics?.content_velocity || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Content Velocity</div>
                </div>
              </div>

              {contentData.content_ideas && (
                <div>
                  <h3 style={{ color: '#374151', marginBottom: 12 }}>Top Content Ideas</h3>
                  <div style={{ display: 'grid', gap: 12 }}>
                    {contentData.content_ideas.slice(0, 3).map((idea, index) => (
                      <div key={index} style={{ padding: 16, background: 'white', borderRadius: 8 }}>
                        <div style={{ fontWeight: 'bold', color: '#1F2937', marginBottom: 4 }}>{idea.title}</div>
                        <div style={{ color: '#6B7280', fontSize: 14, marginBottom: 8 }}>{idea.description}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: 12, color: '#8B5CF6' }}>{idea.platform}</span>
                          <span style={{ fontSize: 12, color: '#059669' }}>Trending: {idea.trending_factor}/10</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Data Ingestion Status */}
          {ingestData && (
            <div style={{ padding: 24, background: '#FEF3C7', border: '1px solid #FDE68A', borderRadius: 12 }}>
              <h2 style={{ color: '#92400E', marginBottom: 20 }}>📊 Data Ingestion Status</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16 }}>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#DC2626' }}>{ingestData.overview?.total_files || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Total Files</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#7C3AED' }}>{ingestData.overview?.data_by_type?.instagram_data || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Instagram Data</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#059669' }}>{ingestData.overview?.data_by_type?.shopify_data || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Shopify Data</div>
                </div>
                <div style={{ padding: 16, background: 'white', borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#DC2626' }}>{ingestData.overview?.data_by_type?.agency_data || 0}</div>
                  <div style={{ color: '#6B7280', fontSize: 14 }}>Agency Data</div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div style={{ padding: 24, background: '#F3F4F6', border: '1px solid #E5E7EB', borderRadius: 12 }}>
            <h2 style={{ color: '#1F2937', marginBottom: 20 }}>⚡ Quick Actions</h2>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <a href="/intelligence" style={{ 
                padding: '12px 20px', 
                background: '#3B82F6', 
                color: 'white', 
                textDecoration: 'none', 
                borderRadius: 8,
                fontWeight: 'bold'
              }}>
                View Intelligence
              </a>
              <a href="/agency" style={{ 
                padding: '12px 20px', 
                background: '#8B5CF6', 
                color: 'white', 
                textDecoration: 'none', 
                borderRadius: 8,
                fontWeight: 'bold'
              }}>
                Agency Dashboard
              </a>
              <a href="/upload" style={{ 
                padding: '12px 20px', 
                background: '#10B981', 
                color: 'white', 
                textDecoration: 'none', 
                borderRadius: 8,
                fontWeight: 'bold'
              }}>
                Upload Data
              </a>
              <button onClick={loadDashboardData} style={{ 
                padding: '12px 20px', 
                background: '#6B7280', 
                color: 'white', 
                border: 'none',
                borderRadius: 8,
                fontWeight: 'bold',
                cursor: 'pointer'
              }}>
                Refresh Data
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
