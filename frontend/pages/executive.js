import { useState, useEffect, useCallback } from "react";
import Head from 'next/head';

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function ExecutiveOverviewPage() {
  const [dashboardData, setDashboardData] = useState(null);
  const [timeframe, setTimeframe] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadExecutiveOverview = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API}/executive/overview?days=${timeframe}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!res.ok) {
        throw new Error(`Failed to load executive overview: HTTP ${res.status}`);
      }

      const result = await res.json();
      setDashboardData(result);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to load executive overview:', err);
      setError(`Unable to load executive overview: ${err.message}`);
      
      // Set fallback data structure
      setDashboardData({
        shopify_metrics: {
          total_sales: 0,
          total_orders: 0,
          conversion_rate: 0,
          aov: 0,
          traffic: 0,
          status: "no_data"
        },
        competitive_analysis: {
          market_position: "unknown",
          competitors_analyzed: 0,
          performance_vs_competitors: "insufficient_data"
        },
        social_performance: {
          total_engagement: 0,
          sentiment_score: 0,
          brand_mentions: 0
        },
        correlations: {},
        recommendations: [
          "Upload Shopify sales data to see e-commerce metrics",
          "Upload competitive intelligence data (Apify scraping results)",
          "Upload social media data to correlate with sales performance"
        ],
        alerts: [
          {
            level: "warning",
            message: "Missing data sources - unable to generate comprehensive insights",
            action: "Upload data files to enable full analysis"
          }
        ]
      });
    } finally {
      setLoading(false);
    }
  }, [timeframe]);

  useEffect(() => {
    loadExecutiveOverview();
  }, [loadExecutiveOverview]);

  const getPerformanceColor = (value, type = 'percentage') => {
    if (type === 'percentage') {
      if (value >= 75) return 'var(--ok)';
      if (value >= 50) return 'var(--warn)';
      return 'var(--danger)';
    }
    return 'var(--muted)';
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };

  return (
    <div>
      <Head>
        <title>Executive Overview - Command Center</title>
      </Head>

      <div className="grid">
        {/* Header Controls */}
        <div className="card" style={{ 
          background: 'linear-gradient(135deg, rgba(106, 166, 255, 0.1), rgba(142, 123, 255, 0.1))',
          border: '1px solid var(--brand)'
        }}>
          <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 'bold', margin: '0 0 8px 0' }}>
                📊 Executive Overview Dashboard
              </h1>
              <div className="muted">
                Integrated competitive intelligence and e-commerce performance analysis
              </div>
            </div>
            
            <div className="row" style={{ gap: 12 }}>
              <select 
                value={timeframe} 
                onChange={(e) => setTimeframe(parseInt(e.target.value))}
                style={{ 
                  background: 'var(--panel)', 
                  border: '1px solid var(--line)',
                  color: '#e9edf2',
                  padding: '8px 12px',
                  borderRadius: 8
                }}
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
                <option value={90}>Last 90 days</option>
              </select>
              
              <button 
                className="button" 
                onClick={loadExecutiveOverview}
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>
          
          {lastUpdate && (
            <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>
              Last updated: {lastUpdate}
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="card" style={{ border: '1px solid var(--warn)', background: 'rgba(245, 158, 11, 0.1)' }}>
            <div className="row" style={{ justifyContent: 'space-between' }}>
              <div>
                <h3 className="title" style={{ color: 'var(--warn)', margin: '0 0 8px 0' }}>Data Connection Issue</h3>
                <div style={{ color: 'var(--warn)' }}>{error}</div>
                <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>
                  Showing fallback dashboard. Ensure backend is running and data sources are configured.
                </div>
              </div>
              <button className="button" onClick={() => setError(null)} style={{ background: 'var(--warn)' }}>
                Dismiss
              </button>
            </div>
          </div>
        )}

        {dashboardData && (
          <>
            {/* Critical Alerts */}
            {dashboardData.alerts && dashboardData.alerts.length > 0 && (
              <div className="card">
                <h3 className="title">🚨 Critical Alerts</h3>
                {dashboardData.alerts.map((alert, index) => (
                  <div key={index} style={{
                    padding: 12,
                    background: alert.level === 'critical' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                    border: `1px solid ${alert.level === 'critical' ? 'var(--danger)' : 'var(--warn)'}`,
                    borderRadius: 8,
                    marginBottom: 8
                  }}>
                    <div style={{ 
                      color: alert.level === 'critical' ? 'var(--danger)' : 'var(--warn)',
                      fontWeight: 'bold',
                      marginBottom: 4
                    }}>
                      {alert.message}
                    </div>
                    <div className="muted" style={{ fontSize: 12 }}>
                      Action: {alert.action}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Key Performance Metrics Grid */}
            <div className="card">
              <h3 className="title">📈 Key Performance Indicators</h3>
              <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
                {/* Shopify Revenue */}
                <div style={{ 
                  padding: 16, 
                  background: 'rgba(52, 211, 153, 0.05)',
                  border: '1px solid var(--ok)',
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: 28, fontWeight: 'bold', color: 'var(--ok)' }}>
                    {formatCurrency(dashboardData.shopify_metrics?.total_sales)}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Total Revenue ({timeframe}d)</div>
                  <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                    {dashboardData.shopify_metrics?.total_orders || 0} orders
                  </div>
                </div>

                {/* Conversion Rate */}
                <div style={{ 
                  padding: 16, 
                  background: 'rgba(106, 166, 255, 0.05)',
                  border: '1px solid var(--brand)',
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: 28, 
                    fontWeight: 'bold', 
                    color: getPerformanceColor(dashboardData.shopify_metrics?.conversion_rate)
                  }}>
                    {formatPercentage(dashboardData.shopify_metrics?.conversion_rate)}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Conversion Rate</div>
                  <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                    {dashboardData.shopify_metrics?.traffic || 0} visitors
                  </div>
                </div>

                {/* Average Order Value */}
                <div style={{ 
                  padding: 16, 
                  background: 'rgba(245, 158, 11, 0.05)',
                  border: '1px solid var(--warn)',
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: 28, fontWeight: 'bold', color: 'var(--warn)' }}>
                    {formatCurrency(dashboardData.shopify_metrics?.aov)}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Average Order Value</div>
                </div>

                {/* Market Position */}
                <div style={{ 
                  padding: 16, 
                  background: 'rgba(142, 123, 255, 0.05)',
                  border: '1px solid var(--brand-2)',
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: 20, fontWeight: 'bold', color: 'var(--brand-2)' }}>
                    #{dashboardData.competitive_analysis?.market_rank || 'N/A'}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Market Position</div>
                  <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                    vs {dashboardData.competitive_analysis?.competitors_analyzed || 0} competitors
                  </div>
                </div>
              </div>
            </div>

            {/* Competitive Analysis Summary */}
            <div className="card">
              <h3 className="title">🏆 Competitive Intelligence Summary</h3>
              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--brand)' }}>
                    Performance vs Competitors
                  </h4>
                  {dashboardData.competitive_analysis?.performance_breakdown ? (
                    <div className="grid" style={{ gap: 8 }}>
                      {Object.entries(dashboardData.competitive_analysis.performance_breakdown).map(([metric, data]) => (
                        <div key={metric} style={{ 
                          padding: 10, 
                          background: 'rgba(255,255,255,0.02)', 
                          borderRadius: 6,
                          border: '1px solid var(--line)'
                        }}>
                          <div className="row" style={{ justifyContent: 'space-between' }}>
                            <span style={{ textTransform: 'capitalize' }}>{metric.replace('_', ' ')}</span>
                            <span style={{ 
                              color: getPerformanceColor(data.percentile),
                              fontWeight: 'bold'
                            }}>
                              {data.percentile ? `${data.percentile}th percentile` : 'No data'}
                            </span>
                          </div>
                          <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
                            Your: {data.your_value || 'N/A'} | Avg: {data.competitor_avg || 'N/A'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="muted">Upload competitive data to see performance comparison</div>
                  )}
                </div>

                <div>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--ok)' }}>
                    Social Media Impact on Sales
                  </h4>
                  {dashboardData.correlations?.social_to_sales ? (
                    <div className="grid" style={{ gap: 8 }}>
                      <div style={{ 
                        padding: 10, 
                        background: 'rgba(255,255,255,0.02)', 
                        borderRadius: 6,
                        border: '1px solid var(--line)'
                      }}>
                        <div className="row" style={{ justifyContent: 'space-between' }}>
                          <span>Engagement → Sales Correlation</span>
                          <span style={{ color: 'var(--ok)', fontWeight: 'bold' }}>
                            {formatPercentage(dashboardData.correlations.social_to_sales.correlation)}
                          </span>
                        </div>
                      </div>
                      <div style={{ 
                        padding: 10, 
                        background: 'rgba(255,255,255,0.02)', 
                        borderRadius: 6,
                        border: '1px solid var(--line)'
                      }}>
                        <div className="row" style={{ justifyContent: 'space-between' }}>
                          <span>Social Traffic Conversion</span>
                          <span style={{ color: 'var(--brand)', fontWeight: 'bold' }}>
                            {formatPercentage(dashboardData.correlations.social_to_sales.social_conversion)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="muted">Upload social media data to see sales correlation</div>
                  )}
                </div>
              </div>
            </div>

            {/* Strategic Recommendations */}
            <div className="card">
              <h3 className="title">🎯 Strategic Recommendations</h3>
              {dashboardData.recommendations && dashboardData.recommendations.length > 0 ? (
                <div className="grid" style={{ gap: 12 }}>
                  {dashboardData.recommendations.map((rec, index) => (
                    <div key={index} style={{
                      padding: 14,
                      background: 'linear-gradient(135deg, rgba(106, 166, 255, 0.05), rgba(142, 123, 255, 0.05))',
                      border: '1px solid var(--brand)',
                      borderRadius: 10,
                      position: 'relative'
                    }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'flex-start', 
                        gap: 12 
                      }}>
                        <div style={{
                          width: 24,
                          height: 24,
                          background: 'var(--brand)',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: 12,
                          fontWeight: 'bold',
                          flexShrink: 0
                        }}>
                          {index + 1}
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ 
                            fontWeight: 'bold', 
                            marginBottom: 4,
                            color: '#e9edf2'
                          }}>
                            {rec.title || `Recommendation ${index + 1}`}
                          </div>
                          <div style={{ 
                            color: 'var(--muted)', 
                            lineHeight: 1.4,
                            fontSize: 14
                          }}>
                            {rec.description || rec}
                          </div>
                          {rec.impact && (
                            <div style={{ 
                              marginTop: 8,
                              fontSize: 12,
                              color: 'var(--brand)',
                              fontWeight: 'bold'
                            }}>
                              Expected Impact: {rec.impact}
                            </div>
                          )}
                          {rec.priority && (
                            <div className="pill" style={{ 
                              marginTop: 8,
                              background: rec.priority === 'high' ? 'var(--danger)' : 
                                         rec.priority === 'medium' ? 'var(--warn)' : 'var(--ok)',
                              color: 'white',
                              fontSize: 10
                            }}>
                              {rec.priority.toUpperCase()} PRIORITY
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="muted">No recommendations available. Upload data to generate strategic insights.</div>
              )}
            </div>

            {/* Data Sources Status */}
            <div className="card">
              <h3 className="title">📂 Data Sources Status</h3>
              <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                <div style={{ 
                  padding: 12, 
                  background: 'rgba(255,255,255,0.02)', 
                  borderRadius: 8,
                  border: `1px solid ${dashboardData.data_sources?.shopify ? 'var(--ok)' : 'var(--danger)'}`
                }}>
                  <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>Shopify Data</div>
                      <div className="muted" style={{ fontSize: 12 }}>
                        {dashboardData.data_sources?.shopify ? 'Connected' : 'Not Connected'}
                      </div>
                    </div>
                    <div style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: dashboardData.data_sources?.shopify ? 'var(--ok)' : 'var(--danger)'
                    }} />
                  </div>
                </div>

                <div style={{ 
                  padding: 12, 
                  background: 'rgba(255,255,255,0.02)', 
                  borderRadius: 8,
                  border: `1px solid ${dashboardData.data_sources?.competitive ? 'var(--ok)' : 'var(--danger)'}`
                }}>
                  <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>Competitive Data</div>
                      <div className="muted" style={{ fontSize: 12 }}>
                        {dashboardData.data_sources?.competitive ? 'Active' : 'Missing'}
                      </div>
                    </div>
                    <div style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: dashboardData.data_sources?.competitive ? 'var(--ok)' : 'var(--danger)'
                    }} />
                  </div>
                </div>

                <div style={{ 
                  padding: 12, 
                  background: 'rgba(255,255,255,0.02)', 
                  borderRadius: 8,
                  border: `1px solid ${dashboardData.data_sources?.social ? 'var(--ok)' : 'var(--danger)'}`
                }}>
                  <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>Social Media Data</div>
                      <div className="muted" style={{ fontSize: 12 }}>
                        {dashboardData.data_sources?.social ? 'Available' : 'Upload Needed'}
                      </div>
                    </div>
                    <div style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: dashboardData.data_sources?.social ? 'var(--ok)' : 'var(--danger)'
                    }} />
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
