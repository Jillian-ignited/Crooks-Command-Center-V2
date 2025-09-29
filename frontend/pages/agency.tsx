import { useEffect, useMemo, useState } from "react";

type Deliverable = {
  id: number;
  phase: string | null;
  task: string;
  owner: string | null;
  channel: string | null;
  assets: string | null;
  dependencies: string | null;
  notes: string | null;
  due_date: string | null;
  status: string;
  priority: number;
  last_updated: string | null;
};

type ApiListResp = {
  items: Deliverable[];
  phases: string[];
  stats: {
    total: number;
    overdue: number;
    statuses: string[];
    by_status: Record<string, number>;
  };
};

const STATUS_VALUES = [
  "Not Started","In Progress","Blocked","Waiting Approval","Approved","Done"
];

export default function AgencyPage() {
  const [data, setData] = useState<ApiListResp | null>(null);
  const [phase, setPhase] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [q, setQ] = useState<string>("");

  const load = async () => {
    const p = new URLSearchParams();
    if (phase) p.set("phase", phase);
    if (status) p.set("status", status);
    if (q) p.set("q", q);
    const res = await fetch(`/api/agency/deliverables?${p.toString()}`);
    if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
    const json = await res.json();
    setData(json);
  };

  useEffect(() => { load().catch(console.error); }, []); // initial
  useEffect(() => { load().catch(console.error); }, [phase, status]); // filters

  const items = useMemo(() => data?.items ?? [], [data]);

  const onSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    await load();
  };

  const updateField = async (id: number, patch: Partial<Deliverable>) => {
    const res = await fetch(`/api/agency/deliverables/${id}`, {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(patch)
    });
    if (!res.ok) {
      alert(`Update failed: ${res.status}`);
      return;
    }
    // Optimistic refresh
    await load();
  };

  const overdue = (d?: string | null) => {
    if (!d) return false;
    try {
      const today = new Date(); today.setHours(0,0,0,0);
      const dt = new Date(d); dt.setHours(0,0,0,0);
      return dt < today;
    } catch { return false; }
  };

  return (
    <div className="min-h-screen bg-[#0a0b0d] text-[#e9edf2] p-6">
      <h1 className="text-2xl font-semibold mb-4">Agency — Deliverables</h1>

      {/* Stats */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="bg-[#0f1217] rounded-2xl p-4">
            <div className="text-sm text-[#a1a8b3]">Total</div>
            <div className="text-xl">{data.stats.total}</div>
          </div>
          <div className="bg-[#0f1217] rounded-2xl p-4">
            <div className="text-sm text-[#a1a8b3]">Overdue</div>
            <div className="text-xl">{data.stats.overdue}</div>
          </div>
          <div className="bg-[#0f1217] rounded-2xl p-4">
            <div className="text-sm text-[#a1a8b3]">In Progress</div>
            <div className="text-xl">{data.stats.by_status["In Progress"] ?? 0}</div>
          </div>
          <div className="bg-[#0f1217] rounded-2xl p-4">
            <div className="text-sm text-[#a1a8b3]">Done</div>
            <div className="text-xl">{data.stats.by_status["Done"] ?? 0}</div>
          </div>
        </div>
      )}

      {/* Controls */}
      <form onSubmit={onSearch} className="flex flex-col md:flex-row gap-3 mb-4">
        <select className="bg-[#0f1217] rounded-xl px-3 py-2"
          value={phase} onChange={e => setPhase(e.target.value)}>
          <option value="">All Phases</option>
          {(data?.phases ?? []).map(p => <option key={p} value={p}>{p}</option>)}
        </select>

        <select className="bg-[#0f1217] rounded-xl px-3 py-2"
          value={status} onChange={e => setStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {STATUS_VALUES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        <input className="flex-1 bg-[#0f1217] rounded-xl px-3 py-2"
          placeholder="Search task/owner/channel/notes…" value={q} onChange={e => setQ(e.target.value)} />

        <button className="bg-[#6aa6ff] text-black font-medium rounded-xl px-4 py-2 hover:opacity-90" type="submit">
          Search
        </button>
      </form>

      {/* Table */}
      <div className="overflow-auto rounded-2xl border border-[#1c2230]">
        <table className="min-w-[960px] w-full">
          <thead className="bg-[#0f1217] text-[#a1a8b3]">
            <tr>
              <th className="text-left p-3">Phase</th>
              <th className="text-left p-3">Task</th>
              <th className="text-left p-3">Owner</th>
              <th className="text-left p-3">Channel</th>
              <th className="text-left p-3">Due</th>
              <th className="text-left p-3">Assets</th>
              <th className="text-left p-3">Status</th>
              <th className="text-left p-3">Priority</th>
            </tr>
          </thead>
          <tbody>
            {items.map(it => (
              <tr key={it.id} className="border-t border-[#1c2230] hover:bg-[#0f1217]">
                <td className="p-3">{it.phase || "—"}</td>
                <td className="p-3">
                  <div className="font-medium">{it.task}</div>
                  {it.notes ? <div className="text-xs text-[#a1a8b3] mt-1">{it.notes}</div> : null}
                  {it.dependencies ? <div className="text-xs text-[#a1a8b3] mt-1">Depends: {it.dependencies}</div> : null}
                </td>
                <td className="p-3">{it.owner || "—"}</td>
                <td className="p-3">{it.channel || "—"}</td>
                <td className={"p-3 " + (overdue(it.due_date) && it.status!=="Done" && it.status!=="Approved" ? "text-[#ff7a7a] font-semibold" : "")}>
                  {it.due_date || "—"}
                </td>
                <td className="p-3">
                  {it.assets ? <a className="underline" href={it.assets} target="_blank">assets</a> : "—"}
                </td>
                <td className="p-3">
                  <select
                    className="bg-[#0f1217] rounded-lg px-2 py-1"
                    value={it.status}
                    onChange={e => updateField(it.id, { status: e.target.value })}
                  >
                    {STATUS_VALUES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
                <td className="p-3">
                  <select
                    className="bg-[#0f1217] rounded-lg px-2 py-1"
                    value={it.priority}
                    onChange={e => updateField(it.id, { priority: Number(e.target.value) })}
                  >
                    {[1,2,3,4,5].map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td className="p-6 text-center text-[#a1a8b3]" colSpan={8}>No deliverables found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* CSV Import */}
      <CSVImport onImported={load} />
    </div>
  );
}

function CSVImport({ onImported }: { onImported: () => void }) {
  const [busy, setBusy] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const upload = async () => {
    if (!file) return;
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch("/api/agency/import?truncate=true", { method: "POST", body: fd });
      if (!res.ok) throw new Error(`Import failed: ${res.status}`);
      await onImported();
      alert("Import complete.");
    } catch (e: any) {
      alert(e?.message || "Import error");
    } finally {
      setBusy(false);
      setFile(null);
    }
  };
  return (
    <div className="mt-6 flex items-center gap-3">
      <input
        type="file"
        accept=".csv,text/csv"
        onChange={e => setFile(e.target.files?.[0] || null)}
        className="text-sm"
      />
      <button
        onClick={upload}
        disabled={!file || busy}
        className="bg-[#6aa6ff] text-black font-medium rounded-xl px-4 py-2 hover:opacity-90 disabled:opacity-50"
      >
        {busy ? "Importing…" : "Import CSV"}
      </button>
    </div>
  );
}
