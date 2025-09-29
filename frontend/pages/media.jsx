import { useEffect, useState } from "react";
import { apiGet, apiPost, apiDel } from "../lib/api";

export default function MediaPage() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function refresh() {
    setErr("");
    try {
      const data = await apiGet("/media/assets");
      setAssets(Array.isArray(data) ? data : data.assets || []);
    } catch (e) { setErr(e.message); }
  }
  useEffect(()=>{ refresh(); },[]);

  async function upload(e){
    e.preventDefault();
    setErr(""); setLoading(true);
    const file = e.currentTarget.file.files[0];
    const kind = e.currentTarget.kind.value || "unknown";
    if(!file){ setErr("Choose a file."); setLoading(false); return; }
    const fd = new FormData();
    fd.append("file", file);
    fd.append("kind", kind);
    try {
      await apiPost("/media/assets", fd);
      e.currentTarget.reset();
      await refresh();
    } catch(e){ setErr(e.message); }
    finally{ setLoading(false); }
  }

  async function remove(id){
    setErr("");
    try { await apiDel(`/media/assets/${id}`); await refresh(); }
    catch(e){ setErr(e.message); }
  }

  return (
    <main style={{maxWidth:900,margin:"40px auto",padding:"0 16px",fontFamily:"system-ui"}}>
      <h1>Asset Library</h1>

      <section style={{margin:"16px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Upload</h2>
        <form onSubmit={upload} style={{display:"grid",gap:8}}>
          <input type="file" name="file" />
          <input name="kind" placeholder="kind (image, video, doc…)" />
          <button disabled={loading} type="submit">{loading?"Uploading…":"Upload"}</button>
        </form>
        {err && <p style={{color:"crimson"}}>{err}</p>}
      </section>

      <section style={{margin:"16px 0"}}>
        <h2>Assets</h2>
        {!assets.length && <p style={{opacity:.7}}>No assets yet.</p>}
        <ul style={{listStyle:"none",padding:0,display:"grid",gap:8}}>
          {assets.map(a=>(
            <li key={a.id} style={{border:"1px solid #eee",borderRadius:10,padding:10,display:"flex",justifyContent:"space-between",alignItems:"center"}}>
              <div>
                <strong>{a.name}</strong>
                <div style={{opacity:.7,fontSize:12}}>
                  {a.mime} · {a.size} bytes · kind: {a.kind}
                </div>
              </div>
              <button onClick={()=>remove(a.id)} style={{background:"#fff",border:"1px solid #ddd",borderRadius:8,padding:"6px 10px"}}>Delete</button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
