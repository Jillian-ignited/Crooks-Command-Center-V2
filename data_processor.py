import json, re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import List, Dict, Any

# --- robust JSONL loader ------------------------------------------------------
def _safe_json_loads(line: str):
    try:
        return json.loads(line)
    except Exception:
        try:
            cleaned = line.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            return json.loads(cleaned)
        except Exception:
            return None

def load_jsonl_data(file_path: str) -> List[Dict[str, Any]]:
    """Load and parse JSONL files from Instagram/TikTok scrapers"""
    rows: List[Dict[str, Any]] = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = _safe_json_loads(line)
            if obj is not None and isinstance(obj, dict):
                rows.append(obj)
    return rows

# --- hashtags & trends --------------------------------------------------------
def analyze_hashtags(posts: List[Dict[str, Any]]):
    """Extract and analyze hashtag trends"""
    counter = Counter()
    for p in posts:
        tags = p.get('hashtags') or []
        if not tags:
            text = f"{p.get('caption','')} {p.get('description','')}"
            tags = re.findall(r"#(\w+)", text)
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split() if t.strip().startswith('#')]
        for t in tags:
            tag = t.lower().lstrip('#')
            if tag:
                counter[tag] += 1

    # simple cultural buckets
    categories = {
        'hip-hop': {'hiphop','hip-hop','rap','trap'},
        'streetwear': {'streetwear','sneakers','kicks','hypebeast','ootd'},
        'heritage': {'archive','y2k','throwback','heritage','legacy'}
    }
    out = []
    for tag, count in counter.most_common():
        cats = [c for c, keys in categories.items() if any(k in tag for k in keys)]
        out.append({'hashtag': tag, 'count': count, 'categories': cats})
    return out

# --- engagement metrics -------------------------------------------------------
def calculate_engagement_metrics(posts: List[Dict[str, Any]]):
    """Calculate comprehensive engagement analytics from real posts"""
    total_likes = total_comments = total_shares = total_views = 0
    by_day = defaultdict(lambda: {'likes':0,'comments':0,'shares':0,'views':0,'count':0})

    for p in posts:
        total_likes    += int(p.get('likesCount') or 0)
        total_comments += int(p.get('commentsCount') or 0)
        total_shares   += int(p.get('shareCount') or 0)
        total_views    += int(p.get('viewCount') or 0)

        ts = p.get('timestamp')
        if ts:
            try:
                day = datetime.fromisoformat(ts.replace('Z', '+00:00')).date().isoformat()
            except Exception:
                day = 'unknown'
        else:
            day = 'unknown'

        d = by_day[day]
        d['likes']    += int(p.get('likesCount') or 0)
        d['comments'] += int(p.get('commentsCount') or 0)
        d['shares']   += int(p.get('shareCount') or 0)
        d['views']    += int(p.get('viewCount') or 0)
        d['count']    += 1

    post_count = len(posts) or 1
    avg_eng = (total_likes + total_comments + total_shares) / post_count
    trend = [{
        'day': day,
        'avg_engagement': round((vals['likes']+vals['comments']+vals['shares'])/max(1, vals['count']), 2),
        'avg_views': round(vals['views']/max(1, vals['count']), 2),
        'posts': vals['count']
    } for day, vals in sorted(by_day.items())]

    er = round(((total_likes + total_comments + total_shares) / total_views * 100.0), 2) if total_views > 0 else 0.0

    return {
        'totals': {
            'likes': total_likes, 'comments': total_comments, 'shares': total_shares,
            'views': total_views, 'posts': len(posts)
        },
        'averages': {'engagement_per_post': round(avg_eng, 2)},
        'engagement_rate_percent': er,
        'trend': trend
    }

# --- cultural signals ---------------------------------------------------------
def identify_cultural_moments(posts: List[Dict[str, Any]]):
    """Detect cultural events and trends from social data (caption/description)"""
    moments = []
    keywords = [
        ('Hispanic Heritage', ['hispanic','latino','latinx','mexico']),
        ('Hip-Hop Anniversary', ['hiphop','hip-hop','rap','biggie','tupac','wu-tang']),
        ('Streetwear Heritage', ['archive','throwback','y2k','heritage']),
    ]
    for p in posts:
        full_text = f"{p.get('caption','')} {p.get('description','')}"
        tl = full_text.lower()
        hit = [label for label, keys in keywords if any(k in tl for k in keys)]
        if hit:
            moments.append({
                'timestamp': p.get('timestamp'),
                'url': p.get('url'),
                'labels': sorted(set(hit)),
                'summary': full_text[:200].replace('\n', ' ')
            })
    return moments

# --- competitive share-of-voice ----------------------------------------------
def competitive_analysis(data: Dict[str, Any]):
    """Analyze competitive positioning via brand mention hits in text"""
    posts = data.get('all_posts', [])
    brand_mentions = Counter()
    competitors = [
        'crooks & castles','crooks and castles','crooks',
        'supreme','bape','kith','palace','fear of god',
        'off-white','purple brand','stussy','billionaire boys club'
    ]
    for p in posts:
        tl = f"{p.get('caption','')} {p.get('description','')}".lower()
        for c in competitors:
            if c in tl:
                brand_mentions[c] += 1

    total = sum(brand_mentions.values()) or 1
    comp = [{'brand': b.title(), 'mentions': n, 'share_pct': round(n*100/total, 2)}
            for b, n in brand_mentions.most_common()]
    return {'brand_mentions': comp, 'notes': 'Mentions parsed from captions/descriptions.'}

# --- report snapshot ----------------------------------------------------------
def generate_intelligence_report(data: Dict[str, Any]):
    """Create export-ready intelligence report (JSON)"""
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'posts': len(data.get('all_posts', [])),
            'engagement_rate_percent': data.get('engagement', {}).get('engagement_rate_percent', 0.0)
        },
        'top_hashtags': data.get('hashtags', [])[:20],
        'cultural_moments': data.get('cultural_moments', [])[:20],
        'competitive': data.get('competitive', {}),
        'recommendations': [
            'Prioritize cultural moments in the next 7–14 days.',
            'Repurpose best-performing formats across IG Reels/TikTok.',
            'Fill asset gaps 72h pre-launch on the calendar.'
        ]
    }

# Optional explicit export list (prevents import surprises)
__all__ = [
    'load_jsonl_data',
    'analyze_hashtags',
    'calculate_engagement_metrics',
    'identify_cultural_moments',
    'competitive_analysis',
    'generate_intelligence_report'
]
