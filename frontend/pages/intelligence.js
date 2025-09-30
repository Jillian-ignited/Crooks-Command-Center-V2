// frontend/pages/intelligence.js
import { useState, useEffect } from "react";

export default function Intelligence() {
  const [file, setFile] = useState(null);
  const [brand, setBrand] = useState("Crooks & Castles");
  const [source, setSource] = useState("apify_instagram");
  const [status, setStatus] = useState("");
  const [uploadResult, setUploadResult] = useState(null);
  const [summary, setSummary] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  // Load summary and file list on mount
  useEffect(() => {
    loadSummary();
    loadFiles();
  }, []);

  async function loadSummary() {
    try {
      const res = await fetch('/api/intelligence/summary');
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  }

  async function loadFiles() {
    try {
      const res = await fetch('/api/intelligence/files');
      const data = await res.json();
      setFiles(data.files || []);
    } catch (err) {
      console.error('Failed to load files:', err);
    }
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("source", source);
    formData.append("brand", brand);

    try {
      setStatus("Uploading and processing with AI...");
      const res = await fetch('/api/intelligence/upload', {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);
      
      setUploadResult(data);
      setStatus("✅ " + data.message);
      
      // Reload data after a delay to show processed insights
      setTimeout(() => {
        loadSummary();
        loadFiles();
      }, 3000);
      
    } catch (err) {
      console.error(err);
      setStatus(`Error: ${err.message}`);
    }
  }

  async function viewFileInsights(fileId) {
    try {
      const res = await fetch(`/api/intelligence/files/${fileId}`);
      const data = await res.json();
      setSelectedFile(data);
    } catch (err) {
      console.error('Failed to load file insights:', err);
    }
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Intelligence Upload & Analysis</h1>

      {/* Upload Form */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", marginBottom: "2rem" }}>
        <h2>Upload Data File</h2>
        <form onSubmit={handleUpload} style={{ display: "grid", gap: 12, maxWidth: 520 }}>
          <label>
            Source
            <select value={source} onChange={(e) => setSource(e.target.value)} style={{ marginLeft: 8, padding: 4 }}>
              <option value="apify_instagram">Instagram (Apify)</option>
              <option value="apify_tiktok">TikTok (Apify)</option>
              <option value="apify_hashtag">Hashtag Analysis (Apify)</option>
              <option value="shopify">Shopify</option>
              <option value="manual">Manual</option>
            </select>
          </label>
          
          <label>
            Brand
            <input 
              value={brand} 
              onChange={(e) => setBrand(e.target.value)} 
              placeholder="Crooks & Castles"
              style={{ marginLeft: 8, padding: 4 }}
            />
          </label>
          
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} accept=".csv,.json,.xlsx,.xls" />
          <button type="submit" style={{ padding: "8px 16px", cursor: "pointer" }}>Upload & Analyze</button>
        </form>
        
        {status && <p style={{ marginTop: 12, fontWeight: "bold" }}>{status}</p>}
      </div>

      {/* AI Insights Summary */}
      {summary?.insights && Object.keys(summary.insights).length > 0 && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", marginBottom: "2rem" }}>
          <h2>Latest AI Insights</h2>
          <p style={{ color: "#888", fontSize: "0.9rem" }}>
            Last updated: {summary.last_updated ? new Date(summary.last_updated).toLocaleString() : 'N/A'}
          </p>
          
          {/* Key Insights */}
          {summary.insights.insights && (
            <div style={{ marginTop: "1rem" }}>
              <h3>Key Insights</h3>
              <ul>
                {Array.isArray(summary.insights.insights) ? (
                  summary.insights.insights.map((insight, i) => (
                    <li key={i} style={{ marginBottom: "0.5rem" }}>{insight}</li>
                  ))
                ) : (
                  <li>{summary.insights.insights}</li>
                )}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {summary.insights.recommendations && (
            <div style={{ marginTop: "1rem" }}>
              <h3>🎯 Recommendations</h3>
              <ul>
                {Array.isArray(summary.insights.recommendations) ? (
                  summary.insights.recommendations.map((rec, i) => (
                    <li key={i} style={{ marginBottom: "0.5rem" }}>{rec}</li>
                  ))
                ) : (
                  <li>{summary.insights.recommendations}</li>
                )}
              </ul>
            </div>
          )}

          {/* Trending Topics */}
          {summary.insights.trending_topics && (
            <div style={{ marginTop: "1rem" }}>
              <h3>📈 Trending Topics</h3>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {Array.isArray(summary.insights.trending_topics) ? (
                  summary.insights.trending_topics.map((topic, i) => (
                    <span key={i} style={{ 
                      background: "#2a2a2a", 
                      padding: "4px 12px", 
                      borderRadius: "4px",
                      fontSize: "0.9rem"
                    }}>
                      {typeof topic === 'string' ? topic : topic.name || JSON.stringify(topic)}
                    </span>
                  ))
                ) : (
                  <span>{summary.insights.trending_topics}</span>
                )}
              </div>
            </div>
          )}

          {/* Hashtag Strategy */}
          {summary.insights.hashtag_strategy && (
            <div style={{ marginTop: "1rem" }}>
              <h3>#️⃣ Hashtag Strategy</h3>
              <p>{summary.insights.hashtag_strategy}</p>
            </div>
          )}
        </div>
      )}

      {/* Uploaded Files List */}
      <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px" }}>
        <h2>Uploaded Files ({files.length})</h2>
        <div style={{ display: "grid", gap: "12px", marginTop: "1rem" }}>
          {files.map(f => (
            <div key={f.id} style={{ 
              background: "#2a2a2a", 
              padding: "12px", 
              borderRadius: "4px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <div>
                <strong>{f.filename}</strong>
                <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "4px" }}>
                  Source: {f.source} | Brand: {f.brand} | 
                  {f.processed ? " ✅ Processed" : " ⏳ Processing..."}
                </div>
                <div style={{ fontSize: "0.8rem", color: "#666" }}>
                  {new Date(f.uploaded_at).toLocaleString()}
                </div>
              </div>
              {f.has_insights && (
                <button 
                  onClick={() => viewFileInsights(f.id)}
                  style={{ padding: "6px 12px", cursor: "pointer" }}
                >
                  View Insights
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Selected File Insights Modal */}
      {selectedFile && (
        <div style={{ 
          position: "fixed", 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          background: "rgba(0,0,0,0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem",
          zIndex: 1000
        }}>
          <div style={{ 
            background: "#1a1a1a", 
            padding: "2rem", 
            borderRadius: "8px", 
            maxWidth: "800px",
            maxHeight: "80vh",
            overflow: "auto",
            position: "relative"
          }}>
            <button 
              onClick={() => setSelectedFile(null)}
              style={{ position: "absolute", top: "1rem", right: "1rem", padding: "8px" }}
            >
              Close ✕
            </button>
            
            <h2>{selectedFile.filename}</h2>
            <pre style={{ 
              background: "#111", 
              color: "#0f0", 
              padding: "12px",
              borderRadius: "4px",
              overflow: "auto",
              fontSize: "0.85rem"
            }}>
              {JSON.stringify(selectedFile.insights, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
