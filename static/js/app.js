/* CROOKS & CASTLES — COMMAND CENTER V2
 * Frontend glue: loads intel, assets, calendar, agency; handles uploads.
 */

const $ = (q, el=document) => el.querySelector(q);
const $$ = (q, el=document) => Array.from(el.querySelectorAll(q));

/* ---------- helpers ---------- */
async function safeFetch(url, opts={}) {
  const r = await fetch(url, opts);
  const ct = (r.headers.get('content-type')||'').toLowerCase();
  const text = await r.text();
  if (ct.includes('application/json')) {
    const json = JSON.parse(text || '{}');
    if (!r.ok) throw new Error(json.error || json.detail || `${r.status} ${r.statusText}`);
    return json;
  }
  // if HTML came back, surface it to debug panel
  throw new Error(text.slice(0,200));
}
function setStatus(msg, ok=true){ const el = $('#app-status'); el.textContent = msg; el.className = ok? 'ok':'err'; }

/* ---------- tabs ---------- */
function bindTabs(){
  const map = {
    intel: $('#tab-intel'),
    assets: $('#tab-assets'),
    calendar: $('#tab-calendar'),
    agency: $('#tab-agency'),
    upload: $('#tab-upload'),
  };
  $$('.tabs button').forEach(b=>{
    b.addEventListener('click', ()=>{
      $$('.tabs button').forEach(x=>x.classList.remove('active')); b.classList.add('active');
      Object.values(map).forEach(s=>s.classList.add('hidden'));
      map[b.dataset.tab].classList.remove('hidden');
    });
  });
}

/* ---------- INTELLIGENCE ---------- */
async function loadIntelligence(){
  try{
    const data = await safeFetch('/api/intelligence');
    // Overview KPIs
    const k = $('#intel-overview'); k.innerHTML = '';
    const totals = data.engagement?.totals || {};
    const rate = data.engagement?.engagement_rate_percent ?? 0;
    const blocks = [
      {label:'Posts', val: data.posts_count || 0},
      {label:'Likes', val: totals.likes || 0},
      {label:'Comments', val: totals.comments || 0},
      {label:'Shares', val: totals.shares || 0},
      {label:'Views', val: totals.views || 0},
      {label:'Eng. Rate', val: `${rate}%`}
    ];
    blocks.forEach(x=>{
      const d = document.createElement('div'); d.className='kpi';
      d.innerHTML = `<div class="meta">${x.label}</div><div style="font-weight:700">${x.val}</div>`;
      k.appendChild(d);
    });

    // Hashtags
    const hc = $('#hashtags'); hc.innerHTML='';
    (data.hashtags||[]).slice(0,30).forEach(t=>{
      const el = document.createElement('div'); el.className='asset';
      el.innerHTML = `<div class="pill">#${t.hashtag || t.term}</div><div class="meta">count: ${t.count || t.score || 0}</div>`;
      hc.appendChild(el);
    });

    // Cultural Moments
    const mc = $('#moments'); mc.innerHTML='';
    (data.cultural_moments||[]).forEach(m=>{
      const el = document.createElement('div'); el.className='asset';
      el.innerHTML = `<div><strong>${(m.labels||[]).join(' · ')}</strong></div>
                      <div class="meta">${m.timestamp || ''}</div>
                      <div>${(m.summary||'').slice(0,240)}</div>`;
      mc.appendChild(el);
    });

    // Competitors (11 brands supported by backend)
    try{
      const comp = await safeFetch('/api/intelligence/competitors');
      const box = $('#comp-voice'); box.innerHTML = '';
      const sov = comp.share_of_voice || comp.competitive?.brand_mentions || [];
      const be = comp.brand_engagement || [];

      const sovCard = document.createElement('div'); sovCard.className='asset';
      sovCard.innerHTML = `<div style="font-weight:700;margin-bottom:6px">Share of Voice</div>` +
        sov.map(x=>`<div class="meta">${x.brand}: ${x.mentions} · ${x.share_pct}%</div>`).join('');
      box.appendChild(sovCard);

      if (be.length){
        const beCard = document.createElement('div'); beCard.className='asset';
        beCard.innerHTML = `<div style="font-weight:700;margin-bottom:6px">Brand Engagement (avg)</div>` +
          be.map(x=>`<div class="meta">${x.brand}: eng ${x.avg_engagement} · views ${x.avg_views} (${x.posts} posts)</div>`).join('');
        box.appendChild(beCard);
      }
    }catch(e){
      $('#comp-voice').innerHTML = `<div class="asset">Competitor API error: <span class="err">${e.message}</span></div>`;
    }

    // Debug
    $('#intel-debug').textContent = JSON.stringify(data, null, 2);
    setStatus('connected', true);
  }catch(e){
    setStatus('intel error', false);
    $('#intel-debug').textContent = 'INTEL ERROR: ' + e.message;
  }
}

