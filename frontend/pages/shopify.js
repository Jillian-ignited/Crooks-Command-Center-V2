import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function ShopifyPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('checking');

  const loadShopifyData = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API}/shopify/dashboard`);
      
      if (!res.ok) {
        throw new Error(`Failed to load Shopify data: HTTP ${res.status}`);
      }
      
      const result = await res.json();
      setData(result);
      setConnectionStatus('connected');
    } catch (err) {
      console.error('Failed to load Shopify data:', err);
      setError(`Unable to load Shopify dashboard: ${err.message}`);
      setConnectionStatus('disconnected');
      
      // Set fallback data for development/testing
      setData({
        store_name: "Demo Store",
        orders_today: 0,
        revenue_today: 0,
        products_count: 0,
        customers_count: 0,
        recent_orders: [],
        top_products: []
      });
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setConnectionStatus('checking');
    try {
      const res = await fetch(`${API}/shopify/test-connection`);
      if (res.ok) {
        setConnectionStatus('connected');
        loadShopifyData();
      } else {
        setConnectionStatus('disconnected');
      }
    } catch (err) {
      setConnectionStatus('disconnected');
    }
  };

  useEffect(() => {
    loadShopifyData();
  }, []);

  if (loading) {
    return (
      <div className="grid">
        <div className="card">
          <h3 className="title">Shopify Integration</h3>
          <div className="muted">Loading Shopify data...</div>
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
              <h3 className="title" style={{ color: 'var(--warn)', margin: '0 0 8px 0' }}>Shopify Connection Issue</h3>
              <div style={{ color: 'var(--warn)' }}>{error}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
                Showing demo data. Check Shopify API configuration.
              </div>
            </div>
            <button 
              className="button" 
              onClick={testConnection}
              style={{ background: 'var(--warn)', minWidth: 'auto', padding: '6px 12px' }}
            >
              Test Connection
            </button>
          </div>
        </div>
      )}

      {/* Connection Status */}
      <div className="card">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <h3 className="title" style={{ margin: 0 }}>Shopify Dashboard</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 6,
              padding: '4px 8px',
              borderRadius: 4,
              background: connectionStatus === 'connected' ? 'rgba(34, 197, 94, 0.1)' : 
                         connectionStatus === 'disconnected' ? 'rgba(239, 68, 68, 0.1)' : 
                         'rgba(156, 163, 175, 0.1)',
              color: connectionStatus === 'connected' ? 'var(--ok)' : 
                     connectionStatus === 'disconnected' ? 'var(--danger)' : 
                     'var(--muted)'
            }}>
              <div style={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                background: connectionStatus === 'connected' ? 'var(--ok)' : 
                           connectionStatus === 'disconnected' ? 'var(--danger)' : 
                           'var(--muted)'
              }}></div>
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'disconnected' ? 'Disconnected' : 
               'Checking...'}
            </div>
            <button 
              className="button" 
              onClick={loadShopifyData}
              disabled={loading}
              style={{ minWidth: 'auto' }}
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
        </div>
        <div className="muted" style={{ marginTop: 8 }}>
          Store: {data?.store_name || 'Not connected'}
        </div>
      </div>

      {/* Key Metrics */}
      {data && (
        <div className="card">
          <h3 className="title">Today's Performance</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
            <div style={{ textAlign: 'center', padding: 16, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--brand)' }}>
                {data.orders_today || 0}
              </div>
              <div className="muted" style={{ fontSize: 14 }}>Orders Today</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 16, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--ok)' }}>
                ${(data.revenue_today || 0).toLocaleString()}
              </div>
              <div className="muted" style={{ fontSize: 14 }}>Revenue Today</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 16, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--warn)' }}>
                {(data.products_count || 0).toLocaleString()}
              </div>
              <div className="muted" style={{ fontSize: 14 }}>Total Products</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: 16, background: 'rgba(255,255,255,0.02)', borderRadius: 8 }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--info)' }}>
                {(data.customers_count || 0).toLocaleString()}
              </div>
              <div className="muted" style={{ fontSize: 14 }}>Total Customers</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Orders */}
      {data && (
        <div className="card">
          <h3 className="title">Recent Orders</h3>
          {data.recent_orders && data.recent_orders.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <th style={{ padding: '12px 8px', textAlign: 'left', color: 'var(--muted)' }}>Order #</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', color: 'var(--muted)' }}>Customer</th>
                    <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--muted)' }}>Total</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', color: 'var(--muted)' }}>Status</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', color: 'var(--muted)' }}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_orders.map((order, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '12px 8px' }}>{order.order_number}</td>
                      <td style={{ padding: '12px 8px' }}>{order.customer_name}</td>
                      <td style={{ padding: '12px 8px', textAlign: 'right' }}>${order.total}</td>
                      <td style={{ padding: '12px 8px' }}>
                        <span style={{ 
                          padding: '2px 8px', 
                          borderRadius: 4, 
                          fontSize: 12,
                          background: order.status === 'fulfilled' ? 'rgba(34, 197, 94, 0.2)' : 
                                     order.status === 'pending' ? 'rgba(245, 158, 11, 0.2)' : 
                                     'rgba(156, 163, 175, 0.2)',
                          color: order.status === 'fulfilled' ? 'var(--ok)' : 
                                order.status === 'pending' ? 'var(--warn)' : 
                                'var(--muted)'
                        }}>
                          {order.status}
                        </span>
                      </td>
                      <td style={{ padding: '12px 8px', color: 'var(--muted)' }}>{order.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="muted" style={{ padding: 16, textAlign: 'center' }}>
              No recent orders found
            </div>
          )}
        </div>
      )}

      {/* Top Products */}
      {data && data.top_products && data.top_products.length > 0 && (
        <div className="card">
          <h3 className="title">Top Products</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 12 }}>
            {data.top_products.map((product, index) => (
              <div key={index} style={{ 
                padding: 12, 
                background: 'rgba(255,255,255,0.02)', 
                borderRadius: 8,
                border: '1px solid rgba(255,255,255,0.05)'
              }}>
                <div style={{ fontWeight: 'bold', marginBottom: 4 }}>{product.title}</div>
                <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
                  {product.sales_count} sales • ${product.revenue}
                </div>
                <div style={{ fontSize: 12, color: 'var(--brand)' }}>
                  ${product.price}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Configuration */}
      <div className="card">
        <h3 className="title">Configuration</h3>
        <div className="muted" style={{ marginBottom: 16 }}>
          Manage your Shopify integration settings
        </div>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button className="button" onClick={testConnection}>
            Test Connection
          </button>
          <button className="button" style={{ background: 'var(--muted)' }}>
            Update API Keys
          </button>
          <button className="button" style={{ background: 'var(--muted)' }}>
            Sync Products
          </button>
          <button className="button" style={{ background: 'var(--muted)' }}>
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
}
