(function(){
  const card = document.getElementById('card');
  const body = document.getElementById('body');
  async function load(){
    const data = await ccc.jsonFetch('/agency');
    card.style.display = 'block';
    body.innerHTML = `
      <div class="muted">Week of ${data.week_of}</div>
      <ul>
        ${(data.deliverables||[]).map(d=>`
          <li><strong>${d.title}</strong> — <span class="pill">${d.status}</span> ${d.owner?`· <span class="muted">${d.owner}</span>`:''} ${d.due?`· due ${d.due}`:''}</li>
        `).join('')}
      </ul>
    `;
  }
  load();
})();