/* ---------- ASSETS ---------- */
async function loadAssets(){
  try{
    const data = await safeFetch('/api/assets');
    const grid = $('#asset-grid'); grid.innerHTML='';
    (data.assets || data).forEach(a=>{
      const url = `/api/assets/${a.id}/download`;
      const thumb = a.thumbnail ? a.thumbnail : '';
      const t = document.createElement('div'); t.className='asset';
      t.innerHTML = `
        <div class="thumb">${thumb ? `<img src="${thumb}" alt="${a.filename}">` : `<i class="fa fa-image"></i>`}</div>
        <div style="margin-top:6px;font-weight:600">${a.filename}</div>
        <div class="meta">${(a.type||'file').toUpperCase()} · ${formatSize(a.size_bytes||a.bytes||0)}</div>
        <a class="btn" href="${url}"><i class="fa fa-download"></i>Download</a>`;
      grid.appendChild(t);
    });
  }catch(e){
    $('#asset-grid').innerHTML = `<div class="asset">ASSET ERROR: <span class="err">${e.message}</span></div>`;
    setStatus('assets error', false);
  }
}
function formatSize(b){ if(!b) return '—'; const u=['B','KB','MB','GB']; let i=0; while(b>1024&&i<u.length-1){b/=1024;i++;} return `${b.toFixed(1)} ${u[i]}` }

/* ---------- CALENDAR ---------- */
async function loadCalendar(view='7_day_view'){
  $$('.view-switch button').forEach(b=> b.classList.toggle('active', b.dataset.view===view));
  try{
    const payload = await safeFetch(`/api/calendar/${view}`);
    const events = payload.events || payload[view] || [];
    const wrap = $('#calendar-events'); wrap.innerHTML='';
    events.forEach(ev=>{
      const kpis = Object.entries(ev.target_kpis || {}).map(([k,v])=>`${k}: ${v}`).join(' · ');
      const el = document.createElement('div'); el.className='asset';
      el.innerHTML = `
        <div style="font-weight:700">${ev.title}</div>
        <div class="meta">${ev.date} — ${ev.cultural_context || ''}</div>
        <div>Deliverables: ${(ev.deliverables || []).join(', ') || '—'}</div>
        <div>Assets: ${(ev.assets_mapped || []).join(', ') || '—'}</div>
        <div>KPIs: ${kpis || '—'}</div>
        <div>Status: ${ev.status || 'planned'}</div>`;
      wrap.appendChild(el);
    });
  }catch(e){
    $('#calendar-events').innerHTML = `<div class="asset">CALENDAR ERROR: <span class="err">${e.message}</span></div>`;
    setStatus('calendar error', false);
  }
}
function bindCalendar(){
  $$('.view-switch [data-view]').forEach(b=>{
    b.addEventListener('click', ()=> loadCalendar(b.dataset.view));
  });
}

