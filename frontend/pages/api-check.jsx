import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function ApiCheck() {
  const [out, setOut] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet("/health");
        setOut(res);
      } catch (e) {
        setErr(e?.message || String(e));
      }
    })();
  }, []);

  return (
    <div style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <h1>API Health Check</h1>
      <p>Calls <code>{process.env.NEXT_PUBLIC_API_BASE}/health</code> on mount.</p>
      {out && <pre style={{ background: "#111", color: "#eee", padding: 12, borderRadius: 8 }}>{JSON.stringify(out, null, 2)}</pre>}
      {err && <pre style={{ background: "#2a0000", color: "#ffb3b3", padding: 12, borderRadius: 8 }}>{err}</pre>}
    </div>
  );
}
