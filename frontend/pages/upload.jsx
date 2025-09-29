import { useState } from "react";
import { apiPost } from "../lib/api";

export default function UploadPage(){
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function uploadToIntelligence(e){
    e.preventDefault();
    const form = e.currentTarget; // capture before any await
    setErr(""); setMsg(""); setLoading(true);
    try {
      const file = form.file?.files?.[0];
      const kind = form.kind?.value || "exec";
      if(!file){ throw new Error("Choose a file"); }
      const fd = new FormData();
      fd.append("file", file);
      fd.append("kind", kind);

      const res = await apiPost("/intelligence/upload", fd);
      setMsg(`Uploaded to intelligence: ${res.filename} (${res.size} bytes)`);
      form.reset?.(); // safe call even if null/undefined
    } catch (e){
      setErr(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  async function uploadToIngest(e){
    e.preventDefault();
    const form = e.currentTarget; // capture before await
    setErr(""); setMsg(""); setLoading(true);
    try {
      const file = form.file?.files?.[0];
      const source = form.source?.value || "manual";
      const notes = form.notes?.value || "";
      if(!file){ throw new Error("Choose a file"); }

      const fd = new FormData();
      fd.append("file", file);
      fd.append("source", source);
      fd.append("notes", notes);

      const res = await apiPost("/ingest/upload", fd);
      setMsg(`Ingest job ${res.job_id} created from ${res.filename} (${res.size} bytes)`);
      form.reset?.();
    } catch (e){
      setErr(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  async function jsonUpload(e){
    e.preventDefault();
    const form = e.currentTarget; // capture before await
    setErr(""); setMsg(""); setLoading(true);
    try {
      const content = form.content?.value || "";
      const kind = form.kind?.value || "notes";
      if(!content.trim()){ throw new Error("Enter JSON or text"); }

      const res = await apiPost("/intelligence/upload", { content, filename: "payload.txt", kind });
      setMsg(`Uploaded JSON payload (${res.size} bytes)`);
      form.reset?.();
    } catch (e){
      setErr(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{maxWidth:900,margin:"40px auto",padding:"0 16px",fontFamily:"system-ui"}}>
      <h1>Upload Center</h1>

      {err && <p style={{color:"crimson"}}>{err}</p>}
      {msg && <p style={{color:"seagreen"}}>{msg}</p>}

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
    </main>
  );
}
