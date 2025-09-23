import os, json, subprocess, shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
from db import SessionLocal, Asset, init_db
from sqlalchemy import select

UPLOAD_DIR = os.environ.get('CCC_UPLOAD_DIR', 'uploads')
THUMB_DIR = os.path.join(UPLOAD_DIR, 'thumbnails')
MAX_FILE_MB = 100

ALLOWED_EXT = {
    'images': {'png','jpg','jpeg','gif','webp'},
    'videos': {'mp4','mov','avi','mkv'},
    'docs':   {'pdf','ppt','pptx','doc','docx','txt'},
    'data':   {'json','jsonl','csv'}
}

init_db()
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

def _type_of(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    for k, exts in ALLOWED_EXT.items():
        if ext in exts: return k
    return 'unknown'

def load_catalog():
    with SessionLocal() as s:
        rows = s.scalars(select(Asset).order_by(Asset.id.desc())).all()
        return {"assets": [r.as_dict() for r in rows]}

def _ffmpeg_available():
    return shutil.which("ffmpeg") is not None

def _video_thumb(src_abs, thumb_abs):
    # Try to extract first frame at 1s using ffmpeg, else fallback to slate
    if _ffmpeg_available():
        try:
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:01", "-i", src_abs, "-frames:v", "1", "-vf", "scale=320:-1", thumb_abs
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass
    # fallback: generate a branded slate
    os.makedirs(os.path.dirname(thumb_abs), exist_ok=True)
    img = Image.new("RGB", (320, 180), color=(13,13,13))
    draw = ImageDraw.Draw(img)
    text = "VIDEO"
    draw.text((12, 12), text, fill=(255,255,255))
    img.save(thumb_abs, "JPEG", quality=85)
    return True

def _image_thumb(src_abs, thumb_abs):
    with Image.open(src_abs) as im:
        if im.mode in ('RGBA','P'): im = im.convert('RGB')
        im.thumbnail((320, 320))
        im.save(thumb_abs, format='JPEG', quality=85)
    return True

def generate_thumbnails(rel_list):
    thumbs = {}
    for rel in rel_list:
        src = os.path.join(UPLOAD_DIR, rel)
        if not os.path.exists(src): continue
        base = os.path.basename(rel)
        name, _ = os.path.splitext(base)
        th_rel = os.path.join('thumbnails', f"{name}_thumb.jpg").replace('\\','/')
        th_abs = os.path.join(UPLOAD_DIR, th_rel)
        atype = _type_of(base)
        try:
            if atype == 'images':
                _image_thumb(src, th_abs)
            elif atype == 'videos':
                _video_thumb(src, th_abs)
            else:
                continue
            thumbs[rel] = th_rel
        except Exception:
            continue
    if thumbs:
        with SessionLocal() as s:
            for rel, th_rel in thumbs.items():
                row = s.execute(select(Asset).where(Asset.rel_path==rel)).scalar_one_or_none()
                if row:
                    row.thumbnail = th_rel
            s.commit()
    return thumbs

def handle_file_upload(file_storage):
    filename = secure_filename(file_storage.filename or '')
    if not filename or _type_of(filename) == 'unknown':
        return {'ok': False, 'error': 'Invalid file type.'}
    size = getattr(file_storage, 'content_length', None) or 0
    if size and size > MAX_FILE_MB * 1024 * 1024:
        return {'ok': False, 'error': f'File too large. Max {MAX_FILE_MB}MB.'}

    save_path = os.path.join(UPLOAD_DIR, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        file_storage.save(save_path)
    except Exception as e:
        return {'ok': False, 'error': f'Failed to save file: {e}'}

    st = os.stat(save_path)
    with SessionLocal() as s:
        asset = Asset(
            filename=filename, rel_path=filename, bytes=st.st_size,
            type=_type_of(filename), created_at=datetime.utcfromtimestamp(st.st_ctime)
        )
        s.add(asset); s.commit(); s.refresh(asset)

        # Auto-thumbnail
        if asset.type in ('images', 'videos'):
            generate_thumbnails([asset.rel_path])
            s.refresh(asset)

        return {'ok': True, 'asset': asset.as_dict()}

def serve_file_download(asset_id):
    with SessionLocal() as s:
        a = s.get(Asset, asset_id)
        if a:
            abs_path = os.path.abspath(os.path.join(UPLOAD_DIR, a.rel_path))
            if os.path.exists(abs_path):
                return abs_path, a.filename
    return None, None

def categorize_assets(files):
    groups = {'Brand Assets': [], 'Social Content': [], 'Video Content': [], 'Intelligence Data': [], 'Documents': []}
    for a in files:
        fn = a.get('filename','').lower()
        t = a.get('type')
        if t == 'images':
            if any(k in fn for k in ['wordmark','castle','medusa','brand','guideline']):
                groups['Brand Assets'].append(a)
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
    by_name = {a['filename']: a for a in assets}
    mapping = []
    for view in ['7_day_view','30_day_view','60_day_view','90_day_view']:
        for ev in calendar.get(view, []):
            used = []
            for fn in ev.get('assets_mapped', []):
                a = by_name.get(fn)
                if a:
                    used.append({'filename': fn, 'asset_id': a['id']})
            mapping.append({'event': ev['title'], 'date': ev['date'], 'assets': used})
    return mapping
