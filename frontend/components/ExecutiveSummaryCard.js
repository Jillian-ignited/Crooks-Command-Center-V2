export default function ExecutiveSummaryCard({ report }) {
  if (!report) return null;
  return (
    <div className="card">
      <h3 className="title">Executive Summary (Last {report.timeframe_days} days)</h3>
      <p>{report.narrative}</p>
      <div style={{marginTop:12}}>
        <div className="muted">Key Moves</div>
        <ul>
          {report.key_moves?.map((m, i) => <li key={i}>{m}</li>)}
        </ul>
      </div>
      <div style={{marginTop:12}}>
        <div className="muted">Risks</div>
        <ul>
          {report.risks?.map((r, i) => <li key={i}>{r}</li>)}
        </ul>
      </div>
    </div>
  );
}
