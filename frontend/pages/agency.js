import { useEffect, useState } from "react";
import AgencyDeliverables from "../components/AgencyDeliverables";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function AgencyPage() {
  const [data, setData] = useState(null);
  useEffect(()=>{
    (async ()=>{
      const res = await fetch(`${API}/agency`);
      setData(await res.json());
    })();
  }, []);
  return (
    <div className="grid">
      <AgencyDeliverables data={data} />
    </div>
  );
}
