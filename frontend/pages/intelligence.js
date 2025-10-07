import { useState, useEffect } from "react";
import { api } from "../lib/api";

export default function Intelligence() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadFiles();
  }, []);

  async function loadFiles() {
    try {
      setLoading(true);
      const data = await api.getFiles();
      setFiles(data.files || []);
      setError("");
    } catch (err) {
      console.error('Failed to load files:', err);
      setError("Failed to load files: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function viewFile(fileId) {
    try {
      setLoading(true);
      const data = await api.getFileAnalysis(fileId);
      setSelectedFile(data);
      setError("");
    } catch (err) {
      console.error('Failed to load file:', err);
      setError("Failed to load file: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function formatAnalysis(analysisData) {
    if (!analysisData || typeof analysisData !== 'object') {
      return <p>No analysis available</p>;
    }

    if (analysisData.error) {
      return (
        <div style={{ padding: "1rem", background: "#2a1a1a", borderRadius: "4px", color: "#ff6b6b" }}>
          <strong>Error:</strong> {analysisData.error}
          <p style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>
            {analysisData.analysis || "AI analysis failed"}
          </p>
        </div>
      );
    }

    const analysisText = analysisData.analysis || "";
    
    // Split by numbered sections or headers
    const sections = analysisText.split(/\n(?=\d+\.|#{1,3}\s|\*\*)/);

    return (
      <div style={{ display: "grid", gap: "1.5rem" }}>
        <div style={{ background: "#1a2a1a", padding: "1rem", borderRadius: "4px" }}>
          <div style={{ fontSize: "0.85rem", color: "#888", marginBottom: "0.5rem" }}>
            📊 Analyzed {analysisData.sample_size || 0} samples from {analysisData.total_records || 0} total records
          </div>
          <div style={{ fontSize: "0.85rem", color: "#888" }}>
            🤖 Model: {analysisData.model || "gpt-3.5-turbo"}
          </div>
        </div>

        {sections.map((section, idx) => (
          <div key={idx} style={{ background: "#1a1a1a", padding: "1.5rem", borderRadius: "8px", lineHeight: "1.6" }}>
            <div style={{ whiteSpace: "pre-wrap" }}>{section.trim()}</div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: "100vh", 
      background: "#0a0b0d", 
      color: "#e9edf2",
      padding: "2rem"
    }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {/* Header */}
        <div style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center",
          marginBottom: "2rem" 
        }}>
          <div>
            <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
              Intelligence Files
            </h1>
            <p style={{ color: "#888" }}>
              Competitive intelligence and AI analysis
            </p>
          </div>
          <a 
            href="/upload" 
            style={{ 
              padding: "12px 24px", 
              background: "#6aa6ff", 
              color: "#fff",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: "600"
            }}
          >
            + Upload File
          </a>
        </div>

        {error && (
          <div style={{ 
            padding: "1rem", 
            background: "#2a1a1a", 
            borderRadius: "8px", 
            color: "#ff6b6b",
            marginBottom: "1rem"
          }}>
            {error}
          </div>
        )}

        {/* Files List */}
        {loading && files.length === 0 ? (
          <div style={{ textAlign: "center", padding: "3rem", color: "#888" }}>
            Loading files...
          </div>
        ) : files.length === 0 ? (
          <div style={{ 
            textAlign: "center", 
            padding: "3rem", 
            background: "#1a1a1a",
            borderRadius: "8px"
          }}>
            <p style={{ color: "#888", marginBottom: "1rem" }}>
              No files uploaded yet
            </p>
            <a href="/upload" style={{ color: "#6aa6ff" }}>
              Upload your first file →
            </a>
          </div>
        ) : (
          <div style={{ display: "grid", gap: "1rem" }}>
            {files.map(file => (
              <div 
                key={file.id}
                style={{ 
                  background: "#1a1a1a", 
                  padding: "1.5rem", 
                  borderRadius: "8px",
                  border: "1px solid #2a2a2a",
                  transition: "border-color 0.2s"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
                      📄 {file.filename}
                    </h3>
                    <div style={{ display: "flex", gap: "1rem", fontSize: "0.85rem", color: "#888" }}>
                      <span>📦 {file.source}</span>
                      <span>🏷️ {file.brand}</span>
                      <span>💾 {file.size_mb}MB</span>
                      <span>📅 {new Date(file.uploaded_at).toLocaleDateString()}</span>
                    </div>
                    <div style={{ marginTop: "0.5rem" }}>
                      {file.status === "processed" && file.has_analysis ? (
                        <span style={{ 
                          padding: "4px 12px", 
                          background: "#1a2a1a", 
                          color: "#4ade80",
                          borderRadius: "4px",
                          fontSize: "0.85rem",
                          fontWeight: "600"
                        }}>
                          ✅ Analyzed
                        </span>
                      ) : file.status === "processed" ? (
                        <span style={{ 
                          padding: "4px 12px", 
                          background: "#2a2a1a", 
                          color: "#fbbf24",
                          borderRadius: "4px",
                          fontSize: "0.85rem"
                        }}>
                          ⚠️ No Analysis
                        </span>
                      ) : (
                        <span style={{ 
                          padding: "4px 12px", 
                          background: "#1a1a2a", 
                          color: "#888",
                          borderRadius: "4px",
                          fontSize: "0.85rem"
                        }}>
                          ⏳ Uploaded
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {file.has_analysis && (
                    <button
                      onClick={() => viewFile(file.id)}
                      style={{ 
                        padding: "10px 20px", 
                        background: "#2a2a2a",
                        color: "#6aa6ff",
                        border: "1px solid #6aa6ff",
                        borderRadius: "6px",
                        cursor: "pointer",
                        fontWeight: "600",
                        transition: "all 0.2s"
                      }}
                      onMouseOver={(e) => e.target.style.background = "#6aa6ff"}
                      onMouseOut={(e) => e.target.style.background = "#2a2a2a"}
                    >
                      📊 View Analysis
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Analysis Modal */}
        {selectedFile && (
          <div style={{ 
            position: "fixed", 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            background: "rgba(0,0,0,0.9)", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center", 
            padding: "2rem", 
            zIndex: 1000,
            overflowY: "auto"
          }}>
            <div style={{ 
              background: "#0a0b0d", 
              padding: "2rem", 
              borderRadius: "12px", 
              maxWidth: "900px", 
              width: "100%",
              maxHeight: "90vh", 
              overflow: "auto",
              border: "1px solid #2a2a2a"
            }}>
              {/* Header */}
              <div style={{ 
                display: "flex", 
                justifyContent: "space-between", 
                alignItems: "flex-start",
                marginBottom: "2rem",
                paddingBottom: "1rem",
                borderBottom: "1px solid #2a2a2a"
              }}>
                <div>
                  <h2 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>
                    {selectedFile.filename}
                  </h2>
                  <div style={{ display: "flex", gap: "1rem", fontSize: "0.85rem", color: "#888" }}>
                    <span>📦 {selectedFile.source}</span>
                    <span>💾 {selectedFile.size_mb}MB</span>
                    <span>📅 {new Date(selectedFile.uploaded_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <button 
                  onClick={() => setSelectedFile(null)}
                  style={{ 
                    padding: "8px 16px", 
                    background: "#2a2a2a",
                    color: "#fff",
                    border: "none",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontWeight: "600"
                  }}
                >
                  ✕ Close
                </button>
              </div>

              {/* Analysis Content */}
              <div>
                {formatAnalysis(selectedFile.analysis)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
