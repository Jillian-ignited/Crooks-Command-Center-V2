// frontend/pages/shopify.js
import { useEffect, useState } from "react";

const API = typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_API_BASE || "") : "";

export default function ShopifyPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [reportType, setReportType] = useState('auto');

  const loadShopifyData = async () => {
    if (typeof window === 'undefined') return;
    
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API}/api/shopify/dashboard`);
      
      if (!res.ok) {
        throw new Error(`Failed to load: HTTP ${res.status}`);
      }
      
      const result = await res.json();
      setData(result);
      setConnectionStatus('connected');
    } catch (err) {
      console.error('Failed to load Shopify data:', err);
      setError(`Unable to load dashboard: ${err.message}`);
      setConnectionStatus('disconnected');
      
      setData({
        store_name: "No data uploaded",
        orders_today: 0,
        revenue_today: 0,
        products_count: 0,
        top_products: []
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!uploadFile) {
      setUploadStatus('Please select a file');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', uploadFile);
    
    try {
      setUploadStatus('Uploading...');
      const res = await fetch(`${API}/api/shopify/upload?report_type=${reportType}`, {
        method: 'POST',
        body: formData
      });
      
      if (res.ok) {
        const result = await res.json();
        setUploadStatus(`Uploaded ${result.filename} (${result.records} rows)`);
        setTimeout(() => {
          loadShopifyData();
          setUploadStatus('');
        }, 2000);
      } else {
        throw new Error(`Upload failed: ${res.status}`);
      }
    } catch (err) {
      setUploadStatus(`Error: ${err.message}`);
    }
  };

  const testConnection = async () => {
    if (typeof window === 'undefined') return;
    
    setConnectionStatus('checking');
    try {
      const res = await fetch(`${API}/api/shopify/test-connection`);
      if (res.ok) {
        const result = await res.json();
        setConnectionStatus(result.connected ? 'connected' : 'disconnected');
        if (result.connected) loadShopifyData();
      } else {
        setConnectionStatus('disconnected');
      }
    } catch (err) {
      setConnectionStatus('disconnected');
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      loadShopifyData();
    }
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Shopify Integration</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Shopify Dashboard</h1>

      {error && (
        <div style={{ background: '#fee', border: '1px solid #f99', padding: '1rem', borderRadius: 8, marginBottom: '1rem', color: '#c33' }}>
          {error}
        </div>
      )}

      <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", marginBottom: "2rem" }}>
        <h2>Upload Shopify Reports</h2>
        <p style={{ color: "#888", marginBottom: "1rem" }}>Upload CSV exports from Shopify Analytics</p>
        
        {uploadStatus && (
          <div style={{ padding: '0.75rem', background: '#f0f9ff', borderRadius: 8, marginBottom: '1rem' }}>
            {uploadStatus}
          </div>
        )}
        
        <div style={{ display: 'grid', gap: '1rem' }}>
          <label>
            Report Type
            <select value={reportType} onChange={(e) => setReportType(e.target.value)} style={{ width: "100%", padding: 8, marginTop: 4 }}>
              <option value="auto">Auto-detect</option>
              <option value="orders">Orders Over Time</option>
              <option value="conversion">Conversion Rate</option>
              <option value="products">Sales by Product</option>
              <option value="sales">Total Sales</option>
            </select>
          </label>
          
          <label>
            CSV File
            <input type="file" accept=".csv" onChange={(e) => setUploadFile(e.target.files?.[0])} style={{ width: "100%", marginTop: 4 }} />
          </label>
          
          <button onClick={handleFileUpload} disabled={!uploadFile} style={{ padding: "10px", cursor: uploadFile ? "pointer" : "not-allowed" }}>
            Upload Report
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
          <div style={{ fontSize: "0.85rem", color: "#888" }}>Orders Today</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{data?.orders_today || 0}</div>
        </div>
        
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
          <div style={{ fontSize: "0.85rem", color: "#888" }}>Revenue Today</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>${(data?.revenue_today || 0).toLocaleString()}</div>
        </div>
        
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
          <div style={{ fontSize: "0.85rem", color: "#888" }}>Total Products</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{(data?.products_count || 0).toLocaleString()}</div>
        </div>
      </div>

      {data?.top_products && data.top_products.length > 0 && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
          <h2>Top Products</h2>
          <div style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
            {data.top_products.map((product, i) => (
              <div key={i} style={{ padding: "0.75rem", background: "#2a2a2a", borderRadius: "6px" }}>
                <div style={{ fontWeight: "bold" }}>{product.title}</div>
                <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "0.25rem" }}>
                  {product.sales_count} sales | ${product.revenue}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
