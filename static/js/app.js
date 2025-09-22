const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

async function safeFetch(url, opts = {}) {
  try {
    const r = await fetch(url, opts);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  } catch (e) {
    console.error('Fetch error', url, e);
    return { error: e.message };
  }
}

function fmtNum(n){ try { return Number(n).toLocaleString(); } catch(e){ return n; } }

function switchTab(key){
  $$('.tab').forEach(b=>b.classList.remove('active'));
  $$('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelector(`.tab[data-tab="${key}"]`).classList.add('active');
  document.getElementById(key).classList.add('active');
}

$$('.tab').forEach(btn => {
  btn.addEventListener('click', ()=> switchTab(btn.dataset.tab));
});

async function loadIntelligence(){
  const data = await safeFetch('/api/intelligence');
  if (data.error) { $('#intel-metrics').textContent = 'Error: ' + data.error; return; }
  const m = data.engagement;
  const metrics = {
    totals: m.totals,
    averages: m.averages,
    engagement_rate_percent: m.engagement_rate_percent,
    trend_points: m.trend.length
  };
  $('#intel-metrics').textContent = JSON.stringify(metrics, null, 2);

  const tags = (data.hashtags || []).slice(0, 24);
  const hc = $('#hashtags');
  hc.innerHTML = '';
  tags.forEach(t => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `<strong>#${t.hashtag}</strong><div class="meta">count: ${t.count} · ${(t.categories||[]).join(', ')}</div>`;
    hc.appendChild(el);
  });

  const moments = data.cultural_moments || [];
  const mc = $('#moments');
  mc.innerHTML = '';
  moments.forEach(mo => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `<div><strong>${(mo.labels||[]).join(' / ')}</strong></div><div class="meta">${mo.timestamp || ''}</div><div>${mo.summary || ''}</div>`;
    mc.appendChild(el);
  });

  const comp = (data.competitive && data.competitive.brand_mentions) ? data.competitive.brand_mentions : [];
  const cc = $('#competitors');
  cc.innerHTML = '';
  comp.forEach(c => {
    const sov = (c.share_pct !== undefined) ? ` · share: ${c.share_pct}%` : '';
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `<div><strong>${c.brand}</strong></div><div class="meta">mentions: ${c.mentions}${sov}</div>`;
    cc.appendChild(el);
  });

  $('#btn-generate-report').onclick = async () => {
    const r = await fetch('/api/reports/generate');
    const blob = await r.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'intelligence_report.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
  };
}

async function loadAssets(){
  const data = await safeFetch('/api/assets');
  if (data.error) { $('#asset-grid').innerHTML = `<div class="asset">Error: ${data.error}</div>`; return; }
  const grid = $('#asset-grid');
  grid.innerHTML = '';
  (data.catalog.assets || []).forEach(a => {
    const imgSrc = a.thumbnail ? `/uploads/${a.thumbnail}` : '/static/img/placeholder.png';
    const card = document.createElement('div');
    card.className = 'asset';
    card.innerHTML = `
      <img src="${imgSrc}" alt="${a.filename}" onerror="this.src='/static/img/placeholder.png'">
      <div class="meta">${a.filename}<br>${(a.size_bytes/1024).toFixed(1)} KB · ${a.type}</div>
      <div class="actions"><a class="btn small" href="/api/assets/${a.id}/download"><i class="fa-solid fa-download"></i> Download</a></div>
    `;
    grid.appendChild(card);
  });
}

async function loadCalendar(view='7_day_view'){
  const data = await safeFetch(`/api/calendar/${view}`);
  if (data.error) { $('#calendar-events').innerHTML = `<div class="asset">Error: ${data.error}</div>`; return; }
  const wrap = $('#calendar-events');
  wrap.innerHTML = '';
  (data.events || []).forEach(ev => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `
      <div><strong>${ev.title}</strong> — ${ev.date}</div>
      <div class="meta">${ev.cultural_context || ''}</div>
      <div>Deliverables: ${(ev.deliverables || []).join(', ')}</div>
      <div>KPIs: ${Object.entries(ev.target_kpis || {}).map(([k,v])=>k+': '+v).join(' · ')}</div>
      <div>Status: ${ev.status || ''}</div>
    `;
    wrap.appendChild(el);
  });
}

async function loadAgency(){
  const data = await safeFetch('/api/agency');
  $('#agency-data').textContent = JSON.stringify(data, null, 2);
}

function enableUpload(){
  const drop = $('#drop');
  const input = $('#file-input');
  drop.addEventListener('click', ()=> input.click());
  drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('drag'); });
  drop.addEventListener('dragleave', e => { drop.classList.remove('drag'); });
  drop.addEventListener('drop', e => {
    e.preventDefault(); drop.classList.remove('drag');
    const files = Array.from(e.dataTransfer.files);
    sendFiles(files);
  });
  input.addEventListener('change', () => {
    const files = Array.from(input.files);
    sendFiles(files);
    input.value = '';
  });

  async function sendFiles(files){
    const form = new FormData();
    files.forEach(f => form.append('files', f));
    let out = $('#upload-results');
    try{
      const res = await fetch('/api/upload', { method: 'POST', body: form });
      const data = await res.json();
      out.innerHTML = '<div class="asset"><strong>Upload Results</strong><pre class="mono">'+JSON.stringify(data, null, 2)+'</pre></div>';
      loadAssets();
      loadIntelligence();
    }catch(e){
      out.innerHTML = '<div class="asset">Upload error: '+(e.message||e)+'</div>';
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  loadIntelligence();
  loadAssets();
  loadCalendar('7_day_view');
  loadAgency();
  enableUpload();

  $$('#calendar .view-switch .btn').forEach(b => {
    if (b.dataset.view) {
      b.addEventListener('click', () => loadCalendar(b.dataset.view));
    }
  });

  // Lightweight Asset search UX
  const hdr = document.querySelector('#assets .card h2');
  if(hdr && !document.getElementById('asset-search')){
    const s = document.createElement('input');
    s.id = 'asset-search';
    s.placeholder = 'Search assets…';
    s.className = 'btn';
    s.style.marginLeft = '8px';
    hdr.appendChild(s);
    s.addEventListener('input', async () => {
      const q = s.value.trim();
      if(!q){ return loadAssets(); }
      const r = await safeFetch('/api/assets/search?q='+encodeURIComponent(q));
      const grid = $('#asset-grid'); grid.innerHTML='';
      (r.results||[]).forEach(a => {
        const imgSrc = a.thumbnail ? `/uploads/${a.thumbnail}` : '/static/img/placeholder.png`;
        const card = document.createElement('div');
        card.className = 'asset';
        card.innerHTML = `
          <img src="${imgSrc}" alt="${a.filename}" onerror="this.src='/static/img/placeholder.png'">
          <div class="meta">${a.filename}<br>${(a.size_bytes/1024).toFixed(1)} KB · ${a.type}</div>
          <div class="actions"><a class="btn small" href="/api/assets/${a.id}/download"><i class="fa-solid fa-download"></i> Download</a></div>
        `;
        grid.appendChild(card);
      });
    });
  }
});
