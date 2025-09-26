import { useEffect, useState, useCallback } from "react";

// API configuration with fallback
const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

// IntelligencePanel component
export default function IntelligencePanel({ data }) {
  if (!data) {
    return (
      <div className="card">
        <h3 className="title">Intelligence Analysis</h3>
        <div className="muted">No data available. Run a report to see analysis.</div>
      </div>
    );
  }

  // Handle API errors
  if (data.error) {
    return (
      <div className="card">
        <h3 className="title">Intelligence Analysis - Error</h3>
        <div style={{ color: 'var(--danger)' }}>
          Error: {data.error}
        </div>
      </div>
    );
  }

  return (
    <div className="grid">
      {/* Brand Performance Summary */}
      {data.brand_performance && (
        <div className="card">
          <h3 className="title">Brand Performance Summary</h3>
          {Object.entries(data.brand_performance).map(([brand, metrics]) => (
            <div key={brand} style={{ marginBottom: 16 }}>
              <h4 style={{ margin: '0 0 8px 0', color: 'var(--brand)' }}>{brand}</h4>
              <div className="row" style={{ gap: 16 }}>
                <div className="pill">
                  Posts: {metrics.total_posts || 0}
                </div>
                <div className="pill">
                  Avg Engagement: {metrics.avg_engagement || 0}
                </div>
                <div className="pill">
                  Sentiment: {metrics.sentiment_score || 'N/A'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Top Performing Content */}
      {data.top_content && data.top_content.length > 0 && (
        <div className="card">
          <h3 className="title">Top Performing Content</h3>
          <div style={{ maxHeight: 400, overflowY: 'auto' }}>
            {data.top_content.map((content, index) => (
              <div key={index} style={{ 
                padding: 12, 
                border: '1px solid var(--line)', 
                borderRadius: 8, 
                marginBottom: 8,
                background: 'rgba(255,255,255,0.02)'
              }}>
                <div className="row" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
                  <span className="pill">{content.brand || 'Unknown Brand'}</span>
                  <span className="pill">{content.platform || 'Unknown Platform'}</span>
                </div>
                <p style={{ margin: '0 0 8px 0', fontSize: 14 }}>
                  {content.text ? content.text.substring(0, 200) + (content.text.length > 200 ? '...' : '') : 'No content available'}
                </p>
                <div className="row" style={{ fontSize: 12, color: 'var(--muted)' }}>
                  <span>Likes: {content.likes || 0}</span>
                  <span>Comments: {content.comments || 0}</span>
                  <span>Shares: {content.shares || 0}</span>
                  {content.url && (
                    <a href={content.url} target="_blank" rel="noopener noreferrer">View</a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sentiment Analysis */}
      {data.sentiment_analysis && (
        <div className="card">
          <h3 className="title">Sentiment Analysis</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--ok)' }}>
                {data.sentiment_analysis.positive || 0}%
              </div>
              <div className="muted">Positive</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--warn)' }}>
                {data.sentiment_analysis.neutral || 0}%
              </div>
              <div className="muted">Neutral</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--danger)' }}>
                {data.sentiment_analysis.negative || 0}%
              </div>
              <div className="muted">Negative</div>
            </div>
          </div>
        </div>
      )}

      {/* Key Insights */}
      {data.insights && data.insights.length > 0 && (
        <div className="card">
          <h3 className="title">Key Insights</h3>
          <ul>
            {data.insights.map((insight, index) => (
              <li key={index}>{insight}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Trending Topics */}
      {data.trending_topics && data.trending_topics.length > 0 && (
        <div className="card">
          <h3 className="title">Trending Topics</h3>
          <div className="row" style={{ flexWrap: 'wrap', gap: 8 }}>
            {data.trending_topics.map((topic, index) => (
              <span key={index} className="pill" style={{ background: 'var(--brand)', color: 'white' }}>
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Competitive Analysis */}
      {data.competitive_analysis && (
        <div className="card">
          <h3 className="title">Competitive Analysis</h3>
          {Object.entries(data.competitive_analysis).map(([competitor, analysis]) => (
            <div key={competitor} style={{ marginBottom: 16 }}>
              <h4 style={{ margin: '0 0 8px 0' }}>{competitor}</h4>
              <div className="muted" style={{ marginBottom: 8 }}>
                {analysis.summary || 'No summary available'}
              </div>
              {analysis.metrics && (
                <div className="row" style={{ gap: 12 }}>
                  <span className="pill">Engagement: {analysis.metrics.engagement || 0}</span>
                  <span className="pill">Growth: {analysis.metrics.growth || 0}%</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Raw Data Debug (for development) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="card">
          <h3 className="title">Debug Data</h3>
          <pre style={{ 
            fontSize: 12, 
            background: '#000', 
            padding: 12, 
            borderRadius: 8, 
            overflow: 'auto',
            maxHeight: 300
          }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

// Enhanced IntelligencePage component with better error handling
export function IntelligencePage() {
  const [brands, setBrands] = useState("Crooks & Castles, Stussy, Supreme");
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  // Enhanced file refresh with error handling
  const refreshFiles = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch(`${API}/intelligence/uploads`);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const json = await res.json();
      setFiles(json.files || []);
    } catch (err) {
      console.error('Failed to refresh files:', err);
      setError(`Failed to load files: ${err.message}`);
      setFiles([]);
    }
  }, []);

  // Enhanced report generation with error handling
  const run = useCallback(async () => {
    setBusy(true);
    setError(null);
    
    try {
      const body = { 
        brands: brands.split(",").map(s => s.trim()).filter(Boolean), 
        lookback_days: Number(days) 
      };
      
      const res = await fetch(`${API}/intelligence/report`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify(body) 
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }
      
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error('Failed to generate report:', err);
      setError(`Failed to generate report: ${err.message}`);
      setData(null);
    } finally {
      setBusy(false);
    }
  }, [brands, days]);

  // Enhanced upload with error handling
  const upload = useCallback(async (selected) => {
    if (!selected || selected.length === 0) return;
    
    setBusy(true);
    setError(null);
    
    try {
      const form = new FormData();
      Array.from(selected).forEach(file => form.append("files", file));
      
      const res = await fetch(`${API}/intelligence/upload`, { 
        method: "POST", 
        body: form 
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }
      
      await refreshFiles();
    } catch (err) {
      console.error('Upload failed:', err);
      setError(`Upload failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }, [refreshFiles]);

  // Enhanced file removal with error handling
  const remove = useCallback(async (name) => {
    setBusy(true);
    setError(null);
    
    try {
      const res = await fetch(`${API}/intelligence/upload/${encodeURIComponent(name)}`, { 
        method: "DELETE" 
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }
      
      await refreshFiles();
    } catch (err) {
      console.error('Delete failed:', err);
      setError(`Delete failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }, [refreshFiles]);

  // Drag & Drop handlers with error handling
  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    
    try {
      if (e.dataTransfer?.files?.length) {
        upload(e.dataTransfer.files);
      }
    } catch (err) {
      console.error('Drop failed:', err);
      setError(`Drop failed: ${err.message}`);
    }
  }, [upload]);

  const onDragOver = useCallback((e) => { 
    e.preventDefault(); 
    setDragOver(true); 
  }, []);

  const onDragLeave = useCallback(() => setDragOver(false), []);

  // Load files on component mount
  useEffect(() => { 
    refreshFiles(); 
  }, [refreshFiles]);

  return (
    <div className="grid">
      {/* Error Display */}
      {error && (
        <div className="card" style={{ border: '1px solid var(--danger)' }}>
          <h3 className="title" style={{ color: 'var(--danger)' }}>Error</h3>
          <div style={{ color: 'var(--danger)' }}>{error}</div>
          <button className="button" onClick={() => setError(null)} style={{ marginTop: 12 }}>
            Dismiss
          </button>
        </div>
      )}

      <div className="card">
        <h3 className="title">Upload Scraped Files (CSV/JSON)</h3>

        {/* Drag & Drop Zone */}
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          className={`dropzone ${dragOver ? 'dragover' : ''}`}
        >
          {dragOver ? "Release to upload..." : "Drag & drop files here or click to select"}
        </div>

        {/* Classic input as fallback */}
        <input 
          type="file" 
          multiple 
          onChange={(e) => upload(e.target.files)} 
          disabled={busy}
          style={{ marginTop: 12 }}
        />

        <div className="muted" style={{ marginTop: 8 }}>
          Expected columns: brand, platform, date, likes, comments, shares, text, url
        </div>
      </div>

      <div className="card">
        <h3 className="title">Uploaded Files ({files.length})</h3>
        {files.length === 0 ? (
          <div className="muted">No files uploaded yet.</div>
        ) : (
          <div style={{ maxHeight: 300, overflowY: 'auto' }}>
            {files.map((f) => (
              <div key={f} className="row" style={{ justifyContent: "space-between", marginBottom: 8 }}>
                <span>{f}</span>
                <button 
                  className="button" 
                  onClick={() => remove(f)} 
                  disabled={busy}
                  style={{ background: 'var(--danger)' }}
                >
                  {busy ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            ))}
          </div>
        )}
        <button 
          className="button" 
          onClick={refreshFiles} 
          disabled={busy}
          style={{ marginTop: 12 }}
        >
          {busy ? 'Refreshing...' : 'Refresh Files'}
        </button>
      </div>

      <div className="card">
        <h3 className="title">Generate Intelligence Report</h3>
        <div className="row" style={{ marginBottom: 12 }}>
          <input 
            style={{ flex: 1 }} 
            value={brands} 
            onChange={e => setBrands(e.target.value)} 
            placeholder="Enter brands separated by commas"
            disabled={busy}
          />
          <input 
            type="number" 
            min="1" 
            max="60" 
            value={days} 
            onChange={e => setDays(e.target.value)} 
            style={{ width: 100 }}
            disabled={busy}
          />
          <button 
            className="button" 
            onClick={run} 
            disabled={busy || brands.trim().length === 0}
          >
            {busy ? 'Generating...' : 'Run Report'}
          </button>
        </div>
        <div className="muted">
          Analyzes last {days} days for: {brands || 'No brands specified'}
        </div>
      </div>

      <IntelligencePanel data={data} />
    </div>
  );
}
