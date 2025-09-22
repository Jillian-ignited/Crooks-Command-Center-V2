import os, uuid, mimetypes, json
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_DIR = os.environ.get('CCC_UPLOAD_DIR', 'uploads')
THUMB_DIR = os.path.join(UPLOAD_DIR, 'thumbnails')
CATALOG_PATH = os.path.join(UPLOAD_DIR, 'assets_catalog.json')

ALLOWED_EXT = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'videos': {'mp4', 'mov', 'avi', 'mkv'},
    'data': {'json', 'jsonl', 'csv'},
    'docs': {'pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt'}
}
MAX_FILE_MB = 200

def _ext_ok(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    for k, exts in ALLOWED_EXT.items():
        if ext in exts:
            return True
    return False

def _type_of(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    for k, exts in ALLOWED_EXT.items():
        if ext in exts:
            return k
    return 'unknown'

def _load_catalog():
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return {'assets': []}
    return {'assets': []}

def _save_catalog(cat):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(CATALOG_PATH, 'w') as f:
        json.dump(cat, f, indent=2)

def scan_upload_directory():
    """Catalog all files with metadata"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    catalog = {'assets': []}
    for root, _, files in os.walk(UPLOAD_DIR):
        for fn in files:
            if fn in ('assets_catalog.json',):
                continue
            fpath = os.path.join(root, fn)
            try:
                stat = os.stat(fpath)
            except Exception:
                continue
            rel = os.path.relpath(fpath, UPLOAD_DIR)
            asset_id = str(uuid.uuid4())
            catalog['assets'].append({
                'id': asset_id,
                'path': rel.replace('\\', '/'),
                'filename': fn,
                'size_bytes': stat.st_size,
                'type': _type_of(fn),
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'thumbnail': None
            })
    _save_catalog(catalog)
    return catalog

def generate_thumbnails(image_files):
    """Create preview thumbnails for images"""
    thumbs = {}
    os.makedirs(THUMB_DIR, exist_ok=True)

    for f in image_files:
        src = os.path.join(UPLOAD_DIR, f)
        if not os.path.exists(src):
            continue
        try:
            with Image.open(src) as im:
                if im.mode in ('RGBA', 'P'):
                    im = im.convert('RGB')
                im.thumbnail((150, 150))
                base = os.path.basename(f)
                name, _ = os.path.splitext(base)
                th_name = f"{name}_thumb.jpg"
                th_path = os.path.join(THUMB_DIR, th_name)
                im.save(th_path, format='JPEG', quality=85)
                thumbs[f] = os.path.relpath(th_path, UPLOAD_DIR).replace('\\', '/')
        except Exception:
            continue

    # Update catalog
    cat = _load_catalog()
    for a in cat.get('assets', []):
        if a.get('type') == 'images':
            rel = a.get('path')
            if rel in thumbs:
                a['thumbnail'] = thumbs[rel]
    _save_catalog(cat)
    return thumbs

def categorize_assets(files):
    """Sort assets by type and purpose"""
    groups = {
        'Brand Assets': [],
        'Social Content': [],
        'Video Content': [],
        'Intelligence Data': [],
        'Documents': []
    }
    for a in files:
        fn = a.get('filename','').lower()
        t = a.get('type')
        if t == 'images':
            if any(k in fn for k in ['wordmark', 'castle', 'medusa', 'brand', 'guideline']):
                groups['Brand Assets'].append(a)
            elif any(k in fn for k in ['story', 'instagram', 'tiktok']):
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
    """Link assets to calendar events"""
    mapping = []
    all_assets = {a['filename']: a for a in assets}
    for view_key in ['7_day_view', '30_day_view', '60_day_view', '90_day_view']:
        for ev in calendar.get(view_key, []):
            used = []
            for fn in ev.get('assets_mapped', []):
                a = all_assets.get(fn)
                if a:
                    used.append({'filename': fn, 'asset_id': a['id']})
            mapping.append({'event': ev['title'], 'date': ev['date'], 'assets': used})
    return mapping

def handle_file_upload(file_storage):
    """Secure file upload with validation"""
    filename = secure_filename(file_storage.filename or '')
    if not filename or not _ext_ok(filename):
        return {'ok': False, 'error': 'Invalid file type.'}
    size = file_storage.content_length or 0
    if size and size > MAX_FILE_MB * 1024 * 1024:
        return {'ok': False, 'error': 'File too large.'}
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR, filename)
    file_storage.save(save_path)

    # update catalog
    cat = _load_catalog()
    asset_id = str(uuid.uuid4())
    stat = os.stat(save_path)
    entry = {
        'id': asset_id,
        'path': filename,
        'filename': filename,
        'size_bytes': stat.st_size,
        'type': _type_of(filename),
        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'thumbnail': None
    }
    cat['assets'].append(entry)
    _save_catalog(cat)

    # Thumbnail if image
    if entry['type'] == 'images':
        generate_thumbnails([filename])

    return {'ok': True, 'asset': entry}

def serve_file_download(asset_id):
    """We return a tuple (abs_path, download_name) or (None, None) if invalid"""
    cat = _load_catalog()
    for a in cat.get('assets', []):
        if a['id'] == asset_id:
            abs_path = os.path.abspath(os.path.join(UPLOAD_DIR, a['path']))
            if os.path.exists(abs_path):
                return abs_path, a['filename']
            break
    return None, None
