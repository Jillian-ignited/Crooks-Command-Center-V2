(function(){
  const brandsEl = document.getElementById('brands');
  const daysEl = document.getElementById('days');
  const runSummaryBtn = document.getElementById('runSummary');
  const runIntelBtn = document.getElementById('runIntel');
  const summaryCard = document.getElementById('summaryCard');
  const summaryBody = document.getElementById('summaryBody');
  const intelCard = document.getElementById('intelCard');
  const intelBody = document.getElementById('intelBody');

  const parseBrands = () => brandsEl.value.split(',').map(s=>s.trim()).filter(Boolean);
  const lookback = () => Number(daysEl.value || 7);

  runSummaryBtn.onclick = async () => {
    const body = { brands: parseBrands(), lookback_days: lookback() };
    const data = await ccc.jsonFetch(`/summary`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    summaryCard.style.display = 'block';
    summaryBody.innerHTML = `
      <div class="muted">Last ${data.timeframe_days} days</div>
      <p>${data.narrative || ''}</p>
      <div style="margin-top:12px"><div class="muted">Key Moves</div><ul>${(data.key_moves||[]).map(m=>`<li>${m}</li>`).join('')}</ul></div>
      <div style="margin-top:12px"><div class="muted">Risks</div><ul>${(data.risks||[]).map(r=>`<li>${r}</li>`).join('')}</ul></div>
    `;
  };

  runIntelBtn.onclick = async () => {
    const body = { brands: parseBrands(), lookback_days: lookback() };
    const data = await ccc.jsonFetch(`/intelligence/report`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    intelCard.style.display = 'block';
    intelBody.innerHTML = renderIntel(data);
  };

  function renderIntel(data){
    if(!data || !data.metrics || !data.metrics.length) return '<div class="muted">No data. Upload files on the Intelligence page.</div>';
    let html = `<div class="muted">Timeframe: ${data.timeframe_days} days</div>`;
    for(const m of data.metrics){
      html += `
        <div class="card" style="margin-top:12px">
          <div class="row" style="justify-content:space-between">
            <strong>${m.brand}</strong><span class="pill">${m.posts} posts</span>
          </div>
          <div class="row" style="gap:16px; margin-top:8px">
            <span class="pill">Avg Likes: ${m.avg_likes}</span>
            <span class="pill">Avg Comments: ${m.avg_comments}</span>
            <span class="pill">Eng Score: ${m.engagement_rate}</span>
          </div>
          <div style="margin-top:10px">
            <div class="muted">Top Keywords</div>
            <div class="row" style="gap:8px; margin-top:6px; flex-wrap:wrap">
              ${(m.top_keywords||[]).map(k=>`<span class="pill">${k}</span>`).join('')}
            </div>
          </div>
          <div style="margin-top:10px">
            <div class="muted">Top Posts</div>
            <ul>
              ${(m.top_posts||[]).map(p=>`
                <li>[${p.platform}] ${String(p.date||'').slice(0,10)} — ❤️${p.likes} 💬${p.comments} — <a target="_blank" rel="noreferrer" href="${p.url}">link</a></li>
              `).join('')}
            </ul>
          </div>
        </div>`;
    }
    if(data.highlights?.length){
      html += `<div style="margin-top:12px"><div class="muted">Highlights</div><ul>${data.highlights.map(h=>`<li>${h}</li>`).join('')}</ul></div>`;
    }
    if(data.prioritized_actions?.length){
      html += `<div style="margin-top:12px"><div class="muted">Prioritized Actions</div><ul>${data.prioritized_actions.map(a=>`<li>${a}</li>`).join('')}</ul></div>`;
    }
    return html;
  }
})();
