import React, { useState } from "react";
import { apiPost } from "../lib/api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");
  const [resp, setResp] = useState<any>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return setStatus("Choose a file first.");
    setStatus("Uploading...");
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("kind", "intelligence_csv");
      const json = await apiPost("/intelligence/upload", fd);
      setResp(json);
      setStatus("Done.");
    } catch (err: any) {
      setStatus(err?.message || "Upload failed");
    }
  };

  return (
    <div style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <h1>Upload Intelligence Data</h1>
      <form onSubmit={onSubmit}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          style={{ display: "block", margin: "12px 0" }}
        />
        <button type="submit">Upload</button>
      </form>
      <p>{status}</p>
      {resp && (
        <pre style={{ background: "#111", color: "#eee", padding: 12, borderRadius: 8 }}>
          {JSON.stringify(resp, null, 2)}
        </pre>
      )}
    </div>
  );
}
