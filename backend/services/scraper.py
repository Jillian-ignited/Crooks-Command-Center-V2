import os, json, csv
from typing import List, Dict, Any
import pandas as pd

UPLOAD_DIR = "data/uploads"

# Supported: json (list of posts), .csv with columns like: brand, platform, date, likes, comments, shares, text, url
def save_uploads(files: List[str]) -> List[str]:
    # here `files` are filepaths already saved by router
    return files

def load_all_uploaded_frames() -> pd.DataFrame:
    rows = []
    for fname in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, fname)
        try:
            if fname.lower().endswith(".json"):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        item = item or {}
                        rows.append(normalize_row(item))
            elif fname.lower().endswith(".csv"):
                df = pd.read_csv(path)
                for _, r in df.iterrows():
                    rows.append(normalize_row(dict(r)))
        except Exception as e:
            # skip corrupt files
            pass
    if not rows:
        return pd.DataFrame(columns=["brand","platform","date","likes","comments","shares","text","url"])
    df = pd.DataFrame(rows)
    # coerce types
    for col in ["likes","comments","shares"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def normalize_row(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "brand": str(item.get("brand") or item.get("account") or "").strip(),
        "platform": str(item.get("platform") or "").strip(),
        "date": str(item.get("date") or item.get("timestamp") or "" )[:10],
        "likes": item.get("likes") or item.get("likeCount") or 0,
        "comments": item.get("comments") or item.get("commentCount") or 0,
        "shares": item.get("shares") or item.get("shareCount") or 0,
        "text": item.get("text") or item.get("caption") or "",
        "url": item.get("url") or item.get("permalink") or "",
    }
