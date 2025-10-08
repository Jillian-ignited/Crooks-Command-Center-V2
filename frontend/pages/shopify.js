import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function ShopifyPage() {
  const [dashboard, setDashboard] = useState(null);
  const [customerStats, setCustomerStats] = useState(null);
  const [topProducts, setTopProducts] = useState(null);
  const [recentOrders, setRecentOrders] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      
      const [dashRes, custRes, prodRes, ordRes] = await Promise.all([
        fetch(`${API_BASE_URL}/shopify/dashboard?period=30d`).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${API_BASE_URL}/shopify/customer-stats?days=30`).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${API_BASE_URL}/shopify/top-products?days=30`).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${API_BASE_URL}/shopify/orders?limit=10`).then(r => r.ok ? r.json() : null).catch(() => null)
      ]);
      
      setDashboard(dashRes);
      setCustomerStats(custRes);
      setTopProducts(prodRes);
      setRecentOrders(ordRes);
    } catch (err) {
      console.error("Failed to load Shopify data:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading Shopify analytics...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      {/* Header */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem", color: "#e9edf2" }}>🛍️ Shopify Analytics</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Real-time store performance metrics</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        {/* Revenue Stats */}
        {dashboard && dashboard.summary && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>Total Revenue (30d)</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#4ade80" }}>
                ${dashboard.summary.total_revenue?.toLocaleString() || '0'}
              </div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>Total Orders</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#6aa6ff" }}>
                {dashboard.summary.total_orders?.toLocaleString() || '0'}
              </div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>Avg Order Value</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#f59e0b" }}>
                ${dashboard.summary.avg_order_value?.toFixed(2) || '0.00'}
              </div>
            </div>
            <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
              <div style={{ color: "#888", fontSize: "0.9rem", marginBottom: "0.5rem" }}>Conversion Rate</div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#a78bfa" }}>
                {dashboard.summary.conversion_rate?.toFixed(2) || '0.00'}%
              </div>
            </div>
          </div>
        )}

        {/* Customer Stats */}
        {customerStats && (
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", marginBottom: "2rem" }}>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Customer Statistics</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
              <div>
                <div style={{ color: "#888", fontSize: "0.85rem" }}>Total Customers</div>
                <div style={{ fontSize: "1.5rem", fontWeight: "600", color: "#e9edf2" }}>
                  {customerStats.total_customers || 0}
                </div>
              </div>
              <div>
                <div style={{ color: "#888", fontSize: "0.85rem" }}>New Customers</div>
                <div style={{ fontSize: "1.5rem", fontWeight: "600", color: "#4ade80" }}>
                  {customerStats.new_customers || 0}
                </div>
              </div>
              <div>
                <div style={{ color: "#888", fontSize: "0.85rem" }}>Returning Customers</div>
                <div style={{ fontSize: "1.5rem", fontWeight: "600", color: "#6aa6ff" }}>
                  {customerStats.returning_customers || 0}
                </div>
              </div>
              <div>
                <div style={{ color: "#888", fontSize: "0.85rem" }}>Retention Rate</div>
                <div style={{ fontSize: "1.5rem", fontWeight: "600", color: "#f59e0b" }}>
                  {customerStats.customer_retention_rate?.toFixed(1) || 0}%
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Top Products */}
        {topProducts && topProducts.products && topProducts.products.length > 0 && (
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", marginBottom: "2rem" }}>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Top Products (Last 30 Days)</h3>
            <div style={{ display: "grid", gap: "1rem" }}>
              {topProducts.products.map(product => (
                <div key={product.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1rem", background: "#0a0b0d", borderRadius: "8px" }}>
                  <div>
                    <div style={{ fontWeight: "600", color: "#e9edf2", marginBottom: "0.25rem" }}>{product.name}</div>
                    <div style={{ fontSize: "0.85rem", color: "#888" }}>{product.sales} sales</div>
                  </div>
                  <div style={{ fontSize: "1.25rem", fontWeight: "600", color: "#4ade80" }}>
                    ${product.revenue?.toFixed(2) || '0.00'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Orders */}
        {recentOrders && recentOrders.orders && recentOrders.orders.length > 0 && (
          <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Recent Orders</h3>
            <div style={{ display: "grid", gap: "0.5rem" }}>
              {recentOrders.orders.map(order => (
                <div key={order.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", background: "#0a0b0d", borderRadius: "6px" }}>
                  <div>
                    <div style={{ fontWeight: "600", color: "#e9edf2" }}>Order #{order.id}</div>
                    <div style={{ fontSize: "0.85rem", color: "#888" }}>
                      {order.customer_name} • {order.items_count} items
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "1.1rem", fontWeight: "600", color: "#4ade80" }}>
                      ${order.total?.toFixed(2) || '0.00'}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: order.status === 'fulfilled' ? '#4ade80' : '#f59e0b', textTransform: "uppercase" }}>
                      {order.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {(!dashboard || !dashboard.summary) && (
          <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🛍️</div>
            <h3 style={{ marginBottom: "0.5rem", color: "#e9edf2" }}>No Shopify Data Yet</h3>
            <p style={{ color: "#888" }}>Connect your Shopify store or import sample data to see analytics</p>
          </div>
        )}
      </div>
    </div>
  );
}
