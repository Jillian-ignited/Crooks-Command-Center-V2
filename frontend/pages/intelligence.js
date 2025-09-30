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
  const [loading, setLoading] = useState(false);

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
    if (!file) {
      setStatus("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("source", source);
    formData.append("brand", brand);

    try {
      setLoading(true);
      setStatus("Uploading and processing with AI...");
      
      const res = await fetch('/api/intelligence/upload', {
        method: "POST",
        body: formData,
      });
      
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(`Server error: ${text.substring(0, 200)}`);
      }
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || `Upload failed: ${res.status}`);
      }
      
      setUploadResult(data);
      setStatus(`✅ ${data.message}`);
      
      setTimeout(() => {
        loadSummary();
        loadFiles();
      }, 3000);
      
    } catch (err) {
      console.error('Upload error:', err);
      setStatus(`❌ Error: ${err.message}`);
    } finally {
      setLoading(false);
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
            <select 
              value={source} 
              onChange={(e) => setSource(e.target.value)} 
              style={{ marginLeft: 8, padding: 4, width: "100%" }}
            >
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
              style={{ marginLeft: 8, padding: 4, width: "100%" }}
            />
          </label>
          
          <label>
            File (.csv, .json, .jsonl, .xlsx)
            <input 
              type="file" 
              onChange={(e) => setFile(e.target.files?.[0] || null)} 
              accept=".csv,.json,.jsonl,.xlsx,.xls"
              style={{ marginTop: 8, width: "100%" }}
            />
          </label>
          
          <button 
            type="submit" 
            disabled={loading || !file}
            style={{ 
              padding: "10px 16px", 
              cursor: loading || !file ? "not-allowed" : "pointer",
              opacity: loading || !file ? 0.6 : 1
            }}
          >
            {loading ? "Processing..." : "Upload & Analyze"}
          </button>
        </form>
        
        {status && (
          <p style={{ 
            marginTop: 12, 
            fontWeight: "bold",
            color: status.includes("✅") ? "#4ade80" : status.includes("❌") ? "#f87171" : "#fff"
          }}>
            {status}
          </p>
        )}
      </div>

      {/* AI Insights Summary */}
      {summary?.insights && Object.keys(summary.insights).length > 0 && (
        <div style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", marginBottom: "2rem" }}>
          <h2>Latest AI Insights</h2>
          <p style={{ color: "#888", fontSize: "0.9rem", marginBottom: "1rem" }}>
            Last updated: {summary.last_updated ? new Date(summary.last_updated).toLocaleString() : 'N/A'}
          </p>
          
          {summary.insigh
