import React, { useState, useEffect } from 'react';

const ExecutiveOverview = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchOverviewData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/executive/overview');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (!result.ok) {
        throw new Error(result.message || 'Failed to load overview data');
      }
      
      setData(result);
    } catch (err) {
      setError(err.message);
      console.error('Executive overview error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const handleRefresh = () => {
    fetchOverviewData();
  };

  if (loading) {
    return (
      <main style={mainStyle}>
        <h1>Executive Overview</h1>
        <div style={loadingStyle}>
          <p>Loading...</p>
        </div>
      </main>
    );
  }

  return (
    <main style={mainStyle}>
      <div style={headerStyle}>
        <h1>Executive Overview</h1>
        <button onClick={handleRefresh} style={refreshButtonStyle}>
          Refresh
        </button>
      </div>

      {error && (
        <div style={errorStyle}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {data && (
        <>
          {/* Brands Section */}
          <section style={sectionStyle}>
            <h2>Brands</h2>
            <div style={metricStyle}>
              <span style={numberStyle}>{data.brands?.count || 0}</span>
            </div>
            {data.brands?.list && (
              <ul style={listStyle}>
                {data.brands.list.map((brand, index) => (
                  <li key={index}>{brand}</li>
                ))}
              </ul>
            )}
          </section>

          {/* Competitors Section */}
          <section style={sectionStyle}>
            <h2>Competitors</h2>
            <div style={metricStyle}>
              <span style={numberStyle}>{data.competitors?.count || 0}</span>
            </div>
            {data.competitors?.list && (
              <ul style={listStyle}>
                {data.competitors.list.map((competitor, index) => (
                  <li key={index}>{competitor}</li>
                ))}
              </ul>
            )}
          </section>

          {/* Benchmarks Section */}
          <section style={sectionStyle}>
            <h2>Benchmarks</h2>
            <div style={metricStyle}>
              <span style={numberStyle}>{data.benchmarks?.count || 0}</span>
            </div>
            
            {data.benchmarks?.metrics && data.benchmarks.metrics.length > 0 ? (
              <div style={benchmarksGridStyle}>
                {data.benchmarks.metrics.map((metric, index) => (
                  <div key={index} style={benchmarkCardStyle}>
                    <div style={benchmarkMetricStyle}>{metric.metric}</div>
                    <div style={benchmarkValueStyle}>{metric.value}</div>
                    <div style={{
                      ...benchmarkTrendStyle,
                      color: metric.trend === 'up' ? '#28a745' : 
                             metric.trend === 'down' ? '#dc3545' : '#6c757d'
                    }}>
                      {metric.trend === 'up' ? '↗' : 
                       metric.trend === 'down' ? '↘' : '→'} {metric.trend}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={noDataStyle}>No benchmarks yet. Import a CSV via Intelligence.</p>
            )}
          </section>

          {/* Last Updated */}
          {data.last_updated && (
            <div style={timestampStyle}>
              Last updated: {new Date(data.last_updated).toLocaleString()}
            </div>
          )}
        </>
      )}
    </main>
  );
};

const mainStyle = {
  maxWidth: 1000,
  margin: '40px auto',
  padding: 20
};

const headerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 24
};

const refreshButtonStyle = {
  padding: '8px 16px',
  background: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: 4,
  cursor: 'pointer',
  fontSize: 14,
  fontWeight: 500
};

const loadingStyle = {
  textAlign: 'center',
  padding: 40,
  color: '#666'
};

const errorStyle = {
  background: '#fee',
  border: '1px solid #f99',
  padding: 12,
  borderRadius: 8,
  marginBottom: 20,
  color: '#c33'
};

const sectionStyle = {
  background: '#fff',
  border: '1px solid #eee',
  borderRadius: 12,
  padding: 20,
  marginBottom: 20,
  boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
};

const metricStyle = {
  marginBottom: 16
};

const numberStyle = {
  fontSize: 32,
  fontWeight: 'bold',
  color: '#333'
};

const listStyle = {
  margin: 0,
  paddingLeft: 20,
  color: '#666'
};

const benchmarksGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: 16,
  marginTop: 16
};

const benchmarkCardStyle = {
  background: '#f8f9fa',
  padding: 16,
  borderRadius: 8,
  border: '1px solid #e9ecef'
};

const benchmarkMetricStyle = {
  fontSize: 14,
  fontWeight: 600,
  color: '#495057',
  marginBottom: 8
};

const benchmarkValueStyle = {
  fontSize: 24,
  fontWeight: 'bold',
  color: '#212529',
  marginBottom: 4
};

const benchmarkTrendStyle = {
  fontSize: 12,
  fontWeight: 500,
  textTransform: 'capitalize'
};

const noDataStyle = {
  color: '#666',
  fontStyle: 'italic',
  marginTop: 16
};

const timestampStyle = {
  textAlign: 'center',
  color: '#666',
  fontSize: 12,
  marginTop: 20,
  padding: 10,
  background: '#f8f9fa',
  borderRadius: 4
};

export default ExecutiveOverview;
