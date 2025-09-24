(function(){
  const rangeEl = document.getElementById('range');
  const btn = document.getElementById('refreshBtn');
  const card = document.getElementById('calCard');
  const body = document.getElementById('calBody');

  async function load(){
    const range = Number(rangeEl.value||60);
    const data = await ccc.jsonFetch(`/calendar?range_days=${range}`);
    card.style.display = 'block';
    if(!data.events?.length){ body.innerHTML = '<div class="muted">No events in range.</div>'; return; }
    body.innerHTML = `
      <div class="muted">Next ${data.range_days} days</div>
      <ul>${data.events.map(e=>`<li><strong>${e.date}</strong> — ${e.title} <span class="pill">${e.category}</span></li>`).join('')}</ul>
    `;
  }

  btn.onclick = load;
  load();
})();
