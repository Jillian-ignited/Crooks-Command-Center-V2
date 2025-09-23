import os, uuid, json
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from db import SessionLocal, Asset, init_db
from sqlalchemy import select

UPLOAD_DIR = os.environ.get('CCC_UPLOAD_DIR', 'uploads')
THUMB_DIR = os.path.join(UPLOAD_DIR, 'thumbnails')
ALLOWED_EXT = {
    'images': {'png','jpg','jpeg','gif','webp'},
    'videos': {'mp4','mov','avi','mkv'},
    'data':   {'json','jsonl','csv'},
    'docs':   {'pdf','ppt','pptx','doc','docx','txt'}
}
MAX_FILE_MB = 200

init_db()
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

def _type_of(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    for k, exts in ALLOWED_EXT.items():
        if ext in exts: return k
    return 'unknown'

def load_catalog():
    # DB-first
    with SessionLocal() as s:
        rows = s.scalars(select(Asset).order_by(Asset.id.desc())).all()
        return {"assets": [r.as_dict() for r in rows]}

def scan_upload_directory():
    # Optional: sync FS → DB (only adds missing)
    changed = 0
    existing_paths = set()
    with SessionLocal() as s:
        existing_paths = {a.rel_path for a in s.scalars(select(Asset)).all()}
        for root, _, files in os.walk(UPLOAD_DIR):
            for fn in files:
                if root.endswith('thumbnails'): 
                    continue
                rel = os.path.relpath(os.path.join(root, fn), UPLOAD_DIR).replace("\\","/")
                if rel in existing_paths: 
                    continue
                abs_path = os.path.join(UPLOAD_DIR, rel)
                try:
                    st = os.stat(abs_path)
                except Exception:
                    continue
                a = Asset(
                    filename=fn, rel_path=rel, bytes=st.st_size,
                    type=_type_of(fn), created_at=datetime.fromtimestamp(st.st_ctime)
                )
                s.add(a); changed += 1
        s.commit()
    return {"synced": changed}

def generate_thumbnails(image_rel_list):
    thumbs = {}
    for rel in image_rel_list:
        src = os.path.join(UPLOAD_DIR, rel)
        if not os.path.exists(src): continue
        try:
            with Image.open(src) as im:
                if im.mode in ('RGBA','P'): im = im.convert('RGB')
                im.thumbnail((150,150))
                base = os.path.basename(rel)
                name, _ = os.path.splitext(base)
                th_name = f"{name}_thumb.jpg"
                th_path = os.path.join(THUMB_DIR, th_name)
                im.save(th_path, format='JPEG', quality=85)
                thumbs[rel] = os.path.relpath(th_path, UPLOAD_DIR).replace('\\','/')
        except Exception:
            continue
    # write to DB
    if thumbs:
        with SessionLocal() as s:
            for rel, th_rel in thumbs.items():
                row = s.execute(select(Asset).where(Asset.rel_path==rel)).scalar_one_or_none()
                if row:
                    row.thumbnail = th_rel
            s.commit()
    return thumbs

def categorize_assets(files):
    groups = {'Brand Assets': [], 'Social Content': [], 'Video Content': [], 'Intelligence Data': [], 'Documents': []}
    for a in files:
        fn = a.get('filename','').lower()
        t = a.get('type')
        if t == 'images':
            if any(k in fn for k in ['wordmark','castle','medusa','brand','guideline']):
                groups['Brand Assets'].append(a)
            elif any(k in fn for k in ['story','instagram','tiktok']):
                groups['Social Content'].append(a)
            else:
                groups['Social Content'].append(a)
        elif t == 'videos':
            groups['Video Content'].append(a)
        elif t == 'data':
            groups['Intelligence Data'].append(a)
        elif t == 'docs':
            groups['Documents'].append(a)
        else:
            groups['Documents'].append(a)
    return groups

def map_assets_to_campaigns(assets, calendar):
    # API keeps same contract
    by_name = {a['filename']: a for a in assets}
    mapping = []
    for view in ['7_day_view','30_day_view','60_day_view','90_day_view']:
        for ev in calendar.get(view, []):
            used = []
            for fn in ev.get('assets_mapped', []):
                a = by_name.get(fn)
                if a: used.append({'filename': fn, 'asset_id': a['id']})
            mapping.append({'event': ev['title'], 'date': ev['date'], 'assets': used})
    return mapping

def handle_file_upload(file_storage):
    from sqlalchemy import select
    filename = secure_filename(file_storage.filename or '')
    if not filename or _type_of(filename) == 'unknown':
        return {'ok': False, 'error': 'Invalid file type.'}
    size = getattr(file_storage, 'content_length', None) or 0
    if size and size > MAX_FILE_MB * 1024 * 1024:
        return {'ok': False, 'error': 'File too large.'}

    save_path = os.path.join(UPLOAD_DIR, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        file_storage.save(save_path)
    except Exception as e:
        return {'ok': False, 'error': f'Failed to save file: {e}'}

    st = os.stat(save_path)
    with SessionLocal() as s:
        a = Asset(
            filename=filename, rel_path=filename, bytes=st.st_size,
            type=_type_of(filename), created_at=datetime.fromtimestamp(st.st_ctime)
        )
        s.add(a); s.commit(); s.refresh(a)
        # gen thumb if image
        if a.type == 'images':
            generate_thumbnails([a.rel_path])
            s.refresh(a)
        return {'ok': True, 'asset': a.as_dict()}

def serve_file_download(asset_id):
    from sqlalchemy import select
    with SessionLocal() as s:
        a = s.get(Asset, asset_id)
        if a:
            abs_path = os.path.abspath(os.path.join(UPLOAD_DIR, a.rel_path))
            if os.path.exists(abs_path):
                return abs_path, a.filename
    return None, None
