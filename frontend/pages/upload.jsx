import { useState } from "react";
import { apiPost } from "../lib/api";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [resp, setResp] = useState(null);

  const onSubmit = async (e) => {
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
    } catch (err) {
      setStatus(err?.message || "Upload failed");
    }
  };

  return (
    <div style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <h1>Upload Intelligence Data</h1>
      <form onSubmit={onSubmit}>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button type="submit">Upload</button>
      </form>
      <p>{status}</p>
      {resp && <pre>{JSON.stringify(resp, null, 2)}</pre>}
    </div>
  );
}
