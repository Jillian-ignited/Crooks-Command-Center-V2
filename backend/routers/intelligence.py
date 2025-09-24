from pathlib import Path
from fastapi import HTTPException
from typing import Dict

# List uploaded files
@router.get("/uploads")
async def list_uploads() -> Dict[str, list]:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return {"files": files}

# Delete a file by name
@router.delete("/upload/{filename}")
async def delete_upload(filename: str) -> Dict[str, str]:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # prevent path traversal
    dest = Path(UPLOAD_DIR) / filename
    try:
        dest = dest.resolve(strict=False)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not str(dest).startswith(str(Path(UPLOAD_DIR).resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not dest.exists():
        raise HTTPException(status_code=404, detail="File not found")
    dest.unlink()
    return {"deleted": filename}

