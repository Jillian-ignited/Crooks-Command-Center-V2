import { useState } from "react";
import { apiPost } from "../lib/api";

export default function UploadPage(){
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function uploadToIntelligence(e){
    e.preventDefault();
    setErr(""); setMsg(""); setLoading(true);
    const f = e.currentTarget.file.files[0];
    const kind = e.currentTarget.kind.value || "exec";
    if(!f){ setErr("Choose a file"); setLoading(false); return; }
    const fd = new FormData();
    fd.append("file", f); fd.append("kind", kind);
    try {
      const res = await apiPost("/intelligence/upload", fd);
      setMsg(`Uploaded to intelligence: ${res.filename} (${res.size} bytes)`);
      e.currentTarget.reset();
    } catch (e){ setErr(e.message); } finally { setLoading(false); }
  }

  async function uploadToIngest(e){
    e.preventDefault();
    setErr(""); setMsg(""); setLoading(true);
    const f = e.currentTarget.file.files[0];
    const source = e.currentTarget.source.value || "manual";
    const notes = e.currentTarget.notes.value || "";
    if(!f){ setErr("Choose a file"); setLoading(false); return; }
    const fd = new FormData();
    fd.append("file", f); fd.append("source", source); fd.append("notes", notes);
    try {
      const res = await apiPost("/ingest/upload", fd);
      setMsg(`Ingest job ${res.job_id} created from ${res.filename} (${res.size} bytes)`);
      e.currentTarget.reset();
    } catch (e){ setErr(e.message); } finally { setLoading(false); }
  }

  async function jsonUpload(e){
    e.preventDefault();
    setErr(""); setMsg(""); setLoading(true);
    const content = e.currentTarget.content.value || "";
    const kind = e.currentTarget.kind.value || "notes";
    try {
      const res = await apiPost("/intelligence/upload", { content, filename: "payload.txt", kind });
      setMsg(`Uploaded JSON payload (${res.size} bytes)`);
      e.currentTarget.reset();
    } catch (e){ setErr(e.message); } finally { setLoading(false); }
  }

  return (
    <main style={{maxWidth:900,margin:"40px auto",padding:"0 16px",fontFamily:"system-ui"}}>
      <h1>Upload Center</h1>

      <section style={{margin:"16px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Upload to Intelligence</h2>
        <form onSubmit={uploadToIntelligence} style={{display:"grid",gap:8}}>
          <input type="file" name="file" />
          <input name="kind" placeholder="kind (exec, media, etc.)" />
          <button disabled={loading} type="submit">{loading?"Uploading…":"Upload"}</button>
        </form>
      </section>

      <section style={{margin:"16px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Upload to Ingest (enhanced)</h2>
        <form onSubmit={uploadToIngest} style={{display:"grid",gap:8}}>
          <input type="file" name="file" />
          <input name="source" placeholder="source (manual, scraper, ig, tiktok…)" />
          <input name="notes" placeholder="notes (optional)" />
          <button disabled={loading} type="submit">{loading?"Uploading…":"Upload"}</button>
        </form>
      </section>

      <section style={{margin:"16px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Upload JSON Payload</h2>
        <form onSubmit={jsonUpload} style={{display:"grid",gap:8}}>
          <textarea name="content" rows={4} placeholder='{"hello":"world"} or plain text'></textarea>
          <input name="kind" placeholder="kind (notes, config…)" />
          <button disabled={loading} type="submit">{loading?"Submitting…":"Submit JSON"}</button>
        </form>
      </section>

      {err && <p style={{color:"crimson"}}>{err}</p>}
      {msg && <p style={{color:"seagreen"}}>{msg}</p>}
    </main>
  );
}
