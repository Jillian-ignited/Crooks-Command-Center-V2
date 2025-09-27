export const apiPost = (path, body, init) => {
  const isFD = body instanceof FormData;
  return fetch(path.startsWith('/')? path: `/${path}`, {
    method: "POST",
    body: isFD ? body : JSON.stringify(body ?? {}),
    headers: isFD ? {} : {"Content-Type":"application/json"},
    ...(init||{})
  }).then(async r => {
    if (!r.ok) throw new Error(`${r.status} ${r.statusText} @ ${path}\n${await r.text()}`);
    const ct = r.headers.get("content-type")||"";
    return ct.includes("application/json") ? r.json() : r.text();
  });
};