/* ---------- AGENCY ---------- */
async function loadAgency(){
  try{
    const data = await safeFetch('/api/agency');
    const a = (data.agencies && data.agencies[0]) || data || {};
    const kpis = $('#agency-kpis'); kpis.innerHTML = '';
    const items = [
      ['Phase', a.phase],
      ['Monthly Budget', `$${(a.monthly_budget||0).toLocaleString()}`],
      ['Budget Used', `$${(a.budget_used||0).toLocaleString()}`],
      ['On-Time', `${a.on_time_delivery||0}%`],
      ['Quality', `${a.quality_score||0}`],
      ['Response', a.performance_metrics?.response_time || a.response_time || '—'],
      ['Revisions', a.performance_metrics?.revision_rounds || a.revision_rounds || '—'],
      ['Client Sat', a.performance_metrics?.client_satisfaction || a.client_satisfaction || '—']
    ];
    items.forEach(([k,v])=>{
      const d = document.createElement('div'); d.className='kpi'; d.innerHTML = `<div class="meta">${k}</div><div style="font-weight:700">${v}</div>`;
      kpis.appendChild(d);
    });

    const prj = $('#agency-projects'); prj.innerHTML='';
    (a.current_projects || a.projects || []).forEach(p=>{
      const el = document.createElement('div'); el.className='asset';
      el.innerHTML = `<div style="font-weight:700">${p.name}</div>
                      <div class="meta">${p.status} · due ${p.due_date || '—'}</div>`;
      prj.appendChild(el);
    });

    const del = $('#agency-deliverables'); del.innerHTML='';
    const breakdown = a.deliverables_breakdown || {};
    ['completed','in_progress','pending'].forEach(bucket=>{
      const list = breakdown[bucket] || [];
      const el = document.createElement('div'); el.className='asset';
      el.innerHTML = `<div style="font-weight:700;text-transform:uppercase">${bucket.replace('_',' ')}</div>` +
        (list.length ? list.map(x=>`<div class="meta">${x}</div>`).join('') : `<div class="meta">—</div>`);
      del.appendChild(el);
    });
  }catch(e){
    $('#agency-kpis').innerHTML = `<div class="asset">AGENCY ERROR: <span class="err">${e.message}</span></div>`;
    setStatus('agency error', false);
  }
}

/* ---------- UPLOADS ---------- */
function enableUpload(){
  const drop = $('#drop'), picker = $('#picker'), browse = $('#browse'), bar = $('#bar'), log = $('#upload-log'), grid = $('#uploaded');
  const acceptMax = 100 * 1024 * 1024; // 100MB

  function pick(){ picker.click(); }
  function dragging(on){ drop.classList.toggle('drag', on); }
  function filesFrom(e){
    return e.dataTransfer?.files || e.target?.files || [];
  }
  async function send(file){
    if (file.size > acceptMax) throw new Error(`${file.name}: over 100MB`);
    const fd = new FormData(); fd.append('files', file);
    const r = await fetch('/api/upload', { method:'POST', body: fd});
    if (!r.ok) throw new Error(`${file.name}: ${r.status} ${r.statusText}`);
    const data = await r.json();
    return data;
  }
  function addThumb(a){
    const t = document.createElement('div'); t.className='asset';
    t.innerHTML = `
      <div class="thumb">${a.thumbnail ? `<img src="${a.thumbnail}">` : `<i class="fa fa-file"></i>`}</div>
      <div style="margin-top:6px;font-weight:600">${a.filename}</div>
      <div class="meta">${(a.type||'file').toUpperCase()} · ${formatSize(a.size_bytes||a.bytes||0)}</div>`;
    grid.prepend(t);
  }

  browse.addEventListener('click', pick);
  ['dragenter','dragover'].forEach(evt=> drop.addEventListener(evt, e=>{e.preventDefault(); dragging(true);} ));
  ['dragleave','dragend','drop'].forEach(evt=> drop.addEventListener(evt, e=>{e.preventDefault(); dragging(false);} ));
  drop.addEventListener('drop', async e=>{
    const files = filesFrom(e); if (!files.length) return;
    bar.style.width = '0%'; log.textContent = '';
    let done = 0;
    for (const f of files){
      try{
        const out = await send(f);
        const assets = out.assets || out; // backend may return {assets:[...] }
        (Array.isArray(assets)?assets:[assets]).forEach(addThumb);
        done++;
        bar.style.width = `${Math.round(done/files.length*100)}%`;
      }catch(err){
        log.textContent += (log.textContent?'\n':'') + err.message;
      }
    }
    // refresh main asset grid after uploads
    loadAssets();
  });

  picker.addEventListener('change', async e=>{
    const files = filesFrom(e); if (!files.length) return;
    bar.style.width = '0%'; log.textContent = '';
    let done = 0;
    for (const f of files){
      try{
        const out = await send(f);
        const assets = out.assets || out;
        (Array.isArray(assets)?assets:[assets]).forEach(addThumb);
        done++;
        bar.style.width = `${Math.round(done/files.length*100)}%`;
      }catch(err){
        log.textContent += (log.textContent?'\n':'') + err.message;
      }
    }
    loadAssets();
  });
}

/* ---------- boot ---------- */
window.addEventListener('DOMContentLoaded',()=>{
  bindTabs();
  bindCalendar();
  enableUpload();
  loadIntelligence();
  loadAssets();
  loadCalendar('7_day_view');
  loadAgency();
});
