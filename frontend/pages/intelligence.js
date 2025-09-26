import { useState, useEffect, useCallback } from "react";
import IntelligencePanel from "../components/IntelligencePanel";

const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function IntelligencePage() {
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Enhanced file refresh with error handling
  const refreshFiles = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch(`${API}/intelligence/uploads`);
      
      if (!res.ok) {
        throw new Error(`Failed to load files: HTTP ${res.status}`);
      }
      
      const json = await res.json();
      setFiles(json.files || []);
    } catch (err) {
      console.error('Failed to refresh files:', err);
      setError(`Unable to load uploaded files: ${err.message}`);
      setFiles([]);
    }
  }, []);

  // Enhanced report generation with comprehensive error handling
  const generateReport = useCallback(async () => {
    if (!brands.trim()) {
      setError("Please enter at least one brand name");
      return;
    }

    setBusy(true);
    setError(null);
    setSuccess(null);
    
    try {
      const brandList = brands.split(",").map(s => s.trim()).filter(Boolean);
      
      if (brandList.length === 0) {
        throw new Error("Please enter valid brand names");
      }

      const body = { 
        brands: brandList, 
        lookback_days: Number(days) 
      };
      
      const res = await fetch(`${API}/intelligence/report`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify(body) 
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Report generation failed: HTTP ${res.status} - ${errorText}`);
      }
      
      const result = await res.json();
      setData(result);
      setSuccess("Intelligence report generated successfully!");
      
      // Auto-clear success message
      setTimeout(() => setSuccess(null), 5000);
      
    } catch (err) {
      console.error('Report generation failed:', err);
      setError(`Failed to generate report: ${err.message}`);
      setData(null);
    } finally {
      setBusy(false);
    }
  }, [brands, days]);

  // Enhanced file upload with validation
  const uploadFiles = useCallback(async (selectedFiles) => {
    if (!selectedFiles || selectedFiles.length === 0) return;
    
    // Validate file types
    const allowedTypes = ['.csv', '.json', '.jsonl'];
    const invalidFiles = Array.from(selectedFiles).filter(file => 
      !allowedTypes.some(type => file.name.toLowerCase().endsWith(type))
    );
    
    if (invalidFiles.length > 0) {
      setError(`Invalid file types: ${invalidFiles.map(f => f.name).join(', ')}. Only CSV, JSON, and JSONL files are allowed.`);
      return;
    }
    
    setBusy(true);
    setError(null);
    setSuccess(null);
    
    try {
      const form = new FormData();
      Array.from(selectedFiles).forEach(file => form.append("files", file));
      
      const res = await fetch(`${API}/intelligence/upload`, { 
        method: "POST", 
        body: form 
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Upload failed: HTTP ${res.status} - ${errorText}`);
      }
      
      const result = await res.json();
      await refreshFiles();
      
      setSuccess(`Successfully uploaded ${selectedFiles.length} file(s)`);
      setTimeout(() => setSuccess(null), 5000);
      
    } catch (err) {
      console.error('Upload failed:', err);
      setError(`Upload failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }, [refreshFiles]);

  // Enhanced file removal with confirmation
  const removeFile = useCallback(async (filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    
    setBusy(true);
    setError(null);
    
    try {
      const res = await fetch(`${API}/intelligence/upload/${encodeURIComponent(filename)}`, { 
        method: "DELETE" 
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Delete failed: HTTP ${res.status} - ${errorText}`);
      }
      
      await refreshFiles();
      setSuccess(`Deleted "${filename}" successfully`);
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      console.error('Delete failed:', err);
      setError(`Failed to delete file: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }, [refreshFiles]);

  // Drag & Drop handlers
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    
    try {
      if (e.dataTransfer?.files?.length) {
        uploadFiles(e.dataTransfer.files);
      }
    } catch (err) {
      setError(`Drop failed: ${err.message}`);
    }
  }, [uploadFiles]);

  const handleDragOver = useCallback((e) => { 
    e.preventDefault(); 
    setDragOver(true); 
  }, []);

  const handleDragLeave = useCallback(() => setDragOver(false), []);

  // Load files on component mount
  useEffect(() => { 
    refreshFiles(); 
  }, [refreshFiles]);

  // Clear messages when user starts new actions
  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="grid">
      {/* Status Messages */}
      {error && (
        <div className="card" style={{ border: '1px solid var(--danger)', background: 'rgba(239, 68, 68, 0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="title" style={{ color: 'var(--danger)', margin: '0 0 8px 0' }}>Error</h3>
              <div style={{ color: 'var(--danger)' }}>{error}</div>
            </div>
            <button 
              className="button" 
              onClick={() => setError(null)}
              style={{ background: 'var(--danger)', minWidth: 'auto', padding: '6px 12px' }}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {success && (
        <div className="card" style={{ border: '1px solid var(--ok)', background: 'rgba(52, 211, 153, 0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="title" style={{ color: 'var(--ok)', margin: '0 0 8px 0' }}>Success</h3>
              <div style={{ color: 'var(--ok)' }}>{success}</div>
            </div>
            <button 
              className="button" 
              onClick={() => setSuccess(null)}
              style={{ background: 'var(--ok)', minWidth: 'auto', padding: '6px 12px' }}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* File Upload Section */}
      <div className="card">
        <h3 className="title">Upload Data Files</h3>
        
        {/* Drag & Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`dropzone ${dragOver ? 'dragover' : ''}`}
          style={{ marginBottom: 12 }}
        >
          {dragOver ? "Release to upload..." : "Drag & drop CSV, JSON, or JSONL files here"}
        </div>

        {/* File Input */}
        <input 
          type="file" 
          multiple 
          accept=".csv,.json,.jsonl"
          onChange={(e) => {
            clearMessages();
            uploadFiles(e.target.files);
          }}
          disabled={busy}
          style={{ marginBottom: 8 }}
        />

        <div className="muted">
          <strong>Supported formats:</strong> CSV, JSON, JSONL<br/>
          <strong>Expected columns:</strong> brand, platform, date, likes, comments, shares, text, url
        </div>
      </div>

      {/* Uploaded Files Section */}
      <div className="card">
        <div className="row" style={{ justifyContent: 'space-between', marginBottom: 12 }}>
          <h3 className="title" style={{ margin: 0 }}>Uploaded Files ({files.length})</h3>
          <button 
            className="button" 
            onClick={() => {
              clearMessages();
              refreshFiles();
            }}
            disabled={busy}
            style={{ minWidth: 'auto' }}
          >
            {busy ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        
        {files.length === 0 ? (
          <div className="muted">No files uploaded yet. Upload some data files to get started.</div>
        ) : (
          <div style={{ maxHeight: 300, overflowY: 'auto' }}>
            {files.map((filename) => (
              <div key={filename} className="row" style={{ 
                justifyContent: "space-between", 
                marginBottom: 8,
                padding: 8,
                background: 'rgba(255,255,255,0.02)',
                borderRadius: 6,
                border: '1px solid var(--line)'
              }}>
                <span style={{ wordBreak: 'break-all' }}>{filename}</span>
                <button 
                  className="button" 
                  onClick={() => removeFile(filename)} 
                  disabled={busy}
                  style={{ 
                    background: 'var(--danger)', 
                    minWidth: 'auto',
                    padding: '4px 8px',
                    fontSize: 12
                  }}
                >
                  {busy ? '...' : 'Delete'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Report Generation Section */}
      <div className="card">
        <h3 className="title">Generate Intelligence Report</h3>
        <div className="row" style={{ marginBottom: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div style={{ flex: '1', minWidth: 200 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 14, color: 'var(--muted)' }}>
              Brand Names (comma-separated)
            </label>
            <input 
              type="text"
              value={brands} 
              onChange={(e) => {
                setBrands(e.target.value);
                clearMessages();
              }}
              placeholder="e.g., Crooks & Castles, Stussy, Supreme"
              disabled={busy}
              style={{ width: '100%' }}
            />
          </div>
          
          <div style={{ minWidth: 120 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 14, color: 'var(--muted)' }}>
              Days to Analyze
            </label>
            <input 
              type="number" 
              min="1" 
              max="365" 
              value={days} 
              onChange={(e) => {
                setDays(Math.max(1, Math.min(365, parseInt(e.target.value) || 1)));
                clearMessages();
              }}
              disabled={busy}
              style={{ width: '100%' }}
            />
          </div>
          
          <div style={{ alignSelf: 'flex-end' }}>
            <button 
              className="button" 
              onClick={() => {
                clearMessages();
                generateReport();
              }}
              disabled={busy || !brands.trim()}
              style={{ padding: '10px 16px' }}
            >
              {busy ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>
        
        <div className="muted">
          {brands.trim() ? 
            `Will analyze last ${days} days for: ${brands}` : 
            'Enter brand names to generate a report'
          }
        </div>
      </div>

      {/* Intelligence Analysis Results */}
      <IntelligencePanel data={data} />
    </div>
  );
}
