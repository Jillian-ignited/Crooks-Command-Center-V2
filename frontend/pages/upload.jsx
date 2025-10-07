import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [source, setSource] = useState("apify");
  const [brand, setBrand] = useState("Crooks & Castles");
  const [description, setDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleUpload(e) {
    e.preventDefault();
    
    if (!file) {
      setError("Please select a file");
      return;
    }

    try {
      setUploading(true);
      setError("");
      setProgress("Uploading file...");
      setResult(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('source', source);
      formData.append('brand', brand);
      if (description) formData.append('description', description);

      const response = await fetch(`${API_BASE_URL}/intelligence/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      setProgress("Upload complete!");
      setResult(data);
      
      setFile(null);
      setDescription("");
      e.target.reset();
      
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || "Upload failed");
      setProgress("");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0b0d", color: "#e9edf2", padding: "2rem" }}>
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>Upload Intelligence File</h1>
          <p style={{ color: "#888" }}>Upload Apify scrapes, Shopify data, or Manus reports for AI analysis</p>
        </div>

        <form onSubmit={handleUpload} style={{ background: "#1a1a1a", padding: "2rem", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", fontSize: "0.95rem" }}>File *</label>
            <input
              type="file"
              accept=".jsonl,.json,.csv,.txt,.xlsx,.xls"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", cursor: "pointer" }}
              required
            />
            <p style={{ fontSize: "0.85rem", color: "#888", marginTop: "0.5rem" }}>Accepted: .jsonl, .json, .csv, .txt, .xlsx, .xls (max 100MB)</p>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", fontSize: "0.95rem" }}>Source *</label>
            <select value={source} onChange={(e) => setSource(e.target.value)} style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2" }} required>
              <option value="apify">Apify (Social Media Scrape)</option>
              <option value="shopify">Shopify (Sales Data)</option>
              <option value="manus">Manus (Weekly Report)</option>
              <option value="manual_upload">Manual Upload</option>
            </select>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", fontSize: "0.95rem" }}>Brand *</label>
            <input type="text" value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Crooks & Castles" style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2" }} required />
          </div>

          <div style={{ marginBottom: "2rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", fontSize: "0.95rem" }}>Description (optional)</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="E.g., Instagram hashtag scrape for #streetwear Sept 2025" rows={3} style={{ width: "100%", padding: "12px", background: "#0a0b0d", border: "1px solid #2a2a2a", borderRadius: "6px", color: "#e9edf2", fontFamily: "inherit", resize: "vertical" }} />
          </div>

          <button type="submit" disabled={uploading || !file} style={{ width: "100%", padding: "14px", background: uploading || !file ? "#2a2a2a" : "#6aa6ff", color: "#fff", border: "none", borderRadius: "6px", fontSize: "1rem", fontWeight: "600", cursor: uploading || !file ? "not-allowed" : "pointer", opacity: uploading || !file ? 0.6 : 1 }}>
            {uploading ? "⏳ Uploading and Analyzing..." : "📤 Upload File"}
          </button>
        </form>

        {progress && (
          <div style={{ marginTop: "1rem", padding: "1rem", background: "#1a2a1a", borderRadius: "8px", color: "#4ade80" }}>
            {progress}
          </div>
        )}

        {error && (
          <div style={{ marginTop: "1rem", padding: "1rem", background: "#2a1a1a", borderRadius: "8px", color: "#ff6b6b" }}>
            ❌ {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: "1.5rem", padding: "1.5rem", background: "#1a1a1a", borderRadius: "12px", border: "1px solid #2a2a2a" }}>
            <h3 style={{ fontSize: "1.2rem", marginBottom: "1rem", color: "#4ade80" }}>✅ Upload Successful!</h3>
            <div style={{ display: "grid", gap: "0.5rem", fontSize: "0.95rem" }}>
              <div><strong>File:</strong> {result.filename}</div>
              <div><strong>Size:</strong> {result.size_mb} MB</div>
              <div><strong>Source:</strong> {result.source}</div>
              <div><strong>Status:</strong> {result.status}</div>
              {result.ai_analysis_complete && (
                <div style={{ color: "#4ade80", marginTop: "0.5rem" }}>🤖 AI Analysis Complete!</div>
              )}
            </div>
            <a href="/intelligence" style={{ display: "inline-block", marginTop: "1rem", padding: "10px 20px", background: "#6aa6ff", color: "#fff", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
              View in Intelligence
            </a>
          </div>
        )}

        <div style={{ marginTop: "2rem", padding: "1.5rem", background: "#1a1a1a", borderRadius: "8px", border: "1px solid #2a2a2a" }}>
          <h4 style={{ marginBottom: "1rem" }}>ℹ️ What happens after upload?</h4>
          <ul style={{ paddingLeft: "1.5rem", color: "#888", lineHeight: "1.8" }}>
            <li>File is uploaded securely to your command center</li>
            <li>AI analyzes the data for streetwear insights (30-60 seconds)</li>
            <li>You get actionable recommendations for Crooks & Castles</li>
            <li>Data is stored for future reference and trend analysis</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
