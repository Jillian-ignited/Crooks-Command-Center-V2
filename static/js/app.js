const $  = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);

function switchTab(key){
  $$('.tab').forEach(b=>b.classList.toggle('active', b.dataset.tab===key));
  $$('.panel').forEach(p=>p.classList.toggle('active', p.id===key));
}
$$('.tab').forEach(btn => btn.addEventListener('click', ()=> switchTab(btn.dataset.tab)));

async function safeFetch(url, opts={}){
  try{
    const r = await fetch(url, opts);
    if(!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    // endpoints that return files (report/csv) won't be JSON
    const ct = r.headers.get('content-type') || '';
    if(!ct.includes('application/json')) return r;
    return await r.json();
  }catch(e){ return {error: e.message}; }
}

function fmtNum(n){ try{ return Number(n).toLocaleString(); }catch{ return n; } }

// ---------------- INTELLIGENCE ----------------
async function loadIntelligence(){
  const data = await safeFetch('/api/intelligence');
  if(data.error){ $('#intel-metrics').textContent = 'Error: ' + data.error; return; }
  const m = data.engagement || {};
  const metrics = {
    posts: data.posts_count || 0,
    likes: m.totals?.likes || 0,
    comments: m.totals?.comments || 0,
    shares: m.totals?.shares || 0,
    views: m.totals?.views || 0,
    engagement_rate_percent: m.engagement_rate_percent || 0,
    trend_points: (m.trend||[]).length
  };
  $('#intel-metrics').textContent = JSON.stringify(metrics, null, 2);

  const tags = (data.hashtags || []).slice(0, 24);
  const hc = $('#hashtags'); hc.innerHTML = '';
  tags.forEach(t=>{
    const el = document.createElement('div');
    el.className='asset';
    el.innerHTML = `<strong>#${t.hashtag}</strong><div class="meta">count: ${t.count}${t.categories?.length?` · ${t.categories.join(', ')}`:''}</div>`;
    hc.appendChild(el);
  });

  const moments = data.cultural_moments || [];
  const mc = $('#moments'); mc.innerHTML = '';
  moments.forEach(mo=>{
    const el = document.createElement('div');
    el.className='asset';
    el.innerHTML = `<div><strong>${(mo.labels||[]).join(' / ')}</strong></div>
                    <div class="meta">${mo.timestamp || ''}</div>
                    <div>${(mo.summary||'').replace(/\n+/g,' ')}</div>`;
    mc.appendChild(el);
  });

  const comp = data.competitive?.brand_mentions || [];
  const cc = $('#competitors'); cc.innerHTML = '';
  comp.forEach(c=>{
    const el = document.createElement('div');
    el.className='asset';
    el.innerHTML = `<div><strong>${c.brand}</strong></div><div class="meta">mentions: ${c.mentions} · share: ${c.share_pct}%</div>`;
    cc.appendChild(el);
  });

  $('#btn-generate-report').onclick = async ()=>{
    const res = await fetch('/api/reports/generate');
    if(!res.ok){ alert('Report failed.'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href=url; a.download='intelligence_report.json';
    document.body.appendChild(a); a.click(); a.remove();
  };
}

// ---------------- ASSETS ----------------
async function loadAssets(){
  const data = await safeFetch('/api/assets');
  const grid = $('#asset-grid'); grid.innerHTML = '';
  if(data.error){ grid.innerHTML = `<div class="asset">Error: ${data.error}</div>`; return; }
  (data.catalog?.assets || []).forEach(a=>{
    const imgSrc = a.thumbnail ? `/uploads/${a.thumbnail}` : 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250"><rect width="100%" height="100%" fill="#0f0f0f"/><text x="50%" y="50%" fill="#777" font-family="monospace" font-size="14" text-anchor="middle">No Preview</text></svg>`);
    const card = document.createElement('div');
    card.className='asset';
    card.innerHTML = `
      <img src="${imgSrc}" alt="${a.filename}">
      <div class="meta">${a.filename}<br>${(a.size_bytes/1024).toFixed(1)} KB · ${a.type||'file'}</div>
      <div><a class="btn small" href="/api/assets/${a.id}/download"><i class="fa-solid fa-download"></i> Download</a></div>
    `;
    grid.appendChild(card);
  });
}

// ---------------- CALENDAR ----------------
async function loadCalendar(view='7_day_view'){
  const data = await safeFetch(`/api/calendar/${view}`);
  const wrap = $('#calendar-events'); wrap.innerHTML='';
  if(data.error){ wrap.innerHTML = `<div class="asset">Error: ${data.error}</div>`; return; }
  (data.events||[]).forEach(ev=>{
    const el = document.createElement('div');
    el.className = 'asset';
    const kpis = Object.entries(ev.target_kpis||{}).map(([k,v])=>`${k}: ${v}`).join(' · ');
    el.innerHTML = `
      <div><strong>${ev.title}</strong> — ${ev.date}</div>
      <div class="meta">${ev.cultural_context || ''}</div>
      <div>Deliverables: ${(ev.deliverables||[]).join(', ')}</div>
      <div>KPIs: ${kpis || '—'}</div>
      <div>Status: ${ev.status || 'planned'}</div>
    `;
    wrap.appendChild(el);
  });
}
function bindCalendarButtons(){
  $$('#calendar .view-switch .btn').forEach(b=>{
    if(b.dataset.view){ b.addEventListener('click', ()=> loadCalendar(b.dataset.view)); }
  });
}

// ---------------- AGENCY ----------------
async function loadAgency(){
  const data = await safeFetch('/api/agency');
  $('#agency-data').textContent = JSON.stringify(data, null, 2);
}

// ---------------- UPLOADS ----------------
function enableUpload(){
  const drop = $('#drop'); const input = $('#file-input'); const out = $('#upload-results');
  drop.addEventListener('click',()=>input.click());
  drop.addEventListener('dragover', e=>{ e.preventDefault(); drop.classList.add('drag'); });
  drop.addEventListener('dragleave', ()=> drop.classList.remove('drag'));
  drop.addEventListener('drop', e=>{
    e.preventDefault(); drop.classList.remove('drag'); sendFiles([...e.dataTransfer.files]);
  });
  input.addEventListener('change', ()=>{ sendFiles([...input.files]); input.value=''; });

  async function sendFiles(files){
    const form = new FormData(); files.forEach(f=>form.append('files', f));
    try{
      const r = await fetch('/api/upload', { method:'POST', body:form });
      const data = await r.json();
      out.innerHTML = `<div class="asset"><strong>Upload Results</strong><pre class="mono">${JSON.stringify(data,null,2)}</pre></div>`;
      loadAssets(); loadIntelligence();
    }catch(e){
      out.innerHTML = `<div class="asset">Upload error: ${e.message||e}</div>`;
    }
  }
}

// ---------------- ADMIN FORMS (DB) ----------------
async function postJSON(url, body){
  const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  try{ return await r.json(); }catch{ return {error:'non-json response'} }
}
function bindAdminForms(){
  const fe = $('#form-add-event');
  if(fe){
    fe.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const fd = new FormData(fe);
      const payload = {
        date: fd.get('date'),
        title: fd.get('title'),
        status: fd.get('status') || 'planned',
        deliverables: [], assets_mapped: [], target_kpis: {}
      };
      const res = await postJSON('/api/calendar', payload);
      alert(res.ok ? 'Event created' : ('Error: ' + (res.error||'unknown')));
      if(res.ok) loadCalendar('30_day_view');
    });
  }
  const fp = $('#form-add-project');
  if(fp){
    fp.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const fd = new FormData(fp);
      const res = await postJSON(`/api/agency/${fd.get('agency_id')}/projects`, {
        name: fd.get('name'),
        due_date: fd.get('due_date') || null,
        status: 'pending'
      });
      alert(res.ok ? 'Project created' : ('Error: ' + (res.error||'unknown')));
      if(res.ok) loadAgency();
    });
  }
}

// ---------------- BOOT ----------------
window.addEventListener('DOMContentLoaded', ()=>{
  loadIntelligence();
  loadAssets();
  loadCalendar('7_day_view');
  loadAgency();
  enableUpload();
  bindCalendarButtons();
  bindAdminForms();
});
