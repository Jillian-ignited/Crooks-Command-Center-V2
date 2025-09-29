import { useEffect, useState } from "react";
import { apiGet, apiPut } from "../lib/api";

export default function AgencyPage() {
  const [dash, setDash] = useState(null);
  const [err, setErr] = useState("");
  const [deliverableId, setDeliverableId] = useState("");
  const [deliverableStatus, setDeliverableStatus] = useState("in_progress");
  const [quality, setQuality] = useState("");
  const [projectId, setProjectId] = useState("");
  const [completion, setCompletion] = useState(0);
  const [projectStatus, setProjectStatus] = useState("active");
  const [msg, setMsg] = useState("");

  async function load() {
    setErr(""); setMsg("");
    try {
      const res = await apiGet("/agency/dashboard");
      setDash(res);
    } catch (e) {
      setErr(e.message);
      setDash(null);
    }
  }

  useEffect(() => { load(); }, []);

  async function updateDeliverable(e) {
    e.preventDefault(); setErr(""); setMsg("");
    if (!deliverableId) { setErr("Deliverable ID required"); return; }
    try {
      const res = await apiPut(`/agency/deliverables/${deliverableId}/status`, {
        body: { status: deliverableStatus, quality_score: quality ? Number(quality) : null }
      });
      setMsg(`Deliverable ${res.deliverable_id} → ${res.new_status}`);
      await load();
    } catch (e) { setErr(e.message); }
  }

  async function updateProject(e) {
    e.preventDefault(); setErr(""); setMsg("");
    if (!projectId) { setErr("Project ID required"); return; }
    try {
      const res = await apiPut(`/agency/projects/${projectId}/progress`, {
        body: { completion_percentage: Number(completion), status: projectStatus }
      });
      setMsg(`Project ${res.project_id} → ${res.status} (${res.completion_percentage}%)`);
      await load();
    } catch (e) { setErr(e.message); }
  }

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: "0 16px", fontFamily: "system-ui" }}>
      <h1>Agency</h1>
      {err && <p style={{ color: "crimson" }}>{err}</p>}
      {msg && <p style={{ color: "seagreen" }}>{msg}</p>}

      <section style={{ margin:"16px 0", padding:16, border:"1px solid #eee", borderRadius:10 }}>
        <h2>Dashboard</h2>
        <pre style={{ whiteSpace: "pre-wrap", background: "#fafafa", padding: 12, borderRadius: 8 }}>
          {JSON.stringify(dash, null, 2)}
        </pre>
        <button onClick={load}>Refresh</button>
      </section>

      <section style={{ margin:"16px 0", padding:16, border:"1px solid #eee", borderRadius:10 }}>
        <h2>Update Deliverable</h2>
        <form onSubmit={updateDeliverable} style={{ display:"grid", gap:8 }}>
          <input placeholder="Deliverable ID" value={deliverableId} onChange={e=>setDeliverableId(e.target.value)}/>
          <input placeholder="Status (e.g., in_progress, complete)" value={deliverableStatus} onChange={e=>setDeliverableStatus(e.target.value)}/>
          <input placeholder="Quality Score (optional)" value={quality} onChange={e=>setQuality(e.target.value)} />
          <button type="submit">Update</button>
        </form>
      </section>

      <section style={{ margin:"16px 0", padding:16, border:"1px solid #eee", borderRadius:10 }}>
        <h2>Update Project</h2>
        <form onSubmit={updateProject} style={{ display:"grid", gap:8 }}>
          <input placeholder="Project ID" value={projectId} onChange={e=>setProjectId(e.target.value)}/>
          <input type="number" min="0" max="100" placeholder="Completion %" value={completion} onChange={e=>setCompletion(e.target.value)} />
          <input placeholder="Status (e.g., active, paused, complete)" value={projectStatus} onChange={e=>setProjectStatus(e.target.value)} />
          <button type="submit">Update</button>
        </form>
      </section>
    </main>
  );
}
