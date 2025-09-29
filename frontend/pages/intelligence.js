// frontend/pages/intelligence.js
import { useState } from "react";

export default function Intelligence() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading...");
      const res = await fetch("/api/intelligence/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();
      setResult(data);
      setStatus("Upload successful ✅");
    } catch (err) {
      console.error(err);
      setStatus("Error during upload ❌");
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Intelligence Upload</h1>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button type="submit">Upload</button>
      </form>
      <p>{status}</p>
      {result && (
        <pre
          style={{
            marginTop: "1rem",
            padding: "1rem",
            background: "#111",
            color: "#0f0",
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
