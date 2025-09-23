const $  = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);

function switchTab(key){
  $$('.tab').forEach(b=>b.classList.toggle('active', b.dataset.tab===key));
  $$('.panel').forEach(p=>p.classList.toggle('active', p.id===key));
}
$$('.tab').forEach(btn => btn.addEventListener('click', ()=> switchTab(btn.dataset.tab)));

async function safeFetch(url, opts = {}){
  try {
    const r = await fetch(url, opts);
    const ct = (r.headers.get('content-type') || '').toLowerCase();
    if (ct.includes('application/json') || url.includes('/api/')) {
      try {
        const data = await r.json();
        if (!r.ok) return { error: (data && (data.detail || data.error)) || `${r.status} ${r.statusText}`, raw: data };
        return data;
      } catch (_) {}
    }
    const text = await r.text();
    if (!r.ok) return { error: `${r.status} ${r.statusText}`, raw: text };
    try { return JSON.parse(text); } catch { return { error: 'NON_JSON_RESPONSE', raw: text }; }
  } catch (e) {
    return { error: e.message || 'NETWORK_ERROR' };
  }
}

function fmt(n){ try{ return Number(n).toLocaleString(); }catch{ return n; } }

// ---------- INTELLIGENCE ----------
async function loadIntelligence(){
  const data = await safeFetch('/api/intelligence');
  if (data.error){
    $('#intel-metrics').textContent = `Error: ${data.error}\n` + (data.raw ? (typeof data.raw==='string' ? data.raw.slice(0,400) : JSON.stringify(data.raw,null,2)) : '');
    return;
  }
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

  // hashtags
  const hc = $('#hashtags'); hc.innerHTML = '';
  (data.hashtags||[]).slice(0,24).forEach(t=>{
    const el = document.createElement('div');
    el.className='asset';
    el.innerHTML = `<strong>#${t.hashtag}</strong><div class="meta">count: ${t.count}${t.categories?.length?` · ${t.categories.join(', ')}`:''}</div>`;
    hc.appendChild(el);
  });

  // cultural moments
  const mc = $('#moments'); mc.innerHTML = '';
  (data.cultural_moments||[]).forEach(mo=>{
    const el = document.createElement('div');
    el.className='asset';
    el.innerHTML = `<div><strong>${(mo.labels||[]).join(' / ')}</strong></div>
                    <div class="meta">${mo.timestamp || ''}</div>
                    <div>${(mo.summary||'').replace(/\n+/g,' ')}</div>`;
    mc.appendChild(el);
  });

  // enhanced competitors (if route exists)
  const comp = await safeFetch('/api/intelligence/competitors');
  const cv = $('#comp-voice'); cv.innerHTML = '';
  if (!comp.error){
    const sov = document.createElement('div');
    sov.className = 'asset';
    sov.innerHTML = `<div><strong>Share of Voice</strong></div>` +
      (comp.share_of_voice||[]).map(x=>`<div class="meta">${x.brand}: ${x.mentions} · ${x.share_pct}%</div>`).join('');
    cv.appendChild(sov);

    const be = document.createElement('div');
    be.className = 'asset';
    be.innerHTML = `<div><strong>Brand Engagement (avg)</strong></div>` +
      (comp.brand_engagement||[]).map(x=>`<div class="meta">${x.brand}: eng ${fmt(x.avg_engagement)} · views ${fmt(x.avg_views)} (${x.posts} posts)</div>`).join('');
    cv.appendChild(be);

    const tt = document.createElement('div');
    tt.className = 'asset';
    tt.innerHTML = `<div><strong>Trending Terms</strong></div>` +
      (comp.trending_terms||[]).slice(0,20).map(x=>`<span class="chip">#${x.term} <small>${x.score}</small></span>`).join(' ');
    cv.appendChild(tt);
  }

  $('#btn-generate-report').onclick = async ()=>{
    const res = await fetch('/api/reports/generate');
    if(!res.ok){ alert('Report failed'); return; }
    const blob = await res.blob(); const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href=url; a.download='intelligence_report.json'; document.body.appendChild(a); a.click(); a.remove();
  };
}

