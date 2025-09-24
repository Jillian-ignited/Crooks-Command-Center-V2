(function(){
  const dz = document.getElementById('dz');
  const input = document.getElementById('fileInput');
  const list = document.getElementById('fileList');
  const runBtn = document.getElementById('runBtn');
  const brandsEl = document.getElementById('brands');
  const daysEl = document.getElementById('days');
  const intelCard = document.getElementById('intelCard');
  const intelBody = document.getElementById('intelBody');

  const parseBrands = () => brandsEl.value.split(',').map(s=>s.trim()).filter(Boolean);
  const lookback = () => Number(daysEl.value || 7);

  async function refresh(){
    const data = await ccc.jsonFetch('/intelligence/uploads');
    const files = data.files || [];
    if(!files.length){ list.innerHTML = '<li class="muted">No files yet.</li>'; return; }
    list.innerHTML = files.map(f => `
      <li class="row" style="justify-content:space-between">
        <span>${f}</span>
        <button class="button" data-del="${f}">Delete</button>
      </li>
    `).join('');
  }

  async function upload(files){
    if(!files || !files.length) return;
    const form = new FormData();
    for(const f of files) form.append('files', f);
    await fetch('/intelligence/upload', { method:'POST', body: form });
    await refresh();
  }

  list.addEventListener('click', async (e)=>{
    const name = e.target?.dataset?.del;
    if(!name) return;
    await fetch(`/intelligence/upload/${encodeURIComponent(name)}`, { method:'DELETE' });
    await refresh();
  });

  input.onchange = (e)=> upload(e.target.files);
  dz.ondragover = (e)=>{ e.preventDefault(); dz.classList.add('dragover'); };
  dz.ondragleave = ()=> dz.classList.remove('dragover');
  dz.ondrop = (e)=>{
    e.preventDefault(); dz.classList.remove('dragover');
    upload(e.dataTransfer.files);
  };

  runBtn.onclick = async () => {
    const body = { brands: parseBrands(), lookback_days: lookback() };
    const data = await ccc.jsonFetch('/intelligence/report', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    intelCard.style.display = 'block';
    intelBody.innerHTML = renderIntel(data);
  };

  function renderIntel(data){
    if(!data || !data.metrics || !data.metrics.length) return '<div class="muted">No data available.</div>';
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

  refresh();
})();
