(function(){
  const brandsEl = document.getElementById('brands');
  const daysEl = document.getElementById('days');
  const runBtn = document.getElementById('runBtn');
  const card = document.getElementById('summaryCard');
  const body = document.getElementById('summaryBody');

  const parseBrands = () => brandsEl.value.split(',').map(s=>s.trim()).filter(Boolean);
  const lookback = () => Number(daysEl.value || 7);

  runBtn.onclick = async () => {
    const payload = { brands: parseBrands(), lookback_days: lookback() };
    const data = await ccc.jsonFetch('/summary', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    card.style.display = 'block';
    body.innerHTML = `
      <div class="muted">Last ${data.timeframe_days} days</div>
      <p>${data.narrative || ''}</p>
      <div style="margin-top:12px"><div class="muted">Key Moves</div><ul>${(data.key_moves||[]).map(m=>`<li>${m}</li>`).join('')}</ul></div>
      <div style="margin-top:12px"><div class="muted">Risks</div><ul>${(data.risks||[]).map(r=>`<li>${r}</li>`).join('')}</ul></div>
    `;
  };
})();
