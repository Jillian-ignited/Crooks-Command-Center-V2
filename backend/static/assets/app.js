(function(){
  // Same-origin API calls (UI served by FastAPI)
  async function jsonFetch(url, options={}){
    const res = await fetch(url, options);
    if(!res.ok){
      let msg = await res.text().catch(()=>res.statusText);
      throw new Error(msg || ("HTTP "+res.status));
    }
    return await res.json();
  }
  window.ccc = { jsonFetch };
})();
