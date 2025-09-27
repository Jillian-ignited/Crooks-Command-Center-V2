export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: "48px auto", padding: 24 }}>
      <h1>Crooks Command Center</h1>
      <nav style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
          <a href="/executive" style={{ padding: '8px 16px', background: '#3B82F6', color: 'white', textDecoration: 'none', borderRadius: 6 }}>Dashboard</a>
          <a href="/executive" style={{ padding: '8px 16px', background: '#8B5CF6', color: 'white', textDecoration: 'none', borderRadius: 6 }}>Executive Overview</a>
          <a href="/intelligence" style={{ padding: '8px 16px', background: '#F59E0B', color: 'white', textDecoration: 'none', borderRadius: 6 }}>Intelligence</a>
          <a href="/summary" style={{ padding: '8px 16px', background: '#EF4444', color: 'white', textDecoration: 'none', borderRadius: 6 }}>Executive Summary</a>
          <a href="/calendar" style={{ padding: '8px 16px', background: '#10B981', color: 'white', textDecoration: 'none', borderRadius: 6 }}>Calendar</a>
          <a href="/agency" style={{ padding: '8px 16px', background: '#F97316', color: 'white', textDecoration: 'none', borderRadius: 6 }}>Agency</a>
        </div>
      </nav>
      
      <div style={{ marginBottom: 24, padding: 16, background: '#F3F4F6', borderRadius: 8 }}>
        <h2 style={{ margin: '0 0 16px 0', color: '#1F2937' }}>v2.1</h2>
        <h3 style={{ margin: '0 0 16px 0', color: '#374151' }}>Crooks Command Center</h3>
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          <li><a href="/api/health" target="_blank" style={{ color: '#3B82F6' }}>API Health Check</a></li>
          <li><a href="/upload" style={{ color: '#3B82F6' }}>Upload Intelligence Data</a></li>
        </ul>
        <p style={{ opacity: 0.8, margin: '16px 0 0 0', color: '#6B7280' }}>Static site is served by FastAPI with API under /api.</p>
      </div>

      <div style={{ padding: 16, background: '#FEF3C7', borderRadius: 8, border: '1px solid #F59E0B' }}>
        <h3 style={{ margin: '0 0 12px 0', color: '#92400E' }}>🚀 Enhanced Features</h3>
        <ul style={{ margin: 0, paddingLeft: 20, color: '#92400E' }}>
          <li>Intelligence report generation now working</li>
          <li>Content dashboard with comprehensive metrics</li>
          <li>Enhanced agency project tracking</li>
          <li>Improved file upload feedback</li>
          <li>Fixed API endpoint connections</li>
        </ul>
      </div>
    </main>
  );
}
