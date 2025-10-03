import { useEffect, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : process.env.NEXT_PUBLIC_API_BASE || "";

export default function Media() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadAssets = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/media/assets`);
      if (res.ok) {
        const data = await res.json();
        setAssets(data.assets || []);
      }
    } catch (err) {
      console.error("Failed to load assets:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/api/media/upload`, {
        method: "POST",
        body: formData
      });

      if (response.ok) {
        await loadAssets();
      }
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    loadAssets();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h1>Asset Library</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1>Street Culture Asset Library</h1>
        <button onClick={loadAssets} style={{ padding: "8px 16px", cursor: "pointer" }}>
          Refresh
        </button>
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h2>Upload New Asset</h2>
        <div style={{ border: "2px dashed #ccc", padding: "2rem", textAlign: "center" }}>
          <input
            type="file"
            onChange={handleFileUpload}
            accept="image/*,video/*"
            disabled={uploading}
          />
          {uploading && <p>Uploading...</p>}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "1rem" }}>
        {assets.length === 0 ? (
          <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "2rem", color: "#6b7280" }}>
            No assets uploaded yet. Upload your first street culture asset above.
          </div>
        ) : (
          assets.map((asset, i) => (
            <AssetCard key={i} asset={asset} />
          ))
        )}
      </div>
    </div>
  );
}

function AssetCard({ asset }) {
  return (
    <div style={{
      background: "white",
      border: "1px solid #e5e7eb",
      borderRadius: "8px",
      padding: "1rem"
    }}>
      <div style={{ marginBottom: "1rem" }}>
        {asset.type === "image" ? (
          <img 
            src={asset.url} 
            alt={asset.name}
            style={{ width: "100%", height: "150px", objectFit: "cover", borderRadius: "4px" }}
          />
        ) : (
          <div style={{ 
            width: "100%", 
            height: "150px", 
            background: "#f3f4f6", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center",
            borderRadius: "4px"
          }}>
            📁 {asset.name}
          </div>
        )}
      </div>
      
      <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1rem" }}>{asset.name}</h3>
      
      <div style={{ fontSize: "0.875rem", color: "#6b7280", marginBottom: "0.5rem" }}>
        <div>Category: {asset.category}</div>
        <div>Compliance: {asset.compliance_score}/100</div>
      </div>
      
      <a 
        href={asset.url} 
        target="_blank" 
        rel="noopener noreferrer"
        style={{
          display: "inline-block",
          background: "#3b82f6",
          color: "white",
          padding: "0.5rem 1rem",
          borderRadius: "4px",
          textDecoration: "none",
          fontSize: "0.875rem"
        }}
      >
        View Asset
      </a>
    </div>
  );
}
