# backend/routers/route_index.py
from fastapi import APIRouter, Request
from fastapi.routing import APIRoute

router = APIRouter(tags=["debug"])

@router.get("/__routes")
def list_routes(request: Request):
    app = request.app
    items = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            methods = sorted(list(r.methods - {"HEAD", "OPTIONS"}))
            items.append({
                "path": r.path,
                "methods": methods,
                "name": r.name,
            })
    items.sort(key=lambda x: (x["path"], ",".join(x["methods"])))
    return {"count": len(items), "routes": items}
