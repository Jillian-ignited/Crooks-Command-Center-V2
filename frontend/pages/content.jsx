import { useState } from "react";
import { apiPost } from "../lib/api";

export default function ContentPage() {
  const [brief, setBrief] = useState(null);
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function createBrief(e){
    e.preventDefault();
    setErr(""); setLoading(true); setBrief(null);
    const fd = new FormData(e.currentTarget);
    try {
      const res = await apiPost("/content/brief", {
        brand: fd.get("brand") || "Crooks & Castles",
        objective: fd.get("objective") || "Drive sell-through",
        audience: fd.get("audience") || "Gen Z streetwear",
        tone: fd.get("tone") || "authentic",
        channels: (fd.get("channels") || "IG, TikTok, Email").split(",").map(s=>s.trim())
      });
      setBrief(res.brief || res);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  }

  async function getIdeas(e){
    e.preventDefault();
    setErr(""); setLoading(true); setIdeas([]);
    const fd = new FormData(e.currentTarget);
    try {
      const res = await apiPost("/content/ideas", {
        brand: fd.get("brand") || "Crooks & Castles",
        theme: fd.get("theme") || "Armor + Cred",
        count: Number(fd.get("count") || 10)
      });
      setIdeas(res.ideas || []);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  }

  return (
    <main style={{maxWidth:900,margin:"40px auto",padding:"0 16px",fontFamily:"system-ui"}}>
      <h1>Content Creation</h1>

      <section style={{margin:"24px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Create Brief</h2>
        <form onSubmit={createBrief} style={{display:"grid",gap:8}}>
          <input name="brand" placeholder="Brand (e.g., Crooks & Castles)" />
          <input name="objective" placeholder="Objective (e.g., Drive sell-through)" />
          <input name="audience" placeholder="Audience (e.g., Gen Z streetwear)" />
          <input name="tone" placeholder="Tone (e.g., authentic)" />
          <input name="channels" placeholder="Channels CSV (IG, TikTok, Email)" />
          <button disabled={loading} type="submit">{loading?"Creating…":"Create Brief"}</button>
        </form>
        {err && <p style={{color:"crimson"}}>{err}</p>}
        {brief && (
          <pre style={{marginTop:12,whiteSpace:"pre-wrap",background:"#fafafa",padding:12,borderRadius:8}}>
            {JSON.stringify(brief,null,2)}
          </pre>
        )}
      </section>

      <section style={{margin:"24px 0",padding:16,border:"1px solid #eee",borderRadius:10}}>
        <h2>Generate Ideas</h2>
        <form onSubmit={getIdeas} style={{display:"grid",gap:8}}>
          <input name="brand" placeholder="Brand" />
          <input name="theme" placeholder="Theme (e.g., Armor + Cred)" />
          <input name="count" placeholder="Count (e.g., 10)" type="number" min="1" max="50" />
          <button disabled={loading} type="submit">{loading?"Generating…":"Generate"}</button>
        </form>
        {!!ideas.length && (
          <ol style={{marginTop:12}}>
            {ideas.map((x,i)=><li key={i}>{x}</li>)}
          </ol>
        )}
      </section>
    </main>
  );
}
