(function(){
  // Same-origin calls (the UI is served by FastAPI)
  window.API_BASE = "";

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
