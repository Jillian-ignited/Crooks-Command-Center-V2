import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any

def _safe_json_loads(line: str):
    try:
        return json.loads(line)
    except Exception:
        # Try to recover by stripping BOMs or invalid trailing commas
        try:
            cleaned = line.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            return json.loads(cleaned)
        except Exception:
            return None

def load_jsonl_data(file_path: str) -> List[Dict[str, Any]]:
    """Load and parse JSONL files from Instagram/TikTok scrapers"""
    rows = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = _safe_json_loads(line)
            if obj is not None and isinstance(obj, dict):
                rows.append(obj)
    return rows

def analyze_hashtags(posts: List[Dict[str, Any]]):
    """Extract and analyze hashtag trends"""
    counter = Counter()
    for p in posts:
        tags = p.get('hashtags') or []
        if isinstance(tags, str):
            # Some scrapers return a space-delimited string
            tags = [t.strip() for t in tags.split() if t.strip().startswith('#')]
        for t in tags:
            tag = t.lower().lstrip('#')
            if tag:
                counter[tag] += 1

    # Cultural categories (very simple keyword mapping for now)
    categories = {
        'hip-hop': {'hiphop', 'rap', 'boom bap', 'trap', 'hip-hop', 'hiphopculture'},
        'streetwear': {'streetwear', 'ootd', 'sneakers', 'hypebeast', 'kicks'},
        'heritage': {'archive', 'y2k', 'throwback', 'retro', 'legacy', 'heritage'}
    }

    tagged = []
    for tag, count in counter.most_common():
        label = []
        for cat, keys in categories.items():
            if any(k in tag for k in keys):
                label.append(cat)
        tagged.append({'hashtag': tag, 'count': count, 'categories': label})

    return tagged

def calculate_engagement_metrics(posts: List[Dict[str, Any]]):
    """Calculate comprehensive engagement analytics"""
    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_views = 0
    timestamps = []

    for p in posts:
        # IG fields
        total_likes += int(p.get('likesCount') or 0)
        total_comments += int(p.get('commentsCount') or 0)
        # TikTok fields
        total_shares += int(p.get('shareCount') or 0)
        total_views += int(p.get('viewCount') or 0)

        ts = p.get('timestamp')
        if ts:
            try:
                timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
            except Exception:
                pass

    count = len(posts) if posts else 1
    avg_engagement = (total_likes + total_comments + total_shares) / count

    # Trend by day
    by_day = defaultdict(lambda: {'likes':0, 'comments':0, 'shares':0, 'views':0, 'count':0})
    for p in posts:
        ts = p.get('timestamp')
        day_key = None
        if ts:
            try:
                day_key = datetime.fromisoformat(ts.replace('Z', '+00:00')).date().isoformat()
            except Exception:
                day_key = 'unknown'
        else:
            day_key = 'unknown'

        by_day[day_key]['likes'] += int(p.get('likesCount') or 0)
        by_day[day_key]['comments'] += int(p.get('commentsCount') or 0)
        by_day[day_key]['shares'] += int(p.get('shareCount') or 0)
        by_day[day_key]['views'] += int(p.get('viewCount') or 0)
        by_day[day_key]['count'] += 1

    trend = []
    for day, vals in sorted(by_day.items()):
        trend.append({
            'day': day,
            'avg_engagement': (vals['likes']+vals['comments']+vals['shares'])/max(1, vals['count']),
            'avg_views': vals['views']/max(1, vals['count']),
            'posts': vals['count']
        })

    total_posts = len(posts)
    engagement_rate = 0.0
    if total_views > 0:
        engagement_rate = round((total_likes + total_comments + total_shares) / total_views * 100.0, 2)

    return {
        'totals': {
            'likes': total_likes,
            'comments': total_comments,
            'shares': total_shares,
            'views': total_views,
            'posts': total_posts
        },
        'averages': {
            'engagement_per_post': round(avg_engagement, 2)
        },
        'engagement_rate_percent': engagement_rate,
        'trend': trend
    }

def identify_cultural_moments(posts: List[Dict[str, Any]]):
    """Detect cultural events and trends from social data"""
    moments = []
    keywords = [
        ('Hispanic Heritage', ['hispanic', 'latino', 'latin', 'latinx', 'mexico']),
        ('Hip-Hop Anniversary', ['hiphop', 'hip-hop', 'rap', 'biggie', 'tupac', 'wu-tang']),
        ('Streetwear Heritage', ['archive', 'throwback', 'y2k', 'heritage']),
    ]

    for p in posts:
        text = (p.get('caption') or '') + ' ' + (p.get('description') or '')
        text_l = text.lower()
        hit = []
        for label, keys in keywords:
            if any(k in text_l for k in keys):
                hit.append(label)
        if hit:
            moments.append({
                'timestamp': p.get('timestamp'),
                'url': p.get('url'),
                'labels': list(set(hit)),
                'summary': text.strip()[:160]
            })
    return moments

def competitive_analysis(data: Dict[str, Any]):
    """Analyze competitive positioning"""
    posts = data.get('all_posts', [])
    brand_mentions = Counter()
    competitors = ['supreme', 'bape', 'kith', 'palace', 'fear of god', 'off-white', 'purple brand']

    for p in posts:
        text = (p.get('caption') or '') + ' ' + (p.get('description') or '')
        tl = text.lower()
        for c in competitors:
            if c in tl:
                brand_mentions[c] += 1

    # Very lightweight comp metric
    comp = [{'brand': b.title(), 'mentions': n} for b, n in brand_mentions.most_common()]
    return {'brand_mentions': comp, 'notes': 'Mentions detected in captions/descriptions only.'}

def generate_intelligence_report(data: Dict[str, Any]):
    """Create formatted intelligence reports"""
    # Data should include metrics, hashtags, cultural moments, competition
    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'summary': {
            'posts': len(data.get('all_posts', [])),
            'engagement_rate_percent': data.get('engagement', {}).get('engagement_rate_percent', 0.0)
        },
        'top_hashtags': data.get('hashtags', [])[:20],
        'cultural_moments': data.get('cultural_moments', [])[:20],
        'competitive': data.get('competitive', {}),
        'recommendations': [
            'Post more around identified cultural moments in the next 7–14 days.',
            'Repurpose high-engagement formats across IG Reels and TikTok.',
            'Align assets to calendar events with gaps flagged below 72 hours in advance.'
        ]
    }
    return report
