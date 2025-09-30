// frontend/pages/executive.js
import { useEffect, useState } from "react";

export default function Executive() {
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);

  async function load() {
    setBusy(true); setErr(null);
    try {
      const res = await fetch("/api/executive/overview");
      const json = await res.json();
      if (!res.ok || json.ok === false) throw new Error("Failed to load overview");
      setData(json);
    } catch (e) {
      setErr(e?.message || "Error");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="min-h-screen bg-[#0a0b0d] text-[#e9edf2] p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Executive Overview</h1>
        <button
          onClick={load}
          className="bg-[#6aa6ff] text-black font-medium rounded-xl px-4 py-2 hover:opacity-90"
        >
          {busy ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {err && (
        <div className="bg-[#140e0e] border border-[#3a1f1f] text-[#ff7a7a] rounded-xl p-4 mb-4">
          {err}
        </div>
      )}

      {!data ? (
        <div className="bg-[#0f1217] rounded-xl p-6 border border-[#1c2230]">Loading…</div>
      ) : (
        <>
          {/* Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
            <Card title="Brands" value={data.cards?.brands ?? 0} />
            <Card title="Competitors" value={data.cards?.competitors ?? 0} />
            <Card title="Benchmarks" value={data.cards?.benchmarks ?? 0} />
          </div>

          {/* Brands & Competitors */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <ListBox title="Brands" items={(data.brands ?? []).map(b => b.name)} />
            <ListBox title="Competitors" items={(data.competitors ?? []).map(c => c.name)} />
          </div>

          {/* Benchmarks table */}
          <div className="rounded-2xl border border-[#1c2230] overflow-auto">
            <table className="min-w-[640px] w-full">
              <thead className="bg-[#0f1217] text-[#a1a8b3]">
                <tr>
                  <th className="text-left p-3">Metric</th>
                  <th className="text-left p-3">Subject</th>
                  <th className="text-left p-3">Value</th>
                  <th className="text-left p-3">As Of</th>
                </tr>
              </thead>
              <tbody>
                {(data.benchmarks ?? []).map((r, i) => (
                  <tr key={i} className="border-t border-[#1c2230]">
                    <td className="p-3">{r.metric}</td>
                    <td className="p-3">{r.subject}</td>
                    <td className="p-3">{r.value}</td>
                    <td className="p-3">{r.as_of}</td>
                  </tr>
                ))}
                {(data.benchmarks ?? []).length === 0 && (
                  <tr><td className="p-4 text-[#a1a8b3]" colSpan={4}>No benchmarks yet. Import a CSV via /intelligence.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function Card({ title, value }) {
  return (
    <div className="bg-[#0f1217] rounded-2xl p-5">
      <div className="text-sm text-[#a1a8b3]">{title}</div>
      <div className="text-2xl">{value}</div>
    </div>
  );
}

function ListBox({ title, items }) {
  return (
    <div className="bg-[#0f1217] rounded-2xl p-5 border border-[#1c2230]">
      <div className="text-sm text-[#a1a8b3] mb-2">{title}</div>
      <ul className="space-y-1">
        {items.map((t, i) => <li key={i}>{t}</li>)}
        {items.length === 0 && <li className="text-[#a1a8b3]">None</li>}
      </ul>
    </div>
  );
}
