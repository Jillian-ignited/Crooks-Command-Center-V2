import { useState, useEffect, useCallback } from "react";
import Head from 'next/head';

const API = process.env.NEXT_PUBLIC_API_BASE || "";

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
    } finally {
      setLoading(false);
    }
  }, [timeframe]);

  useEffect(() => {
    loadExecutiveOverview();
  }, [loadExecutiveOverview]);

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'No Data';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return 'No Data';
    return `${value.toFixed(1)}%`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'var(--ok)';
    if (confidence >= 60) return 'var(--warn)';
    return 'var(--danger)';
  };

  const getRankColor = (rank, total) => {
    if (!rank || !total) return 'var(--muted)';
    if (rank <= total * 0.25) return 'var(--ok)';
    if (rank <= total * 0.5) return 'var(--warn)';
    return 'var(--danger)';
  };

  return (
    <div>
      <Head>
        <title>Executive Overview - Real Data Intelligence</title>
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
                Executive Overview - Real Data Intelligence
              </h1>
              <div className="muted">
                Shopify + Competitive + Social Media Analysis (No Mock Data)
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
          <div className="card" style={{ border: '1px solid var(--danger)', background: 'rgba(239, 68, 68, 0.1)' }}>
            <div className="row" style={{ justifyContent: 'space-between' }}>
              <div>
                <h3 className="title" style={{ color: 'var(--danger)', margin: '0 0 8px 0' }}>Connection Error</h3>
                <div style={{ color: 'var(--danger)' }}>{error}</div>
              </div>
              <button className="button" onClick={() => setError(null)} style={{ background: 'var(--danger)' }}>
                Dismiss
              </button>
            </div>
          </div>
        )}

        {dashboardData && (
          <>
            {/* Data Confidence Dashboard */}
            <div className="card">
              <h3 className="title">Data Quality & Confidence</h3>
              <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
                <div style={{ 
                  padding: 16, 
                  background: 'rgba(255,255,255,0.02)',
                  border: `1px solid ${getConfidenceColor(dashboardData.analysis_confidence?.revenue || 0)}`,
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: 24, 
                    fontWeight: 'bold', 
                    color: getConfidenceColor(dashboardData.analysis_confidence?.revenue || 0)
                  }}>
                    {dashboardData.analysis_confidence?.revenue || 0}%
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Revenue Data Confidence</div>
                  <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                    {dashboardData.data_sources?.shopify ? 'Shopify Connected' : 'No Shopify Data'}
                  </div>
                </div>

                <div style={{ 
                  padding: 16, 
                  background: 'rgba(255,255,255,0.02)',
                  border: `1px solid ${getConfidenceColor(dashboardData.analysis_confidence?.competitive || 0)}`,
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: 24, 
                    fontWeight: 'bold', 
                    color: getConfidenceColor(dashboardData.analysis_confidence?.competitive || 0)
                  }}>
                    {dashboardData.analysis_confidence?.competitive || 0}%
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Competitive Data Confidence</div>
                  <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                    {dashboardData.competitive_analysis?.brands_analyzed || 0} brands analyzed
                  </div>
                </div>

                <div style={{ 
                  padding: 16, 
                  background: 'rgba(255,255,255,0.02)',
                  border: `1px solid ${getConfidenceColor(dashboardData.analysis_confidence?.trending || 0)}`,
                  borderRadius: 12,
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: 24, 
                    fontWeight: 'bold', 
                    color: getConfidenceColor(dashboardData.analysis_confidence?.trending || 0)
                  }}>
                    {dashboardData.analysis_confidence?.trending || 0}%
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>Trending Data Confidence</div>
                  <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                    {dashboardData.trending_topics?.length || 0} trends tracked
                  </div>
                </div>
              </div>
            </div>

            {/* Critical Alerts */}
            {dashboardData.alerts && dashboardData.alerts.length > 0 && (
              <div className="card">
                <h3 className="title">Critical Alerts</h3>
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

            {/* Real Revenue Metrics */}
            {dashboardData.shopify_metrics && (
              <div className="card">
                <h3 className="title">Revenue Intelligence ({timeframe} days)</h3>
                <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
                  <div style={{ 
                    padding: 16, 
                    background: 'rgba(52, 211, 153, 0.05)',
                    border: '1px solid var(--ok)',
                    borderRadius: 12,
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: 'var(--ok)' }}>
                      {formatCurrency(dashboardData.shopify_metrics.total_sales)}
                    </div>
                    <div className="muted" style={{ fontSize: 12 }}>Total Revenue</div>
                    <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                      {dashboardData.shopify_metrics.total_orders || 'No'} orders
                    </div>
                  </div>

                  <div style={{ 
                    padding: 16, 
                    background: 'rgba(106, 166, 255, 0.05)',
                    border: '1px solid var(--brand)',
                    borderRadius: 12,
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: 'var(--brand)' }}>
                      {formatCurrency(dashboardData.shopify_metrics.aov)}
                    </div>
                    <div className="muted" style={{ fontSize: 12 }}>Average Order Value</div>
                    <div className="pill" style={{ marginTop: 8, fontSize: 10 }}>
                      {dashboardData.shopify_metrics.aov && dashboardData.shopify_metrics.aov < 75 ? 'Below Industry Avg' : 'Strong Performance'}
                    </div>
                  </div>

                  <div style={{ 
                    padding: 16, 
                    background: 'rgba(245, 158, 11, 0.05)',
                    border: '1px solid var(--warn)',
                    borderRadius: 12,
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: 'var(--warn)' }}>
                      {dashboardData.shopify_metrics.conversion_rate !== null ? 
                        formatPercentage(dashboardData.shopify_metrics.conversion_rate) : 
                        'Analytics Needed'
                      }
                    </div>
                    <div className="muted" style={{ fontSize: 12 }}>Conversion Rate</div>
                  </div>
                </div>

                {/* Top Products Performance */}
                {dashboardData.shopify_metrics.top_products && dashboardData.shopify_metrics.top_products.length > 0 && (
                  <div style={{ marginTop: 16 }}>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--brand)' }}>
                      Top Performing Products
                    </h4>
                    <div className="grid" style={{ gap: 8 }}>
                      {dashboardData.shopify_metrics.top_products.slice(0, 5).map((product, index) => (
                        <div key={index} style={{ 
                          padding: 10, 
                          background: 'rgba(255,255,255,0.02)', 
                          borderRadius: 6,
                          border: '1px solid var(--line)'
                        }}>
                          <div className="row" style={{ justifyContent: 'space-between' }}>
                            <span style={{ fontWeight: 'bold' }}>{product.name}</span>
                            <span style={{ color: 'var(--ok)' }}>
                              {formatCurrency(product.revenue)}
                            </span>
                          </div>
                          <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
                            Quantity: {product.quantity} units
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Real Competitive Analysis */}
            {dashboardData.competitive_analysis && dashboardData.competitive_analysis.status === 'active' && (
              <div className="card">
                <h3 className="title">Competitive Intelligence vs {dashboardData.competitive_analysis.brands_analyzed} Brands</h3>
                
                {/* Market Position Overview */}
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                  <div>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--brand)' }}>
                      Market Position
                    </h4>
                    <div style={{ 
                      padding: 16, 
                      background: 'rgba(255,255,255,0.02)',
                      borderRadius: 8,
                      border: `1px solid ${getRankColor(dashboardData.competitive_analysis.crooks_rank, dashboardData.competitive_analysis.brands_analyzed)}`,
                      textAlign: 'center'
                    }}>
                      <div style={{ 
                        fontSize: 36, 
                        fontWeight: 'bold', 
                        color: getRankColor(dashboardData.competitive_analysis.crooks_rank, dashboardData.competitive_analysis.brands_analyzed)
                      }}>
                        #{dashboardData.competitive_analysis.crooks_rank || 'N/A'}
                      </div>
                      <div className="muted" style={{ fontSize: 12 }}>
                        of {dashboardData.competitive_analysis.brands_analyzed} tracked brands
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--ok)' }}>
                      Market Share
                    </h4>
                    <div style={{ 
                      padding: 16, 
                      background: 'rgba(255,255,255,0.02)',
                      borderRadius: 8,
                      border: '1px solid var(--line)',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: 36, fontWeight: 'bold', color: 'var(--ok)' }}>
                        {dashboardData.competitive_analysis.market_share && 
                         dashboardData.competitive_analysis.market_share['crooks & castles'] ? 
                         formatPercentage(dashboardData.competitive_analysis.market_share['crooks & castles']) : 
                         'No Data'
                        }
                      </div>
                      <div className="muted" style={{ fontSize: 12 }}>
                        digital engagement share
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Comparison Details */}
                {dashboardData.competitive_analysis.performance_comparison && (
                  <div>
                    <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--warn)' }}>
                      Performance vs Competitors
                    </h4>
                    <div className="grid" style={{ gap: 8 }}>
                      {Object.entries(dashboardData.competitive_analysis.performance_comparison).map(([metric, data]) => (
                        <div key={metric} style={{ 
                          padding: 12, 
                          background: 'rgba(255,255,255,0.02)', 
                          borderRadius: 6,
                          border: '1px solid var(--line)'
                        }}>
                          <div className="row" style={{ justifyContent: 'space-between', marginBottom: 4 }}>
                            <span style={{ textTransform: 'capitalize', fontWeight: 'bold' }}>
                              {metric.replace('_', ' ')}
                            </span>
                            <span style={{ 
                              color: data.performance_vs_avg >= 0 ? 'var(--ok)' : 'var(--danger)',
                              fontWeight: 'bold'
                            }}>
                              {data.performance_vs_avg >= 0 ? '+' : ''}{data.performance_vs_avg}% vs avg
                            </span>
                          </div>
                          <div className="row" style={{ justifyContent: 'space-between', fontSize: 12, color: 'var(--muted)' }}>
                            <span>Your: {data.crooks_value}</span>
                            <span>Avg: {data.competitor_avg}</span>
                            <span>Rank: #{data.rank}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Real Trending Topics */}
            {dashboardData.trending_topics && dashboardData.trending_topics.length > 0 && (
              <div className="card">
                <h3 className="title">Revenue Intelligence - Trending Topics</h3>
                <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 12 }}>
                  {dashboardData.trending_topics.slice(0, 12).map((topic, index) => (
                    <div key={index} style={{
                      padding: 12,
                      background: topic.trend_strength === 'high' ? 'rgba(106, 166, 255, 0.1)' : 
                                  topic.trend_strength === 'medium' ? 'rgba(245, 158, 11, 0.1)' : 
                                  'rgba(255, 255, 255, 0.02)',
                      border: `1px solid ${topic.trend_strength === 'high' ? 'var(--brand)' : 
                                          topic.trend_strength === 'medium' ? 'var(--warn)' : 
                                          'var(--line)'}`,
                      borderRadius: 8
                    }}>
                      <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ 
                            fontWeight: 'bold', 
                            color: topic.type === 'hashtag' ? 'var(--brand)' : '#e9edf2'
                          }}>
                            {topic.term}
                          </div>
                          <div className="muted" style={{ fontSize: 11 }}>
                            {topic.frequency} mentions • {topic.type}
                          </div>
                        </div>
                        <div className="pill" style={{ 
                          background: topic.trend_strength === 'high' ? 'var(--brand)' : 
                                     topic.trend_strength === 'medium' ? 'var(--warn)' : 
                                     'var(--muted)',
                          color: 'white',
                          fontSize: 9
                        }}>
                          {topic.trend_strength.toUpperCase()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Strategic Recommendations */}
            <div className="card">
              <h3 className="title">Strategic Recommendations (Data-Driven)</h3>
              {dashboardData.recommendations && dashboardData.recommendations.length > 0 ? (
                <div className="grid" style={{ gap: 16 }}>
                  {dashboardData.recommendations.map((rec, index) => (
                    <div key={index} style={{
                      padding: 18,
                      background: 'linear-gradient(135deg, rgba(106, 166, 255, 0.05), rgba(142, 123, 255, 0.05))',
                      border: `2px solid ${rec.priority === 'critical' ? 'var(--danger)' : 
                                          rec.priority === 'high' ? 'var(--warn)' : 
                                          'var(--brand)'}`,
                      borderRadius: 12
                    }}>
                      <div className="row" style={{ justifyContent: 'space-between', marginBottom: 12 }}>
                        <h4 style={{ margin: 0, fontSize: 18, color: 'var(--brand)' }}>
                          {rec.title}
                        </h4>
                        <div className="pill" style={{ 
                          background: rec.priority === 'critical' ? 'var(--danger)' : 
                                     rec.priority === 'high' ? 'var(--warn)' : 
                                     'var(--ok)',
                          color: 'white',
                          fontSize: 10
                        }}>
                          {rec.priority.toUpperCase()} PRIORITY
                        </div>
                      </div>
                      
                      <div style={{ marginBottom: 12, lineHeight: 1.5 }}>
                        {rec.description}
                      </div>
                      
                      {rec.context && (
                        <div style={{ 
                          marginBottom: 12, 
                          padding: 10,
                          background: 'rgba(255,255,255,0.02)',
                          borderRadius: 6,
                          fontSize: 13,
                          color: 'var(--muted)'
                        }}>
                          <strong style={{ color: '#e9edf2' }}>Context:</strong> {rec.context}
                        </div>
                      )}
                      
                      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 12 }}>
                        <div>
                          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>Expected Impact</div>
                          <div style={{ fontSize: 14, fontWeight: 'bold', color: 'var(--ok)' }}>
                            {rec.expected_impact}
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>Implementation Time</div>
                          <div style={{ fontSize: 14, fontWeight: 'bold', color: 'var(--warn)' }}>
                            {rec.time_to_implement}
                          </div>
                        </div>
                      </div>
                      
                      {rec.specific_actions && rec.specific_actions.length > 0 && (
                        <div>
                          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>Specific Actions:</div>
                          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
                            {rec.specific_actions.map((action, actionIndex) => (
                              <li key={actionIndex} style={{ marginBottom: 4 }}>
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {rec.success_metrics && rec.success_metrics.length > 0 && (
                        <div style={{ marginTop: 12 }}>
                          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>Success Metrics:</div>
                          <div className="row" style={{ flexWrap: 'wrap', gap: 6 }}>
                            {rec.success_metrics.map((metric, metricIndex) => (
                              <span key={metricIndex} className="pill" style={{ 
                                background: 'var(--brand)', 
                                color: 'white',
                                fontSize: 10
                              }}>
                                {metric}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="muted">
                  No recommendations available. Upload data files to generate strategic insights.
                </div>
              )}
            </div>

            {/* Real-time Intelligence Insights */}
            {(dashboardData.revenue_insights || dashboardData.competitive_insights) && (
              <div className="card">
                <h3 className="title">Intelligence Insights</h3>
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  {dashboardData.revenue_insights && dashboardData.revenue_insights.length > 0 && (
                    <div>
                      <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--ok)' }}>
                        Revenue Intelligence
                      </h4>
                      <div className="grid" style={{ gap: 8 }}>
                        {dashboardData.revenue_insights.map((insight, index) => (
                          <div key={index} style={{ 
                            padding: 10, 
                            background: 'rgba(52, 211, 153, 0.05)', 
                            borderRadius: 6,
                            border: '1px solid var(--ok)',
                            fontSize: 13
                          }}>
                            {insight}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {dashboardData.competitive_insights && dashboardData.competitive_insights.length > 0 && (
                    <div>
                      <h4 style={{ margin: '0 0 12px 0', fontSize: 16, color: 'var(--brand)' }}>
                        Competitive Intelligence
                      </h4>
                      <div className="grid" style={{ gap: 8 }}>
                        {dashboardData.competitive_insights.map((insight, index) => (
                          <div key={index} style={{ 
                            padding: 10, 
                            background: 'rgba(106, 166, 255, 0.05)', 
                            borderRadius: 6,
                            border: '1px solid var(--brand)',
                            fontSize: 13
                          }}>
                            {insight}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
