// Update the handleUpload function:
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
    
    // Check if response is JSON
    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await res.text();
      throw new Error(`Server returned non-JSON response: ${text.substring(0, 200)}`);
    }
    
    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`);
    }
    
    setUploadResult(data);
    setStatus("✅ " + data.message);
    
    // Reload data after delay
    setTimeout(() => {
      loadSummary();
      loadFiles();
    }, 3000);
    
  } catch (err) {
    console.error('Upload error:', err);
    setStatus(`❌ Error: ${err.message}`);
  }
}
