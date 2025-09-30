# backend/file_parser.py
import pandas as pd
from pathlib import Path
import json

def parse_uploaded_file(file_path: str) -> tuple[list, str]:
    """
    Parse CSV, JSON, JSONL, or Excel file and return data + detected type
    Returns: (data as list of dicts, source_type)
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
            return df.to_dict('records'), detect_source_type(df)
        
        elif ext == '.jsonl':
            # Parse JSONL (one JSON object per line)
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(f"Skipping invalid JSON line: {e}")
                            continue
            return data, detect_source_type_from_json(data)
        
        elif ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Try parsing as JSONL first (Apify often uses .json for JSONL)
                if '\n' in content and not content.startswith('['):
                    data = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if line:
                            try:
                                data.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                    if data:
                        return data, detect_source_type_from_json(data)
                
                # Try parsing as regular JSON
                data = json.loads(content)
                if isinstance(data, list):
                    return data, detect_source_type_from_json(data)
                else:
                    return [data], "unknown"
        
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return df.to_dict('records'), detect_source_type(df)
        
        else:
            print(f"Unsupported file extension: {ext}")
            return [], "unknown"
    
    except Exception as e:
        print(f"Error parsing file: {e}")
        import traceback
        traceback.print_exc()
        return [], "unknown"

def detect_source_type(df: pd.DataFrame) -> str:
    """Detect if data is from Instagram, TikTok, hashtag scrape, etc."""
    columns = [c.lower() for c in df.columns]
    
    if any('instagram' in c or 'ig_' in c for c in columns):
        return "instagram"
    elif any('tiktok' in c or 'tt_' in c for c in columns):
        return "tiktok"
    elif any('hashtag' in c or '#' in c for c in columns):
        return "hashtag"
    elif any('engagement' in c or 'likes' in c or 'comments' in c for c in columns):
        return "social_media"
    else:
        return "general"

def detect_source_type_from_json(data: list) -> str:
    """Detect source type from JSON structure"""
    if not data or len(data) == 0:
        return "unknown"
    
    first_item = data[0]
    keys = [k.lower() for k in first_item.keys()]
    
    # Check for common Apify/social media fields
    if any('instagram' in k for k in keys):
        return "instagram"
    elif any('tiktok' in k for k in keys):
        return "tiktok"
    elif any('hashtag' in k or 'tag' in k for k in keys):
        return "hashtag"
    elif any(k in ['likes', 'comments', 'shares', 'engagement'] for k in keys):
        return "social_media"
    else:
        return "social_media"
