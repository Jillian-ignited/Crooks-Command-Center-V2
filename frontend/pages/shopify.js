import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function ShopifyPage() {
  const [dashboard, setDashboard] = useState(null);
  const [orders, setOrders] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [customerStats, setCustomerStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, orders, products, upload
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [dashboardRes, ordersRes, productsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/shopify/dashboard?period=30d`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE_URL}/shopify/orders?limit=10`).then(r => r.json()).catch(() => ({ orders: [] })),
        fetch(`${API_BASE_URL}/shopify/top-products?days=30`).then(r => r.json()).catch(() => ({ top_products: [] })),
        fetch(`${API_BASE_URL}/shopify/customer-stats?days=30`).then(r => r.json()).catch(() => null)
      ]);
      
      setDashboard(dashboardRes);
      setOrders(ordersRes.orders || []);
      setTopProducts(productsRes.top_products || []);
      setCustomerStats(statsRes);
    } catch (err) {
      console.error("Failed to load Shopify data:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/shopify/import-csv`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        alert(`✅ Success!\nImported: ${result.imported}\nUpdated: ${result.updated}`);
        loadData(); // Reload all data
        setActiveTab("dashboard"); // Switch to dashboard to see results
      } else {
        alert(`❌ Error: ${result.detail || 'Upload failed'}`);
      }
    } catch (err) {
      alert(`❌ Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  }

  async function handleAnalyticsUpload(endpoint, file) {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/shopify/${endpoint}`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        alert(`✅ ${result.message}`);
        loadData();
      } else {
        alert(`❌ Error: ${result.detail || 'Upload failed'}`);
      }
    } catch (err) {
      alert(`❌ Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
          <div>Loading Shopify data...</div>
        </div>
      </div>
    );
  }

  const hasData = dashboard && (dashboard.orders.current > 0 || dashboard.revenue.current > 0);

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2" }}>
      {/* Header */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem 2rem", borderBottom: "1px solid #2a2a2a" }}>
        <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem", color: "#e9edf2" }}>🛍️ Shopify Dashboard</h1>
            <p style={{ color: "#888", fontSize: "0.95rem" }}>Revenue, orders, and customer analytics</p>
          </div>
          <Link href="/" style={{ color: "#6aa6ff", textDecoration: "none" }}>← Back to Dashboard</Link>
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "2rem" }}>
        {/* Tabs */}
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", borderBottom: "1px solid #2a2a2a" }}>
          <button onClick={() => setActiveTab("dashboard")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "dashboard" ? "#6aa6ff" : "#888", borderBottom: activeTab === "dashboard" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📊 Dashboard
          </button>
          <button onClick={() => setActiveTab("orders")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "orders" ? "#6aa6ff" : "#888", borderBottom: activeTab === "orders" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📦 Orders ({orders.length})
          </button>
          <button onClick={() => setActiveTab("products")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "products" ? "#6aa6ff" : "#888", borderBottom: activeTab === "products" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            🏆 Top Products
          </button>
          <button onClick={() => setActiveTab("upload")} style={{ padding: "1rem 1.5rem", background: "none", border: "none", color: activeTab === "upload" ? "#6aa6ff" : "#888", borderBottom: activeTab === "upload" ? "2px solid #6aa6ff" : "none", cursor: "pointer", fontSize: "1rem" }}>
            📤 Upload Data
          </button>
        </div>

        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && (
          <>
            {!hasData ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🛍️</div>
                <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#e9edf2" }}>No Shopify Data Yet</h2>
                <p style={{ color: "#888", marginBottom: "2rem", maxWidth: "500px", margin: "0 auto 2rem" }}>
                  Upload your Shopify analytics reports to see real revenue, conversion rates, and customer analytics
                </p>
                <button onClick={() => setActiveTab("upload")} style={{ padding: "12px 24px", background: "#6aa6ff", color: "#fff", border: "none", borderRadius: "8px", fontSize: "1rem", cursor: "pointer", fontWeight: "600" }}>
                  Upload Shopify Data
                </button>
              </div>
            ) : (
              <>
                {/* Key Metrics */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
                  {/* Revenue */}
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div style={{ color: "#888", fontSize: "0.9rem" }}>💰 Revenue (30d)</div>
                      {dashboard.revenue.growth !== 0 && (
                        <span style={{ fontSize: "0.85rem", color: dashboard.revenue.growth > 0 ? "#4ade80" : "#ff6b6b", background: dashboard.revenue.growth > 0 ? "#1a2a1a" : "#2a1a1a", padding: "2px 8px", borderRadius: "12px" }}>
                          {dashboard.revenue.growth > 0 ? "↑" : "↓"} {Math.abs(dashboard.revenue.growth)}%
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>${dashboard.revenue.current.toLocaleString()}</div>
                  </div>

                  {/* Orders */}
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div style={{ color: "#888", fontSize: "0.9rem" }}>📦 Orders</div>
                      {dashboard.orders.growth !== 0 && (
                        <span style={{ fontSize: "0.85rem", color: dashboard.orders.growth > 0 ? "#4ade80" : "#ff6b6b", background: dashboard.orders.growth > 0 ? "#1a2a1a" : "#2a1a1a", padding: "2px 8px", borderRadius: "12px" }}>
                          {dashboard.orders.growth > 0 ? "↑" : "↓"} {Math.abs(dashboard.orders.growth)}%
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{dashboard.orders.current.toLocaleString()}</div>
                  </div>

                  {/* AOV */}
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div style={{ color: "#888", fontSize: "0.9rem" }}>💵 Avg Order Value</div>
                      {dashboard.avg_order_value.growth !== 0 && (
                        <span style={{ fontSize: "0.85rem", color: dashboard.avg_order_value.growth > 0 ? "#4ade80" : "#ff6b6b", background: dashboard.avg_order_value.growth > 0 ? "#1a2a1a" : "#2a1a1a", padding: "2px 8px", borderRadius: "12px" }}>
                          {dashboard.avg_order_value.growth > 0 ? "↑" : "↓"} {Math.abs(dashboard.avg_order_value.growth)}%
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>${dashboard.avg_order_value.current.toLocaleString()}</div>
                  </div>

                  {/* Customers */}
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div style={{ color: "#888", fontSize: "0.9rem" }}>👥 Customers</div>
                      {dashboard.customers.growth !== 0 && (
                        <span style={{ fontSize: "0.85rem", color: dashboard.customers.growth > 0 ? "#4ade80" : "#ff6b6b", background: dashboard.customers.growth > 0 ? "#1a2a1a" : "#2a1a1a", padding: "2px 8px", borderRadius: "12px" }}>
                          {dashboard.customers.growth > 0 ? "↑" : "↓"} {Math.abs(dashboard.customers.growth)}%
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{dashboard.customers.current.toLocaleString()}</div>
                  </div>

                  {/* Conversion Rate */}
                  {dashboard.conversion_rate && dashboard.conversion_rate.current > 0 && (
                    <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                        <div style={{ color: "#888", fontSize: "0.9rem" }}>📈 Conversion Rate</div>
                        {dashboard.conversion_rate.growth !== 0 && (
                          <span style={{ fontSize: "0.85rem", color: dashboard.conversion_rate.growth > 0 ? "#4ade80" : "#ff6b6b", background: dashboard.conversion_rate.growth > 0 ? "#1a2a1a" : "#2a1a1a", padding: "2px 8px", borderRadius: "12px" }}>
                            {dashboard.conversion_rate.growth > 0 ? "↑" : "↓"} {Math.abs(dashboard.conversion_rate.growth)}%
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#e9edf2" }}>{dashboard.conversion_rate.current}%</div>
                    </div>
                  )}
                </div>

                {/* Customer Stats */}
                {customerStats && (
                  <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a", marginBottom: "2rem" }}>
                    <h3 style={{ fontSize: "1.25rem", marginBottom: "1.5rem", color: "#e9edf2" }}>👥 Customer Insights</h3>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.5rem" }}>
                      <div>
                        <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Total Customers</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e9edf2" }}>{customerStats.total_customers}</div>
                      </div>
                      <div>
                        <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>New Customers</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#4ade80" }}>{customerStats.new_customers}</div>
                      </div>
                      <div>
                        <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Returning Customers</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#6aa6ff" }}>{customerStats.returning_customers}</div>
                      </div>
                      <div>
                        <div style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Avg Customer Value</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e9edf2" }}>${customerStats.avg_customer_value}</div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* ORDERS TAB */}
        {activeTab === "orders" && (
          <div>
            {orders.length === 0 ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📦</div>
                <h3 style={{ marginBottom: "1rem", color: "#e9edf2" }}>No Orders Yet</h3>
                <p style={{ color: "#888" }}>Upload your Shopify orders CSV to see orders here</p>
              </div>
            ) : (
              <div style={{ display: "grid", gap: "1rem" }}>
                {orders.map(order => (
                  <div key={order.id} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                      <div>
                        <div style={{ fontSize: "1.1rem", fontWeight: "600", marginBottom: "0.5rem", color: "#e9edf2" }}>
                          Order #{order.order_number}
                        </div>
                        <div style={{ fontSize: "0.9rem", color: "#888" }}>
                          {order.customer_email}
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#4ade80", marginBottom: "0.25rem" }}>
                          ${order.total_price}
                        </div>
                        <div style={{ fontSize: "0.85rem", color: "#888" }}>
                          {order.items_count} items
                        </div>
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                      {order.financial_status && (
                        <span style={{ padding: "4px 10px", background: "#0a0b0d", borderRadius: "6px", fontSize: "0.8rem", color: "#888" }}>
                          {order.financial_status}
                        </span>
                      )}
                      {order.fulfillment_status && (
                        <span style={{ padding: "4px 10px", background: "#0a0b0d", borderRadius: "6px", fontSize: "0.8rem", color: "#888" }}>
                          {order.fulfillment_status}
                        </span>
                      )}
                      {order.created_at && (
                        <span style={{ padding: "4px 10px", background: "#0a0b0d", borderRadius: "6px", fontSize: "0.8rem", color: "#888" }}>
                          {new Date(order.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* PRODUCTS TAB */}
        {activeTab === "products" && (
          <div>
            {topProducts.length === 0 ? (
              <div style={{ background: "#1a1a1a", padding: "3rem 2rem", borderRadius: "12px", textAlign: "center", border: "1px solid #2a2a2a" }}>
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🏆</div>
                <h3 style={{ marginBottom: "1rem", color: "#e9edf2" }}>No Product Data Yet</h3>
                <p style={{ color: "#888" }}>Upload orders to see top selling products</p>
              </div>
            ) : (
              <div>
                <h3 style={{ fontSize: "1.25rem", marginBottom: "1.5rem", color: "#e9edf2" }}>🏆 Top Selling Products (Last 30 Days)</h3>
                <div style={{ display: "grid", gap: "1rem" }}>
                  {topProducts.map((product, index) => (
                    <div key={index} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                          <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#6aa6ff", background: "#0a0b0d", width: "40px", height: "40px", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                            #{index + 1}
                          </div>
                          <div>
                            <div style={{ fontWeight: "600", fontSize: "1.1rem", marginBottom: "0.25rem", color: "#e9edf2" }}>
                              {product.name}
                            </div>
                            <div style={{ fontSize: "0.9rem", color: "#888" }}>
                              {product.quantity_sold} units sold
                            </div>
                          </div>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#4ade80" }}>
                            ${product.revenue.toLocaleString()}
                          </div>
                          <div style={{ fontSize: "0.85rem", color: "#888" }}>revenue</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* UPLOAD TAB */}
        {activeTab === "upload" && (
          <div>
            <div style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", border: "1px solid #2a2a2a", maxWidth: "900px", margin: "0 auto" }}>
              <h3 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", color: "#e9edf2" }}>📤 Upload Shopify Data</h3>
              
              {/* Orders Export */}
              <div style={{ marginBottom: "3rem" }}>
                <h4 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#e9edf2" }}>📦 Option 1: Individual Orders</h4>
                <p style={{ color: "#888", marginBottom: "1rem", lineHeight: "1.6" }}>
                  For detailed customer and product tracking
                </p>
                <ol style={{ color: "#888", lineHeight: "1.8", paddingLeft: "1.5rem", marginBottom: "1.5rem" }}>
                  <li>Go to your Shopify admin dashboard</li>
                  <li>Click on <strong style={{ color: "#e9edf2" }}>Orders</strong> in the left menu</li>
                  <li>Click the <strong style={{ color: "#e9edf2" }}>Export</strong> button</li>
                  <li>Choose date range</li>
                  <li>Select <strong style={{ color: "#e9edf2" }}>Plain CSV file</strong></li>
                  <li>Click <strong style={{ color: "#e9edf2" }}>Export orders</strong></li>
                </ol>
                
                <div style={{ border: "2px dashed #2a2a2a", borderRadius: "12px", padding: "1.5rem", textAlign: "center", background: "#0a0b0d" }}>
                  <input 
                    type="file" 
                    accept=".csv" 
                    onChange={handleFileUpload}
                    disabled={uploading}
                    style={{ display: "none" }}
                    id="shopify-orders-upload"
                  />
                  <label 
                    htmlFor="shopify-orders-upload" 
                    style={{ 
                      display: "inline-block",
                      padding: "12px 24px", 
                      background: uploading ? "#444" : "#6aa6ff", 
                      color: "#fff", 
                      borderRadius: "8px", 
                      cursor: uploading ? "not-allowed" : "pointer",
                      fontWeight: "600",
                      fontSize: "0.95rem"
                    }}
                  >
                    {uploading ? "Uploading..." : "📦 Upload Orders CSV"}
                  </label>
                </div>
              </div>

              {/* Analytics Reports */}
              <div style={{ borderTop: "1px solid #2a2a2a", paddingTop: "2rem" }}>
                <h4 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "#e9edf2" }}>📊 Option 2: Analytics Reports</h4>
                <p style={{ color: "#888", marginBottom: "1rem", lineHeight: "1.6" }}>
                  For daily metrics and conversion tracking
                </p>
                <ol style={{ color: "#888", lineHeight: "1.8", paddingLeft: "1.5rem", marginBottom: "1.5rem" }}>
                  <li>Go to <strong style={{ color: "#e9edf2" }}>Analytics → Reports</strong> in Shopify</li>
                  <li>Export these reports as CSV:</li>
                  <ul style={{ marginTop: "0.5rem", marginLeft: "1rem" }}>
                    <li><strong style={{ color: "#e9edf2" }}>Total sales over time</strong></li>
                    <li><strong style={{ color: "#e9edf2" }}>Orders over time</strong></li>
                    <li><strong style={{ color: "#e9edf2" }}>Conversion rate over time</strong></li>
                  </ul>
                </ol>

                <div style={{ display: "grid", gap: "1rem" }}>
                  {/* Sales Analytics */}
                  <div style={{ border: "2px dashed #2a2a2a", borderRadius: "12px", padding: "1.5rem", textAlign: "center", background: "#0a0b0d" }}>
                    <input 
                      type="file" 
                      accept=".csv" 
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) handleAnalyticsUpload('import-analytics-sales', file);
                      }}
                      disabled={uploading}
                      style={{ display: "none" }}
                      id="analytics-sales-upload"
                    />
                    <label 
                      htmlFor="analytics-sales-upload" 
                      style={{ 
                        display: "inline-block",
                        padding: "12px 24px", 
                        background: uploading ? "#444" : "#4ade80", 
                        color: "#fff", 
                        borderRadius: "8px", 
                        cursor: uploading ? "not-allowed" : "pointer",
                        fontWeight: "600",
                        fontSize: "0.95rem"
                      }}
                    >
                      📊 Upload Total Sales Over Time
                    </label>
                  </div>

                  {/* Orders Analytics */}
                  <div style={{ border: "2px dashed #2a2a2a", borderRadius: "12px", padding: "1.5rem", textAlign: "center", background: "#0a0b0d" }}>
                    <input 
                      type="file" 
                      accept=".csv" 
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) handleAnalyticsUpload('import-analytics-orders', file);
                      }}
                      disabled={uploading}
                      style={{ display: "none" }}
                      id="analytics-orders-upload"
                    />
                    <label 
                      htmlFor="analytics-orders-upload" 
                      style={{ 
                        display: "inline-block",
                        padding: "12px 24px", 
                        background: uploading ? "#444" : "#4ade80", 
                        color: "#fff", 
                        borderRadius: "8px", 
                        cursor: uploading ? "not-allowed" : "pointer",
                        fontWeight: "600",
                        fontSize: "0.95rem"
                      }}
                    >
                      📊 Upload Orders Over Time
                    </label>
                  </div>

                  {/* Conversion Analytics */}
                  <div style={{ border: "2px dashed #2a2a2a", borderRadius: "12px", padding: "1.5rem", textAlign: "center", background: "#0a0b0d" }}>
                    <input 
                      type="file" 
                      accept=".csv" 
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) handleAnalyticsUpload('import-analytics-conversion', file);
                      }}
                      disabled={uploading}
                      style={{ display: "none" }}
                      id="analytics-conversion-upload"
                    />
                    <label 
                      htmlFor="analytics-conversion-upload" 
                      style={{ 
                        display: "inline-block",
                        padding: "12px 24px", 
                        background: uploading ? "#444" : "#4ade80", 
                        color: "#fff", 
                        borderRadius: "8px", 
                        cursor: uploading ? "not-allowed" : "pointer",
                        fontWeight: "600",
                        fontSize: "0.95rem"
                      }}
                    >
                      📊 Upload Conversion Rate Over Time
                    </label>
                  </div>
                </div>
              </div>

              {hasData && (
                <div style={{ marginTop: "2rem", padding: "1rem", background: "#1a2a1a", borderRadius: "8px", borderLeft: "3px solid #4ade80" }}>
                  <div style={{ color: "#4ade80", fontWeight: "600", marginBottom: "0.5rem" }}>✅ Data Already Imported</div>
                  <div style={{ fontSize: "0.9rem", color: "#888" }}>
                    You have data imported. Upload new CSVs weekly to keep metrics current.
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
