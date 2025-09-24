export default function AgencyDeliverables({ data }) {
  if (!data) return null;
  return (
    <div className="card">
      <h3 className="title">Agency — Week of {data.week_of}</h3>
      <ul>
        {data.deliverables?.map((d, i) => (
          <li key={i}>
            <strong>{d.title}</strong> — <span className="pill">{d.status}</span>
            {d.owner ? <> · <span className="muted">{d.owner}</span></> : null}
            {d.due ? <> · due {d.due}</> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
