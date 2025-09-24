export default function CalendarView({ data }) {
  if (!data) return null;
  return (
    <div className="card">
      <h3 className="title">Cultural Calendar (Next {data.range_days} days)</h3>
      {data.events?.length ? (
        <ul>
          {data.events.map((e, i) => (
            <li key={i}>
              <strong>{e.date}</strong> — {e.title} <span className="pill">{e.category}</span>
            </li>
          ))}
        </ul>
      ) : <div className="muted">No events in range.</div>}
    </div>
  );
}
