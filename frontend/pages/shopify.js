// Add after your existing state declarations
const [uploadingFile, setUploadingFile] = useState(null);
const [uploadStatus, setUploadStatus] = useState('');

const handleFileUpload = async (file, reportType) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    setUploadStatus('Uploading...');
    const res = await fetch(`${API}/shopify/upload?report_type=${reportType}`, {
      method: 'POST',
      body: formData
    });
    
    if (res.ok) {
      const result = await res.json();
      setUploadStatus(`✓ Uploaded ${result.filename} (${result.records} rows)`);
      setTimeout(() => loadShopifyData(), 1000);
    }
  } catch (err) {
    setUploadStatus(`Error: ${err.message}`);
  }
};

// Add this JSX before the "Configuration" card:
<div className="card">
  <h3 className="title">Upload Shopify Reports</h3>
  <div className="muted" style={{ marginBottom: 16 }}>
    Upload your Shopify Analytics exports (CSV files)
  </div>
  
  {uploadStatus && (
    <div style={{ padding: 12, background: '#f0f9ff', borderRadius: 8, marginBottom: 16 }}>
      {uploadStatus}
    </div>
  )}
  
  <div style={{ display: 'grid', gap: 12 }}>
    {['orders', 'conversion', 'products', 'sales'].map(type => (
      <div key={type} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <label style={{ flex: 1, textTransform: 'capitalize' }}>{type} Report:</label>
        <input 
          type="file" 
          accept=".csv"
          onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0], type)}
          style={{ flex: 2 }}
        />
      </div>
    ))}
  </div>
</div>
