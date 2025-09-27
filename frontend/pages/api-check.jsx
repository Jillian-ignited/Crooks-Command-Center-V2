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
      {out && <pre>{JSON.stringify(out, null, 2)}</pre>}
      {err && <pre style={{ color: "red" }}>{err}</pre>}
    </div>
  );
}
