import React, { useState, useEffect } from 'react';
import { Upload, TrendingUp, Package, ShoppingCart, Users, DollarSign, ShoppingBag, ArrowUp } from 'lucide-react';

const API_BASE = '/api';

export default function ShopifyPage() {
  const [metrics, setMetrics] = useState(null);
  const [customerStats, setCustomerStats] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadStatus, setUploadStatus] = useState({});

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [metricsRes, statsRes, productsRes, ordersRes] = await Promise.all([
        fetch(`${API_BASE}/shopify/dashboard?period=30d`),
        fetch(`${API_BASE}/shopify/customer-stats?days=30`),
        fetch(`${API_BASE}/shopify/top-products?limit=10`),
        fetch(`${API_BASE}/shopify/orders?limit=10`)
      ]);

      const metricsData = await metricsRes.json();
      const statsData = await statsRes.json();
      const productsData = await productsRes.json();
      const ordersData = await ordersRes.json();

      setMetrics(metricsData);
      setCustomerStats(statsData);
      setTopProducts(productsData.products || []);
      setRecentOrders(ordersData.orders || []);
    } catch (error) {
      console.error('Error fetching Shopify data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file, endpoint, uploadKey) => {
    setUploadStatus(prev => ({ ...prev, [uploadKey]: 'uploading' }));
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/shopify/${endpoint}`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUploadStatus(prev => ({ 
          ...prev, 
          [uploadKey]: `✅ ${result.message}` 
        }));
        // Refresh data after successful upload
        setTimeout(() => fetchAllData(), 1000);
      } else {
        setUploadStatus(prev => ({ 
          ...prev, 
          [uploadKey]: `❌ ${result.message || 'Upload failed'}` 
        }));
      }
    } catch (error) {
      setUploadStatus(prev => ({ 
        ...prev, 
        [uploadKey]: `❌ Upload failed: ${error}` 
      }));
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading Shopify data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Shopify Analytics</h1>
          <p className="text-gray-600">Track your store performance and import data</p>
        </div>

        {/* Upload Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Metrics Upload */}
          <UploadSection
            title="Import Metrics CSV"
            description="Upload sales & conversion data (can upload multiple CSVs - they merge automatically)"
            icon={<TrendingUp className="w-6 h-6" />}
            uploadKey="metrics"
            endpoint="import-metrics-csv"
            status={uploadStatus.metrics}
            onFileUpload={handleFileUpload}
          />

          {/* Products Upload */}
          <UploadSection
            title="Import Products CSV"
            description="Upload product sales data to track top sellers"
            icon={<Package className="w-6 h-6" />}
            uploadKey="products"
            endpoint="import-products-csv"
            status={uploadStatus.products}
            onFileUpload={handleFileUpload}
          />

          {/* Orders Upload */}
          <UploadSection
            title="Import Orders CSV"
            description="Upload order history for detailed tracking"
            icon={<ShoppingCart className="w-6 h-6" />}
            uploadKey="orders"
            endpoint="import-orders-csv"
            status={uploadStatus.orders}
            onFileUpload={handleFileUpload}
          />

          {/* Customers Upload */}
          <UploadSection
            title="Import Customers CSV"
            description="Upload customer data for segmentation analysis"
            icon={<Users className="w-6 h-6" />}
            uploadKey="customers"
            endpoint="import-customers-csv"
            status={uploadStatus.customers}
            onFileUpload={handleFileUpload}
          />
        </div>

        {/* Metrics Dashboard */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Revenue"
              value={formatCurrency(metrics.summary.total_revenue)}
              icon={<DollarSign className="w-6 h-6" />}
              color="bg-green-500"
            />
            <MetricCard
              title="Total Orders"
              value={metrics.summary.total_orders.toString()}
              icon={<ShoppingBag className="w-6 h-6" />}
              color="bg-blue-500"
            />
            <MetricCard
              title="Avg Order Value"
              value={formatCurrency(metrics.summary.avg_order_value)}
              icon={<TrendingUp className="w-6 h-6" />}
              color="bg-purple-500"
            />
            <MetricCard
              title="Conversion Rate"
              value={`${metrics.summary.conversion_rate.toFixed(2)}%`}
              icon={<ArrowUp className="w-6 h-6" />}
              color="bg-orange-500"
            />
          </div>
        )}

        {/* Customer Stats */}
        {customerStats && customerStats.total_customers > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Users className="w-6 h-6 text-blue-600" />
              Customer Statistics
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Customers</p>
                <p className="text-2xl font-bold text-gray-900">{customerStats.total_customers}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">New Customers</p>
                <p className="text-2xl font-bold text-green-600">{customerStats.new_customers}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Returning</p>
                <p className="text-2xl font-bold text-blue-600">{customerStats.returning_customers}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Retention Rate</p>
                <p className="text-2xl font-bold text-purple-600">{customerStats.customer_retention_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Top Products */}
        {topProducts.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Package className="w-6 h-6 text-blue-600" />
              Top Products by Revenue
            </h2>
            <div className="space-y-3">
              {topProducts.map((product, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{product.title}</p>
                    <p className="text-sm text-gray-600">{product.vendor} • {product.type}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-gray-900">{formatCurrency(product.total_sales)}</p>
                    <p className="text-sm text-gray-600">{product.units_sold} units sold</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Orders */}
        {recentOrders.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ShoppingCart className="w-6 h-6 text-blue-600" />
              Recent Orders
            </h2>
            <div className="space-y-3">
              {recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{order.id}</p>
                    <p className="text-sm text-gray-600">{order.customer_name} • {order.items_count} items</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-gray-900">{formatCurrency(order.total)}</p>
                    <p className="text-sm text-gray-600">{formatDate(order.created_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!metrics?.summary.total_orders && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Data Yet</h3>
            <p className="text-gray-600">Upload your Shopify CSV files above to get started!</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Upload Section Component
function UploadSection({ title, description, icon, uploadKey, endpoint, status, onFileUpload }) {
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file, endpoint, uploadKey);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
          {icon}
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-gray-900 mb-1">{title}</h3>
          <p className="text-sm text-gray-600 mb-3">{description}</p>
          
          <label className="inline-block">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors">
              <Upload className="w-4 h-4" />
              Choose CSV File
            </span>
          </label>

          {status && (
            <div className={`mt-3 p-3 rounded-lg text-sm ${
              status.includes('✅') ? 'bg-green-50 text-green-800' :
              status.includes('uploading') ? 'bg-blue-50 text-blue-800' :
              'bg-red-50 text-red-800'
            }`}>
              {status}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Metric Card Component
function MetricCard({ title, value, icon, color }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg text-white ${color}`}>
          {icon}
        </div>
      </div>
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
