export default function IntelligencePanel({ data }) {
  if (!data) return null;
  return (
    <div className="card">
      <h3 className="title">Brand Intelligence</h3>
      <div className="muted">Timeframe: {data.timeframe_days} days</div>
      <div style={{marginTop:12}} className="grid" style={{display:'grid', gridTemplateColumns:'1fr', gap:12}}>
        {data.metrics?.map((m, idx) => (
          <div key={idx} className="card">
            <div className="row" style={{justifyContent:'space-between'}}>
              <strong>{m.brand}</strong>
              <span className="pill">{m.posts} posts</span>
            </div>
            <div className="row" style={{gap:16, marginTop:8}}>
              <span className="pill">Avg Likes: {m.avg_likes}</span>
              <span className="pill">Avg Comments: {m.avg_comments}</span>
              <span className="pill">Eng Score: {m.engagement_rate}</span>
            </div>
            <div style={{marginTop:10}}>
              <div className="muted">Top Keywords</div>
              <div className="row" style={{gap:8, marginTop:6, flexWrap:'wrap'}}>
                {m.top_keywords?.map((k, i) => <span key={i} className="pill">{k}</span>)}
              </div>
            </div>
            <div style={{marginTop:10}}>
              <div className="muted">Top Posts</div>
              <ul>
                {m.top_posts?.map((p, i) => (
                  <li key={i}>
                    [{p.platform}] {p.date?.slice(0,10)} — ❤️{p.likes} 💬{p.comments} — <a href={p.url} target="_blank" rel="noreferrer">link</a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
      <div style={{marginTop:12}}>
        <div className="muted">Highlights</div>
        <ul>{data.highlights?.map((h,i)=>(<li key={i}>{h}</li>))}</ul>
      </div>
      <div style={{marginTop:12}}>
        <div className="muted">Prioritized Actions</div>
        <ul>{data.prioritized_actions?.map((a,i)=>(<li key={i}>{a}</li>))}</ul>
      </div>
    </div>
  );
}
