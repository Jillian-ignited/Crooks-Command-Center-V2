import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../lib/api";

export default function IngestPage() {
  const [status, setStatus] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  // local job log (append on successful uploads)
  const [jobs, setJobs] = useState([]);

  async function loadStatus() {
    setErr("");
    try {
      const s = await apiGet("/ingest/status");
      setStatus(s);
    } catch (e) {
      setErr(`Status: ${e.message}`);
    }
  }

  useEffect(() => { loadStatus(); }, []);

  async function uploadFile(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    const form = e.currentTarget;
    const file = form.file.files[0];
    const source = form.source.value || "manual";
    const notes = form.notes.value || "";
    if (!file) { setErr("Choose a file."); setLoading(false); return; }

    const fd = new FormData();
    fd.append("file", file);
    fd.append("source", source);
    fd.append("notes", notes);

    try {
      const res = await apiPost("/ingest/upload", fd);
      setJobs((j) => [{ id: res.job_id, mode: res.mode || "multipart", filename: res.filename, size: res.size, ts: new Date().toISOString(), source: res.source || source }, ...j].slice(0, 20));
      form.reset();
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function uploadJSON(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    const form = e.currentTarget;
    const content = form.content.value || "";
    const source = form.source.value || "manual";
    const notes = form.notes.value || "";
    if (!content.trim()) { setErr("Enter JSON or text content."); setLoading(false); return; }

    try {
      const res = await apiPost("/ingest/upload", { content, source, notes });
      setJobs((j) => [{ id: res.job_id, mode: res.mode || "json", size: res.size, ts: new Date().toISOString(), source: source }, ...j].slice(0, 20));
      form.reset();
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 960, margin: "40px auto", padding: "0 16px", fontFamily: "system-ui" }}>
      <h1>Ingest (Enhanced)</h1>

      {err && <p style={{ color: "crimson" }}>{err}</p>}

      {/* Status */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Status</h2>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <span
            style={{
              display: "inline-block",
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: (status && status.ok !== false) ? "seagreen" : "darkorange"
            }}
          />
          <span style={{ fontSize: 14 }}>
            {(status && status.ok !== false) ? "OK" : "Unavailable"}
            {status?.queues ? ` · queues: ${Object.keys(status.queues).join(", ")}` : ""}
          </span>
          <button onClick={loadStatus} style={{ marginLeft: "auto", padding: "6px 10px", borderRadius: 8, border: "1px solid #ddd", background: "#fff" }}>
            Refresh
          </button>
        </div>
        <pre style={{ whiteSpace: "pre-wrap", background: "#fafafa", padding: 12, borderRadius: 8, marginTop: 12 }}>
          {JSON.stringify(status, null, 2)}
        </pre>
      </section>

      {/* File Upload */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Upload File</h2>
        <form onSubmit={uploadFile} style={{ display: "grid", gap: 8 }}>
          <input type="file" name="file" />
          <input name="source" placeholder="source (manual, scraper, ig, tiktok…)" />
          <input name="notes" placeholder="notes (optional)" />
          <button disabled={loading} type="submit">
            {loading ? "Uploading…" : "Upload"}
          </button>
        </form>
      </section>

      {/* JSON Upload */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Submit JSON/Text</h2>
        <form onSubmit={uploadJSON} style={{ display: "grid", gap: 8 }}>
          <textarea name="content" rows={5} placeholder='Paste JSON or plain text here'></textarea>
          <input name="source" placeholder="source (manual, scraper, ig, tiktok…)" />
          <input name="notes" placeholder="notes (optional)" />
          <button disabled={loading} type="submit">
            {loading ? "Submitting…" : "Submit"}
          </button>
        </form>
      </section>

      {/* Recent Jobs */}
      <section style={{ marginTop: 16, padding: 16, border: "1px solid #eee", borderRadius: 10 }}>
        <h2 style={{ marginTop: 0 }}>Recent Jobs</h2>
        {!jobs.length && <p style={{ opacity: 0.7 }}>No jobs yet.</p>}
        {!!jobs.length && (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
            {jobs.map((j) => (
              <li key={j.id} style={{ border: "1px solid #eee", borderRadius: 10, padding: 12 }}>
                <div style={{ fontWeight: 600 }}>{j.id}</div>
                <div style={{ fontSize: 13, opacity: 0.85 }}>
                  mode: {j.mode} {j.filename ? `· ${j.filename}` : ""} {j.size ? `· ${j.size} bytes` : ""} {j.source ? `· ${j.source}` : ""}
                </div>
                <div style={{ fontSize: 12, opacity: 0.75 }}>{new Date(j.ts).toLocaleString()}</div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
