const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function fmtNum(n){ return n.toLocaleString(); }

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
  const res = await fetch('/api/intelligence');
  const data = await res.json();
  const m = data.engagement;
  const metrics = {
    totals: m.totals,
    averages: m.averages,
    engagement_rate_percent: m.engagement_rate_percent,
    trend_points: m.trend.length
  };
  $('#intel-metrics').textContent = JSON.stringify(metrics, null, 2);

  const tags = data.hashtags.slice(0, 24);
  const hc = $('#hashtags');
  hc.innerHTML = '';
  tags.forEach(t => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `<strong>#${t.hashtag}</strong><div class="meta">count: ${t.count} · ${t.categories.join(', ')}</div>`;
    hc.appendChild(el);
  });

  const moments = data.cultural_moments;
  const mc = $('#moments');
  mc.innerHTML = '';
  moments.forEach(mo => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `<div><strong>${mo.labels.join(' / ')}</strong></div><div class="meta">${mo.timestamp || ''}</div><div>${mo.summary}</div>`;
    mc.appendChild(el);
  });

  const comp = data.competitive.brand_mentions || [];
  const cc = $('#competitors');
  cc.innerHTML = '';
  comp.forEach(c => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `<div><strong>${c.brand}</strong></div><div class="meta">mentions: ${c.mentions}</div>`;
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
  const res = await fetch('/api/assets');
  const data = await res.json();
  const grid = $('#asset-grid');
  grid.innerHTML = '';
  data.catalog.assets.forEach(a => {
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
  const res = await fetch(`/api/calendar/${view}`);
  const data = await res.json();
  const wrap = $('#calendar-events');
  wrap.innerHTML = '';
  data.events.forEach(ev => {
    const el = document.createElement('div');
    el.className = 'asset';
    el.innerHTML = `
      <div><strong>${ev.title}</strong> — ${ev.date}</div>
      <div class="meta">${ev.cultural_context}</div>
      <div>Deliverables: ${ev.deliverables.join(', ')}</div>
      <div>KPIs: ${Object.entries(ev.target_kpis).map(([k,v])=>k+': '+v).join(' · ')}</div>
      <div>Status: ${ev.status}</div>
    `;
    wrap.appendChild(el);
  });
}

async function loadAgency(){
  const res = await fetch('/api/agency');
  const data = await res.json();
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
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    const data = await res.json();
    const out = $('#upload-results');
    out.innerHTML = '<div class="asset"><strong>Upload Results</strong><pre class="mono">'+JSON.stringify(data, null, 2)+'</pre></div>';
    loadAssets();
    loadIntelligence();
  }
}

window.addEventListener('DOMContentLoaded', () => {
  loadIntelligence();
  loadAssets();
  loadCalendar('7_day_view');
  loadAgency();
  enableUpload();

  $$('#calendar .view-switch .btn').forEach(b => {
    b.addEventListener('click', () => loadCalendar(b.dataset.view));
  });
});