// ---------- ASSETS ----------
async function loadAssets(){
  const data = await safeFetch('/api/assets');
  const grid = $('#asset-grid'); grid.innerHTML = '';
  if (data.error){ grid.innerHTML = `<div class="asset">Error: ${data.error}</div>`; return; }

  (data.catalog?.assets||[]).forEach(a=>{
    const imgSrc = a.thumbnail ? `/uploads/${a.thumbnail}` :
      'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="100%" height="100%" fill="#0f0f0f"/><text x="50%" y="50%" fill="#777" font-family="monospace" font-size="14" text-anchor="middle">No Preview</text></svg>`);
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

// ---------- CALENDAR ----------
async function loadCalendar(view='7_day_view'){
  const data = await safeFetch(`/api/calendar/${view}`);
  const wrap = $('#calendar-events'); wrap.innerHTML='';
  if (data.error){ wrap.innerHTML = `<div class="asset">Error: ${data.error}</div>`; return; }
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

// ---------- AGENCY ----------
async function loadAgency(){
  const data = await safeFetch('/api/agency');
  $('#agency-data').textContent = JSON.stringify(data, null, 2);
}

// ---------- UPLOADS ----------
function enableUpload(){
  const drop = $('#drop'), input = $('#file-input'), out = $('#upload-results');
  const MAX = 100 * 1024 * 1024;
  const ACCEPT = new Set(['png','jpg','jpeg','gif','webp','mp4','mov','avi','mkv','pdf','ppt','pptx','doc','docx','txt','json','jsonl','csv']);
  const extOf = n => (n.includes('.') ? n.split('.').pop().toLowerCase() : '');
  const okType = f => ACCEPT.has(extOf(f.name));
  const okSize = f => f.size <= MAX;

  drop.addEventListener('click',()=>input.click());
  drop.addEventListener('dragover', e=>{ e.preventDefault(); drop.classList.add('drag'); });
  drop.addEventListener('dragleave', ()=> drop.classList.remove('drag'));
  drop.addEventListener('drop', e=>{
    e.preventDefault(); drop.classList.remove('drag'); handleFiles([...e.dataTransfer.files]);
  });
  input.addEventListener('change', ()=>{ handleFiles([...input.files]); input.value=''; });

  const statusCard = html => { const el = document.createElement('div'); el.className='asset'; el.innerHTML = html; out.prepend(el); return el; };

  async function handleFiles(files){
    if(!files.length) return;
    const errors = [], ok = [];
    files.forEach(f=>{
      if(!okType(f)) errors.push(`❌ ${f.name}: invalid type`);
      else if(!okSize(f)) errors.push(`❌ ${f.name}: over 100MB`);
      else ok.push(f);
    });
    if(errors.length) statusCard(errors.map(e=>`<div>${e}</div>`).join(''));
    if(!ok.length) return;

    const card = statusCard(`<strong>Uploading ${ok.length} file(s)…</strong><div class="meta">Working…</div>`);
    const form = new FormData(); ok.forEach(f=>form.append('files', f));
    try{
      const r = await fetch('/api/upload', { method:'POST', body: form });
      if(!r.ok){ const txt = await r.text(); card.innerHTML = `<div>Upload failed: ${r.status} ${r.statusText}</div><pre class="mono">${txt.slice(0,400)}</pre>`; return; }
      const data = await r.json();
      const bad = (data.results||[]).filter(x=>!x.ok), good = (data.results||[]).filter(x=>x.ok);
      card.innerHTML = `<div><strong>Upload complete</strong></div><div class="meta">Success: ${good.length} · Errors: ${bad.length}</div>`;
      loadAssets(); loadIntelligence();
    }catch(e){
      card.innerHTML = `<div>Upload error: ${e.message||e}</div>`;
    }
  }
}

// ---------- BOOT ----------
window.addEventListener('DOMContentLoaded', ()=>{
  loadIntelligence();
  loadAssets();
  loadCalendar('7_day_view');
  loadAgency();
  bindCalendarButtons();
  enableUpload();
});
